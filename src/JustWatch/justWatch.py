# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
import os
import re
import traceback

from Components.config import config
from twisted.internet import reactor, threads

try:
    from simplejustwatchapi import details, episodes, popular, providers, search, seasons
except Exception as import_error:  # pragma: no cover
    details = episodes = popular = providers = search = seasons = None
    SIMPLEJW_IMPORT_ERROR = import_error
else:
    SIMPLEJW_IMPORT_ERROR = None


HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0.1)'}
ICON_URL = 'https://images.justwatch.com'
WATCHLIST = '/etc/enigma2/justWatch/justWatch.json'
DEBUG_LOG = '/tmp/justwatch-debug.log'


def debug_log(message):
    try:
        with open(DEBUG_LOG, 'a', encoding='utf-8') as handle:
            handle.write('%s %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(message)))
    except Exception:
        pass


def log_exception(prefix):
    debug_log('%s\n%s' % (prefix, traceback.format_exc()))


def jw_debug(message):
    debug_log(message)


COUNTRY_CODE = {
    'COP': '$', 'USD': 'US$', 'AUD': 'A$', 'TWD': 'NT$', 'IDR': 'Rp.', 'KRW': '₩', 'BGN': 'Lw',
    'TRY': 'TL, ₺; ', 'ARS': 'arg$', 'GBP': '£', 'NZD': 'NZ$', 'THB': '฿', 'EUR': '€', 'MXN': 'mex$',
    'HUF': 'Ft', 'VND': '₫, D', 'RON': 'L', 'NOK': 'nkr', 'RUB': '₽', 'ZAR': 'R', 'MYR': 'MS',
    'INR': 'iR, ₹', 'DKK': 'dkr', 'JPY': '¥', 'CZK': 'Kč', 'BRL': 'R$', 'CAD': 'kan$', 'PLN': 'zł',
    'PHP': '₱', 'SEK': 'Skr', 'SGD': 'S$', 'HKD': 'HK$'
}


COUNTRY_LANGUAGE_MAP = {
    "AR": "es", "AT": "de", "AU": "en", "BE": "nl", "BG": "bg", "BR": "pt", "CA": "en",
    "CH": "de", "CL": "es", "CO": "es", "CZ": "cs", "DE": "de", "DK": "da", "EC": "es",
    "EE": "et", "ES": "es", "FI": "fi", "FR": "fr", "GB": "en", "GR": "el", "HK": "zh",
    "HU": "hu", "ID": "id", "IE": "en", "IN": "hi", "IT": "it", "JP": "ja", "KR": "ko",
    "LT": "lt", "LV": "lv", "MX": "es", "MY": "ms", "NL": "nl", "NO": "no", "NZ": "en",
    "PE": "es", "PH": "en", "PL": "pl", "PT": "pt", "RO": "ro", "SE": "sv", "SG": "en",
    "TH": "th", "TR": "tr", "US": "en", "VE": "es", "ZA": "en"
}

COUNTRY_LABELS = {
    "AR": "Argentina", "AT": "Austria", "AU": "Australia", "BE": "Belgium", "BG": "Bulgaria",
    "BR": "Brazil", "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "CO": "Colombia",
    "CZ": "Czech Republic", "DE": "Germany", "DK": "Denmark", "EC": "Ecuador", "EE": "Estonia",
    "ES": "Spain", "FI": "Finland", "FR": "France", "GB": "United Kingdom", "GR": "Greece",
    "HK": "Hong Kong", "HU": "Hungary", "ID": "Indonesia", "IE": "Ireland", "IN": "India",
    "IT": "Italy", "JP": "Japan", "KR": "South Korea", "LT": "Lithuania", "LV": "Latvia",
    "MX": "Mexico", "MY": "Malaysia", "NL": "Netherlands", "NO": "Norway", "NZ": "New Zealand",
    "PE": "Peru", "PH": "Philippines", "PL": "Poland", "PT": "Portugal", "RO": "Romania",
    "SE": "Sweden", "SG": "Singapore", "TH": "Thailand", "TR": "Turkey", "US": "United States",
    "VE": "Venezuela", "ZA": "South Africa"
}

GENRE_LABELS = {
    'act': 'Action & Adventure', 'ani': 'Animation', 'cmy': 'Comedy', 'crm': 'Crime', 'doc': 'Documentary',
    'drm': 'Drama', 'fml': 'Family', 'fnt': 'Fantasy', 'hst': 'History', 'hrr': 'Horror', 'msc': 'Music',
    'rly': 'Reality TV', 'rma': 'Romance', 'scf': 'Science-Fiction', 'spt': 'Sport', 'thr': 'Thriller',
    'war': 'War', 'wsn': 'Western', 'eur': 'Made in Europe', 'kids': 'Kids', 'spt': 'Sport'
}


def _ensure_backend():
    if SIMPLEJW_IMPORT_ERROR is not None:
        debug_log('simplejustwatchapi import failed: %s' % SIMPLEJW_IMPORT_ERROR)
        raise RuntimeError('simplejustwatchapi import failed: %s' % SIMPLEJW_IMPORT_ERROR)


def _locale_parts():
    locale = getattr(config.justwatch.locale, 'value', 'de_DE') or 'de_DE'
    if '_' in locale:
        language, country = locale.split('_', 1)
    elif '-' in locale:
        language, country = locale.split('-', 1)
    else:
        language = locale[:2] or 'de'
        country = getattr(config.justwatch.country, 'value', 'DE') or 'DE'
    return language.lower(), country.upper()


def _call_callback(callback, *args):
    debug_log('_call_callback callback=%s args_types=%s' % (getattr(callback, '__name__', repr(callback)), [type(a).__name__ for a in args]))
    if callback:
        reactor.callFromThread(callback, *args)


def _provider_filter():
    value = getattr(config.justwatch.providers, 'value', '') or ''
    providers_value = [item.strip() for item in value.split(',') if item.strip()]
    return providers_value or None


def _full_image_url(url):
    if not url:
        return None
    if url.startswith('http://') or url.startswith('https://'):
        return url
    return ICON_URL + url


def _normalize_object_type(value):
    value = (value or '').lower()
    if value in ('show', 'shows', 'series'):
        return 'show'
    return 'movie'


def _offer_to_dict(offer):
    package = getattr(offer, 'package', None)
    package_id = getattr(package, 'package_id', None)
    if package_id is None:
        package_id = getattr(package, 'id', None)
    return {
        'id': getattr(offer, 'id', None),
        'provider_id': package_id,
        'monetization_type': (getattr(offer, 'monetization_type', '') or '').lower(),
        'presentation_type': (getattr(offer, 'presentation_type', '') or '').lower(),
        'currency': getattr(offer, 'price_currency', None),
        'retail_price': getattr(offer, 'price_value', None),
        'urls': {'standard_web': getattr(offer, 'url', None)},
        'element_count': getattr(offer, 'element_count', None),
        'last_change_retail_price_value': getattr(offer, 'last_change_retail_price_value', None),
        'available_to': getattr(offer, 'available_to', None),
        'type': getattr(offer, 'type', None),
        'deeplink_roku': getattr(offer, 'deeplink_roku', None),
        'subtitle_languages': getattr(offer, 'subtitle_languages', []) or [],
        'video_technology': getattr(offer, 'video_technology', []) or [],
        'audio_technology': getattr(offer, 'audio_technology', []) or [],
        'audio_languages': getattr(offer, 'audio_languages', []) or [],
    }


def _entry_to_legacy_dict(entry, include_seasons=False, include_episodes=False):
    object_type = _normalize_object_type(getattr(entry, 'object_type', ''))
    scoring = getattr(entry, 'scoring', None)
    interactions = getattr(entry, 'interactions', None)
    charts = getattr(entry, 'streaming_charts', None)
    data = {
        'id': getattr(entry, 'object_id', None),
        'node_id': getattr(entry, 'entry_id', None),
        'object_type': object_type,
        'jw_entity_id': getattr(entry, 'entry_id', None),
        'title': getattr(entry, 'title', '') or '',
        'full_path': getattr(entry, 'url', None),
        'full_path_deeplink': getattr(entry, 'url', None),
        'poster': getattr(entry, 'poster', None),
        'backdrops': [{'backdrop_url': url} for url in (getattr(entry, 'backdrops', None) or [])],
        'short_description': getattr(entry, 'short_description', None),
        'original_release_year': getattr(entry, 'release_year', None),
        'runtime': getattr(entry, 'runtime_minutes', None),
        'genre_ids': list(getattr(entry, 'genres', None) or []),
        'age_certification': getattr(entry, 'age_certification', None),
        'offers': [_offer_to_dict(offer) for offer in (getattr(entry, 'offers', None) or [])],
        'scoring': {
            'imdb_score': getattr(scoring, 'imdb_score', None) if scoring else None,
            'imdb_votes': getattr(scoring, 'imdb_votes', None) if scoring else None,
            'tmdb_popularity': getattr(scoring, 'tmdb_popularity', None) if scoring else None,
            'tmdb_score': getattr(scoring, 'tmdb_score', None) if scoring else None,
            'tomatometer': getattr(scoring, 'tomatometer', None) if scoring else None,
            'certified_fresh': getattr(scoring, 'certified_fresh', None) if scoring else None,
            'jw_rating': getattr(scoring, 'jw_rating', None) if scoring else None,
        },
        'interactions': {
            'likes': getattr(interactions, 'likes', None) if interactions else None,
            'dislikes': getattr(interactions, 'dislikes', None) if interactions else None,
        },
        'streaming_charts': {
            'rank': getattr(charts, 'rank', None) if charts else None,
            'trend': getattr(charts, 'trend', None) if charts else None,
            'trend_difference': getattr(charts, 'trend_difference', None) if charts else None,
            'top_rank': getattr(charts, 'top_rank', None) if charts else None,
            'days_in_top_3': getattr(charts, 'days_in_top_3', None) if charts else None,
            'days_in_top_10': getattr(charts, 'days_in_top_10', None) if charts else None,
            'days_in_top_100': getattr(charts, 'days_in_top_100', None) if charts else None,
            'days_in_top_1000': getattr(charts, 'days_in_top_1000', None) if charts else None,
            'updated': getattr(charts, 'updated', None) if charts else None,
        },
        'imdb_id': getattr(entry, 'imdb_id', None),
        'tmdb_id': getattr(entry, 'tmdb_id', None),
        'credits': [],
        'clips': [],
    }
    if include_seasons:
        data['seasons'] = []
    if include_episodes:
        data['episodes'] = []
    return data


def _season_to_legacy_dict(entry):
    data = _entry_to_legacy_dict(entry)
    data.update({
        'season_number': getattr(entry, 'season_number', None),
        'episode_count': getattr(entry, 'total_episode_count', None),
    })
    return data


def _episode_to_legacy_dict(episode):
    return {
        'id': getattr(episode, 'object_id', None),
        'node_id': getattr(episode, 'episode_id', None),
        'object_type': 'show_episode',
        'title': getattr(episode, 'title', None),
        'short_description': getattr(episode, 'short_description', None),
        'runtime': getattr(episode, 'runtime_minutes', None),
        'episode_number': getattr(episode, 'episode_number', None),
        'season_number': getattr(episode, 'season_number', None),
        'offers': [_offer_to_dict(offer) for offer in (getattr(episode, 'offers', None) or [])],
        'original_release_year': getattr(episode, 'release_year', None),
        'original_release_date': getattr(episode, 'release_date', None),
    }


def get_locale():
    language, country = _locale_parts()
    country_dir = os.path.join(os.path.dirname(__file__), 'images', 'country')
    result = []
    seen = set()
    try:
        codes = sorted([os.path.splitext(name)[0].upper() for name in os.listdir(country_dir) if name.lower().endswith('.png')])
    except Exception:
        codes = []

    for iso in codes:
        lang = COUNTRY_LANGUAGE_MAP.get(iso, iso.lower())
        full_locale = '%s_%s' % (lang, iso)
        result.append({
            'country': COUNTRY_LABELS.get(iso, iso),
            'iso_3166_2': iso,
            'full_locale': full_locale,
            'language': lang,
        })
        seen.add(iso)

    if country not in seen:
        result.insert(0, {
            'country': COUNTRY_LABELS.get(country, country),
            'iso_3166_2': country,
            'full_locale': '%s_%s' % (language, country),
            'language': language,
        })

    return result


def search_for_item(callback, query, page, content_types, genres, century, age, person_id):
    if isinstance(query, bytes):
        try:
            query = query.decode('utf-8', 'ignore')
        except Exception:
            query = ''
    if isinstance(content_types, bytes):
        try:
            content_types = content_types.decode('utf-8', 'ignore')
        except Exception:
            content_types = 'All'
    debug_log('search_for_item query=%r page=%r content_types=%r genres=%r century=%r age=%r person_id=%r' % (query, page, content_types, genres, century, age, person_id))
    _ensure_backend()
    language, country = _locale_parts()
    page = max(1, int(page or 1))
    offset = (page - 1) * 100
    provider_codes = _provider_filter()

    title = query or ''
    if title:
        entries = search(title, country, language, 100, True, offset, provider_codes)
    else:
        entries = popular(country, language, 100, True, offset, provider_codes)

    items = []
    wanted_type = None
    if content_types == 'Series':
        wanted_type = 'show'
    elif content_types == 'Movies':
        wanted_type = 'movie'

    wanted_genres = set(genres or [])
    wanted_age = set(age or [])
    wanted_year = int(century) if century else None

    for entry in entries:
        data = _entry_to_legacy_dict(entry)
        if wanted_type and data.get('object_type') != wanted_type:
            continue
        if wanted_genres and not wanted_genres.intersection(set(data.get('genre_ids') or [])):
            continue
        if wanted_age and (data.get('age_certification') not in wanted_age):
            continue
        if wanted_year and data.get('original_release_year') != wanted_year:
            continue
        items.append(data)

    videos = {
        'page': page,
        'page_size': 100,
        'total_pages': 1,
        'total_results': len(items),
        'items': items,
        'person_id_unsupported': bool(person_id),
    }
    debug_log('search_for_item result items=%s total_results=%s total_pages=%s' % (len(items), videos.get('total_results'), videos.get('total_pages')))
    _call_callback(callback, videos)
    return videos


def get_search_for_item(callback=None, query=None, page=None, content_types=None, genres=None, century=None, age=None, person_id=None):
    d = threads.deferToThread(search_for_item, callback, query, page, content_types, genres, century, age, person_id)
    d.addErrback(lambda failure: (debug_log('get_search_for_item errback %s' % failure), failure))
    return d


def get_providers():
    debug_log('get_providers start')
    _ensure_backend()
    _, country = _locale_parts()
    result = []
    for provider in providers(country):
        provider_id = getattr(provider, 'package_id', None)
        if provider_id is None:
            provider_id = getattr(provider, 'id', None)
        result.append({
            'id': provider_id,
            'package_id': getattr(provider, 'package_id', None),
            'name': getattr(provider, 'name', None),
            'clear_name': getattr(provider, 'name', None),
            'technical_name': getattr(provider, 'technical_name', None),
            'short_name': getattr(provider, 'short_name', None),
            'icon_url': getattr(provider, 'icon', None),
        })
    debug_log('get_providers loaded=%s' % len(result))
    return result


def get_provider_over_id(data, provider_id):
    provider = {}
    for item in data:
        if item.get('id') == provider_id or item.get('package_id') == provider_id:
            provider = item
            break
    return provider


def get_currency(item, currency):
    find = COUNTRY_CODE.get(currency)
    if find:
        item = item + find
    return item


def get_genre_over_ids(data):
    return [GENRE_LABELS.get(item, item) for item in (data or [])]


def get_genres():
    items = []
    for genre_id, label in sorted(GENRE_LABELS.items(), key=lambda kv: kv[1].lower()):
        items.append({'id': genre_id, 'translation': label})
    return items


def _normalize_backend_node_id(entity_id, content_type=None, season=False):
    if entity_id is None:
        return None
    if isinstance(entity_id, bytes):
        try:
            entity_id = entity_id.decode("utf-8")
        except Exception:
            entity_id = entity_id.decode("latin-1", "ignore")
    if not isinstance(entity_id, str):
        entity_id = str(entity_id)
    entity_id = entity_id.strip()
    if not entity_id:
        return entity_id
    if ':' in entity_id:
        return entity_id
    lowered = entity_id.lower()
    # simplejustwatchapi search/details commonly use short graph ids like ts81342 / tm123 / ss42 / es9
    if lowered.startswith(("ts", "tm", "ss", "es", "ep")):
        return entity_id
    if season:
        return 'SHOW_SEASON:%s' % entity_id
    node_prefix = 'SHOW' if content_type == 'show' else 'MOVIE'
    return '%s:%s' % (node_prefix, entity_id)


def got_title(callback, title_id, content_type):
    try:
        debug_log("got_title start title_id=%r content_type=%r" % (title_id, content_type))
        _ensure_backend()
        language, country = _locale_parts()
        node_id = _normalize_backend_node_id(title_id, content_type=content_type)
        debug_log('got_title details node_id=%s country=%s language=%s' % (node_id, country, language))
        entry = details(node_id, country, language, True)
        debug_log('got_title details returned type=%s value=%r' % (type(entry).__name__, entry))
        if entry is None:
            data = {}
        else:
            data = _entry_to_legacy_dict(entry)
            debug_log('got_title mapped keys=%s offers=%s backdrops=%s' % (sorted(data.keys()), len(data.get('offers') or []), len(data.get('backdrops') or [])))
            if content_type == 'show':
                season_entries = seasons(node_id, country, language, True) or []
                debug_log('got_title seasons returned count=%s' % len(season_entries))
                data['seasons'] = [_season_to_legacy_dict(item) for item in season_entries]
        _call_callback(callback, data)
    except Exception:
        log_exception('got_title failed title_id=%r content_type=%r' % (title_id, content_type))
        _call_callback(callback, {})


def get_title(title_id, content_type='movie', callback=None):
    debug_log('get_title schedule title_id=%r content_type=%r callback=%s' % (title_id, content_type, getattr(callback, '__name__', repr(callback))))
    d = threads.deferToThread(got_title, callback, title_id, content_type)
    d.addErrback(lambda failure: (debug_log('get_title errback %s' % failure), failure))
    return d


def got_season(callback, season_id):
    try:
        debug_log('got_season start season_id=%r' % (season_id,))
        _ensure_backend()
        language, country = _locale_parts()
        node_id = _normalize_backend_node_id(season_id, season=True)
        entry = details(node_id, country, language, True)
        episode_entries = episodes(node_id, country, language, True) or []
        debug_log('got_season details_type=%s episodes=%s' % (type(entry).__name__, len(episode_entries)))
        if entry is None:
            data = {'episodes': []}
        else:
            data = _entry_to_legacy_dict(entry, include_episodes=True)
            data['show_title'] = data.get('title')
            data['original_title'] = None
            data['episodes'] = [_episode_to_legacy_dict(item) for item in episode_entries]
        _call_callback(callback, data)
    except Exception:
        log_exception('got_season failed season_id=%r' % (season_id,))
        _call_callback(callback, {'episodes': []})


def get_season(callback, season_id):
    debug_log('get_season schedule season_id=%r callback=%s' % (season_id, getattr(callback, '__name__', repr(callback))))
    d = threads.deferToThread(got_season, callback, season_id)
    d.addErrback(lambda failure: (debug_log('get_season errback %s' % failure), failure))
    return d


def get_cinema_times(title_id, content_type='movie'):
    return []


def get_cinema_details():
    return []


def get_upcoming_cinema(weeks_offset, nationwide_cinema_releases_only=True):
    return {'page': 0, 'page_size': 0, 'total_pages': 1, 'total_results': 0, 'items': []}


def get_certifications(content_type='movie'):
    """Return basic German FSK ratings list for filtering.

    simplejustwatchapi does not expose a certifications endpoint, but the backend
    returns age_certification values like '0', '6', '12', '16', '18'.
    """
    certs = [
        {'organization': '', 'technical_name': '__all__', 'order': -1, 'title': 'All'},
        {'organization': 'FSK', 'technical_name': '0', 'order': 0},
        {'organization': 'FSK', 'technical_name': '6', 'order': 1},
        {'organization': 'FSK', 'technical_name': '12', 'order': 2},
        {'organization': 'FSK', 'technical_name': '16', 'order': 3},
        {'organization': 'FSK', 'technical_name': '18', 'order': 4},
    ]
    return certs


def got_person_detail(callback, person_id):
    data = ('', '', '', {'page': 1, 'page_size': 100, 'total_pages': 1, 'total_results': 0, 'items': []})
    _call_callback(callback, data)


def get_person_detail(callback, person_id):
    threads.deferToThread(got_person_detail, callback, person_id)


def get_century(data):
    """Return year filter list up to the current year (inclusive)."""
    try:
        selected = int(data) if data is not None and str(data).strip() else None
    except Exception:
        selected = None

    start_year = 1900
    end_year = datetime.now().year

    century_data = [("All", "__all__", selected is None)]
    for year in range(end_year, start_year - 1, -1):
        select = True if selected is not None and year == selected else False
        century_data.append((str(year), year, select))

    return century_data


def get_poster_url(url, size='small'):
    return _full_image_url(url)


def get_backdrop_url(url):
    return _full_image_url(url)


def get_provider_icon_url(url):
    return _full_image_url(url)


def _download_file_worker(url, destination):
    import requests
    if not url or not destination:
        return False
    parent = os.path.dirname(destination)
    if parent and not os.path.isdir(parent):
        os.makedirs(parent, exist_ok=True)
    response = requests.get(url, headers=HEADER, timeout=20, stream=True)
    response.raise_for_status()
    with open(destination, 'wb') as handle:
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                handle.write(chunk)
    return True


def download_file(url, destination, callback=None):
    debug_log('download_file url=%r destination=%r callback=%s' % (url, destination, getattr(callback, '__name__', repr(callback))))
    d = threads.deferToThread(_download_file_worker, url, destination)

    def _done(result):
        if callback:
            reactor.callFromThread(callback)
        return result

    def _err(failure):
        print('[JustWatch] download_file failed: %s -> %s (%s)' % (url, destination, failure))
        if callback:
            reactor.callFromThread(callback)
        return failure

    d.addCallbacks(_done, _err)
    return d


def got_free_flash(callback):
    try:
        flash_info = None
        fd = os.popen('df -m %s | tail -n1' % config.justwatch.cache_destination.value)
        for line in fd.readlines():
            items = line.split()
            if len(items) > 5:
                flash_info = items[3]
                break
        fd.close()
        free_flash = int(flash_info) if flash_info else None
    except Exception:
        free_flash = None
    _call_callback(callback, free_flash)


def get_free_flash(callback):
    threads.deferToThread(got_free_flash, callback)


def get_provider_title_id(technical_name, url):
    title_id = None
    if 'amazon' in technical_name and url:
        title_id = re.findall(r'ASIN=(.*?)&', url, re.S)[0] if re.findall(r'ASIN=(.*?)&', url, re.S) else None
        if not title_id:
            title_id = re.findall(r'https://www.primevideo.com/detail/(.*?)\?.*?', url, re.S)[0] if re.findall(r'https://www.primevideo.com/detail/(.*?)\?.*?', url, re.S) else None
    elif 'netflix' in technical_name and url:
        title_id = re.findall(r'title/(\d+)', url, re.S)[0] if re.findall(r'title/(\d+)', url, re.S) else None
    elif 'daserstemediathek' in technical_name and url:
        title_id = url.split('/')[-1] if url.split('/') else None
    elif 'disneyplus' in technical_name and url:
        title_id = url.split('/')[-1] if url.split('/') else None
    return title_id


def get_watchlist():
    data = {'items': []}
    if os.path.isfile(WATCHLIST):
        with open(WATCHLIST, 'r') as data_watchlist:
            data = json.load(data_watchlist)
    else:
        save_data(data)
    return data


def get_watchlistIds(object_type='movie'):
    ids_movie = []
    ids_show = []
    data = get_watchlist()
    items = data.get('items') or []
    for item in items:
        if item.get('object_type') == 'movie':
            ids_movie.append(item.get('id'))
        elif item.get('object_type') == 'show':
            ids_show.append(item.get('id'))
    return ids_movie if object_type == 'movie' else ids_show


def add_item_watchlist(item, object_type='movie'):
    data = get_watchlist()
    items = data.get('items') or []
    add_item = {
        'title': item.get('title'),
        'id': item.get('id'),
        'object_type': object_type,
        'poster': item.get('poster'),
    }
    if items:
        is_find = False
        for find in items:
            if find.get('id') == item.get('id') and object_type == find.get('object_type'):
                is_find = True
                break
        if not is_find:
            items.append(add_item)
    else:
        items.append(add_item)
    save_data({'items': items})


def remove_item_watchlist(item, object_type='movie'):
    data = get_watchlist()
    items = data.get('items') or []
    items_new = []
    for find in items:
        if find.get('id') != item.get('id') or object_type != find.get('object_type'):
            items_new.append(find)
    save_data({'items': items_new})


def save_data(data):
    with open(WATCHLIST, 'w') as outfile:
        json.dump(data, outfile)
