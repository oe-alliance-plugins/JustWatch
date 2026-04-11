from Screens.Screen import Screen
import os

from Components.AVSwitch import AVSwitch
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.Renderer.JustWatchVRunningText import JustWatchVRunningText
from Components.config import config, configfile
from Screens.InfoBar import MoviePlayer
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
from enigma import ePicLoad, gFont, eServiceReference, gPixmapPtr, \
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_WRAP, eTimer
from twisted.web.client import downloadPage

from .justWatch import *
from .just_watch_spinner import JustWatchSpinner
from .just_watch_episodes import JustWatchEpisodesScreen
from .just_watch_actor_search import JustWatchPersonSearchScreen
from .yt_url import get_play_url
from .__init__ import _


DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    BACKDROP_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_select_30x30.png"
    BACKDROP_NO_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_no_select_30x30.png"
    BACKGROUND_CONTENT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_596x50.png"
    CONTENT_WATCHLIST_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_250x50.png"
    CONTENT_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_select_100x50.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_110x110.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_100x100.png"

else:
    skinFactor = 1.5
    BACKDROP_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_select_20x20.png"
    BACKDROP_NO_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_no_select_20x20.png"
    BACKGROUND_CONTENT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_397x33.png"
    CONTENT_WATCHLIST_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_166x33.png"
    CONTENT_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_select_66x33.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_73x73.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_66x66.png"


NO_OFFERS_STR = _("There are currently no offers.")


def _normalize_offer_quality(value):
    value = (value or "").strip().lower()
    if value in ("_4k", "4k", "uhd"):
        return "4K"
    if value in ("hd", "fhd", "fullhd"):
        return "HD"
    return "SD"


def _first_nonempty_quality(content_stream_list, fallback="HD"):
    for quality in ("HD", "4K", "SD"):
        quality_data = content_stream_list.get(quality, {}) if isinstance(content_stream_list, dict) else {}
        if any(quality_data.get(k) for k in ("flatrate", "rent", "buy")):
            return quality
    return fallback if fallback in (content_stream_list or {}) else next(iter(content_stream_list or {"HD": {}}))


ACTOR_STR = _("Actors:")
TRAILER_STR = _("Trailer:")
TRAILER_ERROR_STR = _("No trailer was found!")
SEASON_STR = _(" Season")
SEASONS_STR = _(" Seasons")
DESCRIPTION_STR = _("Unfortunately no description available at the moment.")

WATCHLIST_STR = _("Watchlist")
ADD_WATCHLIST_STR = _("Add to Watchlist")
REMOVE_WATCHLIST_STR = _("Delete from Watchlist")
WATCHLIST_ERROR_STR = _("Watchlist mode error!\nCheck login")

ADD_WATCHLIST_INFO_STR = _("Your selection has been added to the watchlist")
REMOVE_WATCHLIST_INFO_STR = _("Your selection has been deleted from the watchlist")


class JustWatchSeriesScreen(Screen, JustWatchSpinner):
    def __init__(self, session, data, providers, amazon, netflix, disney):
        if DESKTOPSIZE.width() >= 1920:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatchSeriesScreen" position="center,center" size="1920,1080" title="JustWatch">
                           <!-- Gui 1 -->
                           <widget name="JustWatchBackdrop" position="40,10" size="1840,600" backgroundColor="#001b1e25" zPosition="1" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchTitleText" position="40,620" size="1840,50" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00ffffff" zPosition="1" font="JW; 38" valign="center" halign="left"/>
                           <widget name="JustWatchGenresText" position="40,680" size="1840,40" backgroundColor="#001b1e25" transparent="1" foregroundColor="#008a8876" zPosition="1" font="JW; 30" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="JustWatchDescriptionText" position="40,725" size="1840,330" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 30" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="JustWatchDown" position="1836,1055" size="44,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/down_44x25.png" zPosition="1" />
                           <!-- Gui 2 -->
                           <widget name="JustWatchCover" position="40,20" size="422,600" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/transparent_422x600.png" alphatest="blend" zPosition="3" />
                           <widget name="JustWatchContent" position="490,20" size="596,50" backgroundColor="#001b1e25" zPosition="1" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchContentProvider" position="490,80" size="1390,540" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchSeason" position="40,640" size="1840,400" backgroundColor="#001a2632" zPosition="2" transparent="0" enableWrapAround="1" />
                           <!-- Gui 3 -->
                           <widget name="JustWatchActors" position="40,10" size="1840,170" backgroundColor="#001a2632" zPosition="2" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchTrailers" position="40,220" size="1840,170" backgroundColor="#001a2632" zPosition="2" transparent="0" enableWrapAround="1" />
                           <!-- Provider Mode -->
                           <widget name="BackgroundProviderModeList" position="560,215" size="800,610" backgroundColor="#00cac253" transparent="0" zPosition="7" />
                           <widget name="JustWatchProviderModeList" position="565,220" size="790,600" foregroundColor="#00ffffff" backgroundColor="#001a2632" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" zPosition="8" transparent="0" enableWrapAround="1" />
                           <!-- Spinner -->
                           <widget name="BackgroundSpinner" position="460,370" size="1000,42" backgroundColor="#001b1e25" transparent="0" zPosition="98" />
                           <widget name="JustWatchSpinner" position="925,640" size="70,70" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/spinner/1.png" alphatest="blend" zPosition="99" />
                           </screen>
                        """
        else:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatchSeriesScreen" position="center,center" size="1280,720" title="JustWatch">
                           <!-- Gui 1 -->
                           <widget name="JustWatchBackdrop" position="26,6" size="1226,400" backgroundColor="#001b1e25" zPosition="1" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchTitleText" position="26,413" size="1226,33" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00ffffff" zPosition="1" font="JW; 25" valign="center" halign="left"/>
                           <widget name="JustWatchGenresText" position="26,453" size="1226,26" backgroundColor="#001b1e25" transparent="1" foregroundColor="#008a8876" zPosition="1" font="JW; 20" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="JustWatchDescriptionText" position="26,483" size="1226,220" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 20" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="JustWatchDown" position="1224,703" size="29,16" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/down_29x16.png" zPosition="1" />
                           <!-- Gui 2 -->
                           <widget name="JustWatchCover" position="26,13" size="281,400" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/transparent_281x400.png" alphatest="blend" zPosition="3" />
                           <widget name="JustWatchContent" position="326,13" size="397,33" backgroundColor="#001b1e25" zPosition="1" transparent="1" enableWrapAround="1" /><widget name="JustWatchContentProvider" position="326,53" size="926,360" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchContentProvider" position="326,53" size="926,360" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchSeason" position="26,426" size="1226,266" backgroundColor="#001a2632" zPosition="2" transparent="0" enableWrapAround="1" />
                           <!-- Gui 3 -->
                           <widget name="JustWatchActors" position="26,6" size="1226,113" backgroundColor="#001a2632" zPosition="2" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchTrailers" position="26,146" size="1226,113" backgroundColor="#001a2632" zPosition="2" transparent="0" enableWrapAround="1" />
                           <!-- Provider Mode -->
                           <widget name="BackgroundProviderModeList" position="373,143" size="533,406" backgroundColor="#00cac253" transparent="0" zPosition="7" />
                           <widget name="JustWatchProviderModeList" position="376,146" size="526,400" foregroundColor="#00ffffff" backgroundColor="#001a2632" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" zPosition="8" transparent="0" enableWrapAround="1" />
                           <!-- Spinner -->
                           <widget name="BackgroundSpinner" position="306,246" size="666,28" backgroundColor="#001b1e25" transparent="0" zPosition="98" />
                           <widget name="JustWatchSpinner" position="616,426" size="46,46" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/spinner/1.png" alphatest="blend" zPosition="99" />
                           </screen>
                        """
        Screen.__init__(self, session)

        JustWatchSpinner.__init__(self)

        self['actions'] = NumberActionMap(['JustWatch_Actions'], {'ok': self.keyOk,
                                                                  'cancel': self.keyCancel,
                                                                  'left': self.keyLeft,
                                                                  'right': self.keyRight,
                                                                  'up': self.keyUp,
                                                                  'down': self.keyDown,
                                                                  }, -1)

        self.chooseJustWatchBackdropList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchBackdropList.l.setItemHeight(int(600 / skinFactor))
        self['JustWatchBackdrop'] = self.chooseJustWatchBackdropList

        self.chooseJustWatchContentList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchContentList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchContentList.l.setItemHeight(int(50 / skinFactor))
        self['JustWatchContent'] = self.chooseJustWatchContentList

        self.chooseJustWatchContentProviderList = MenuList([], enableWrapAround=True,
                                                           content=eListboxPythonMultiContent)
        self.chooseJustWatchContentProviderList.l.setFont(0, gFont('JW', int(22 / skinFactor)))
        self.chooseJustWatchContentProviderList.l.setItemHeight(int(540 / skinFactor))
        self['JustWatchContentProvider'] = self.chooseJustWatchContentProviderList

        self.chooseJustWatchActorsList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchActorsList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchActorsList.l.setFont(1, gFont('JW', int(34 / skinFactor)))
        self.chooseJustWatchActorsList.l.setItemHeight(int(170 / skinFactor))
        self['JustWatchActors'] = self.chooseJustWatchActorsList

        self.chooseJustWatchTrailersList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchTrailersList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchTrailersList.l.setFont(1, gFont('JW', int(34 / skinFactor)))
        self.chooseJustWatchTrailersList.l.setItemHeight(int(170 / skinFactor))
        self['JustWatchTrailers'] = self.chooseJustWatchTrailersList

        self.chooseJustWatchSeasonList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchSeasonList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchSeasonList.l.setItemHeight(int(400 / skinFactor))
        self['JustWatchSeason'] = self.chooseJustWatchSeasonList

        self.chooseJustWatchProviderModeList = MenuList([], enableWrapAround=True,
                                                        content=eListboxPythonMultiContent)
        self.chooseJustWatchProviderModeList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchProviderModeList.l.setItemHeight(int(60 / skinFactor))
        self['JustWatchProviderModeList'] = self.chooseJustWatchProviderModeList

        self['JustWatchTitleText'] = Label("")
        self['JustWatchGenresText'] = Label("")
        self['BackgroundProviderModeList'] = Label("")
        self['JustWatchDescriptionText'] = JustWatchVRunningText("")
        self['JustWatchDown'] = Pixmap()

        self['JustWatchCover'] = Pixmap()
        self['JustWatchCover'].hide()
        self['JustWatchContent'].hide()
        self['JustWatchContentProvider'].hide()
        self['JustWatchActors'].hide()
        self['JustWatchTrailers'].hide()
        self['JustWatchSeason'].hide()
        self['BackgroundProviderModeList'].hide()
        self['JustWatchProviderModeList'].hide()

        self.title = ""
        self.description = ""
        self.genres = ""
        self.cover_destination = "%s/%s-poster.jpg" % (config.justwatch.cache_destination.value, str(data.get("id")))
        self.data = data
        self.backdrop_list = []
        self.actors_list = []
        self.trailers_list = []
        self.season_list = []
        self.cover_list = []
        self.download_list = []
        self.providers = providers
        self.content_list = ["SD", "HD", "4K"]
        self.backdrop_list_index = 0
        self.actor_index = 0
        self.trailer_index = 0
        self.season_index = 0
        self.content_list_select = config.justwatch.content_mode.value
        self.content_list_index = self.content_list.index(config.justwatch.content_mode.value)

        self.content_stream_list = {}
        self.content_stream_index = 0

        self.gui_mode = 0
        self.last_gui_mode = 0

        self.amazon = amazon
        self.netflix = netflix
        self.disney = disney

        self.watchlistIds = get_watchlistIds(object_type="show")
        self.is_watchlist = False

        self.CoverTimer = eTimer()
        self.CoverTimerStatus = False
        self.CoverTimer.callback.append(self.reloadCover)

        self.onLayoutFinish.append(self.do_build_backdrop_data)
        self.onLayoutFinish.append(self.show_cover)

    def do_show_gui_mode(self):
        if self.gui_mode == 0:
            self['JustWatchCover'].hide()
            self['JustWatchContent'].hide()
            self['JustWatchContentProvider'].hide()
            self['JustWatchActors'].hide()
            self['JustWatchTrailers'].hide()
            self['JustWatchSeason'].hide()

            self['JustWatchBackdrop'].show()
            self['JustWatchTitleText'].show()
            self['JustWatchGenresText'].show()
            self['JustWatchDescriptionText'].show()
            self['JustWatchDown'].show()
        elif self.gui_mode <= 5:
            self['JustWatchBackdrop'].hide()
            self['JustWatchTitleText'].hide()
            self['JustWatchGenresText'].hide()
            self['JustWatchDescriptionText'].hide()
            self['JustWatchDown'].hide()
            self['JustWatchActors'].hide()
            self['JustWatchTrailers'].hide()

            self.build_content()
            self['JustWatchCover'].show()
            self['JustWatchContent'].show()
            self['JustWatchContentProvider'].show()
            self['JustWatchSeason'].show()
            self['JustWatchDown'].show()
        else:
            self['JustWatchCover'].hide()
            self['JustWatchContent'].hide()
            self['JustWatchContentProvider'].hide()
            self['JustWatchSeason'].hide()
            self['JustWatchDown'].hide()

            self['JustWatchActors'].show()
            self['JustWatchTrailers'].show()

    def do_build_backdrop_data(self):
        jw_debug('%s do_build_backdrop_data start id=%r title=%r backdrops=%s offers=%s' % (self.__class__.__name__, self.data.get('id') if isinstance(self.data, dict) else None, self.data.get('title') if isinstance(self.data, dict) else None, len(self.data.get('backdrops') or []) if isinstance(self.data, dict) else None, len(self.data.get('offers') or []) if isinstance(self.data, dict) else None))
        backdrop = self.data.get("backdrops")
        if backdrop:
            for item in backdrop:
                backdrop_url = item.get("backdrop_url")
                drop_url = get_backdrop_url(backdrop_url) if backdrop_url else None
                drop_id = None
                if backdrop_url:
                    parts = [part for part in backdrop_url.split('/') if part]
                    if len(parts) >= 3:
                        drop_id = '%s-%s-%s' % (
                            parts[-3],
                            parts[-2],
                            parts[-1].replace('.jpg', '').replace('.png', '').replace('.', '_')
                        )
                    elif len(parts) >= 2:
                        drop_id = '%s-%s' % (parts[-2], parts[-1].replace('.jpg', '').replace('.png', '').replace('.', '_'))
                    else:
                        drop_id = backdrop_url.replace('https://', '').replace('http://', '').replace('/', '-').replace('.', '_')
                if drop_id and drop_url:
                    drop_destination = "%s/%s-backdrop.jpg" % (config.justwatch.cache_destination.value, drop_id)
                    self.backdrop_list.append((drop_url, drop_destination))
        self.load_backdrop()
        self.build_gui()
        self.build_actors()
        self.build_trailers()
        self.build_season()

    def build_content(self):
        self.watchlistIds = get_watchlistIds(object_type="show")
        self.is_watchlist = True if self.data.get("id") in self.watchlistIds else False
        watchlist_mode = "- " + WATCHLIST_STR if self.data.get("id") in self.watchlistIds else "+ " + WATCHLIST_STR
        data = [self.content_list_index, self.gui_mode, self.content_list_select, self.content_list, watchlist_mode]
        self.chooseJustWatchContentList.setList(list(map(content_entry, [data])))
        self.chooseJustWatchContentList.selectionEnabled(0)

        data = [self.content_stream_index, self.gui_mode, self.content_list_select, self.content_stream_list]
        self.chooseJustWatchContentProviderList.setList(list(map(content_provider_entry, [data])))
        self.chooseJustWatchContentProviderList.selectionEnabled(0)

    def build_gui(self):
        jw_debug('%s build_gui keys=%s' % (self.__class__.__name__, sorted(self.data.keys()) if isinstance(self.data, dict) else type(self.data).__name__))
        century = " (" + str(self.data.get("original_release_year")) + ")" if self.data.get(
            "original_release_year") else ""
        self.title = self.data.get("title") + century if self.data.get("title") else "" + century
        self.description = self.data.get("short_description") if self.data.get(
            "short_description") else DESCRIPTION_STR
        runtime = "   " + str(self.data.get("runtime")) + " Min." if self.data.get("runtime") else ""
        fsk = "   FSK " + str(self.data.get("age_certification")) if self.data.get("age_certification") else ""
        self.genres = ", ".join(get_genre_over_ids(self.data.get("genre_ids"))) + runtime + fsk if self.data.get("genre_ids") else "" + runtime + fsk

        sd_buy = []
        sd_flatrate = []
        sd_rent = []
        hd_buy = []
        hd_flatrate = []
        hd_rent = []
        uhd_buy = []
        uhd_flatrate = []
        uhd_rent = []
        if self.data.get("offers"):
            for item in self.data.get("offers"):
                monetization_type = item.get("monetization_type") if item.get(
                    "monetization_type") else None
                season_num = str(item.get("element_count")) + SEASON_STR if item.get("element_count") == 1 else str(
                    item.get("element_count")) + SEASONS_STR
                provider = get_provider_over_id(self.providers, item.get("provider_id"))
                technical_name = provider.get("technical_name") if provider.get(
                    "technical_name") else ""
                icon_destination = "%s/provider/%s.jpg" % (config.justwatch.cache_destination.value, technical_name)
                presentation_type = _normalize_offer_quality(item.get("presentation_type"))
                short_name = provider.get("short_name") if provider.get("short_name") else "no_provider"
                url = item.get("urls").get("standard_web")
                title_id = get_provider_title_id(technical_name, url)
                select_all = True if config.justwatch.providers.value == "" else False
                if short_name in config.justwatch.providers.value.split(",") or select_all:
                    if monetization_type == "buy":
                        if presentation_type == "SD":
                            sd_buy.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                        elif presentation_type == "HD":
                            hd_buy.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                        elif presentation_type == "4K":
                            uhd_buy.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                    elif monetization_type == "flatrate":
                        if presentation_type == "SD":
                            sd_flatrate.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                        elif presentation_type == "HD":
                            hd_flatrate.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                        elif presentation_type == "4K":
                            uhd_flatrate.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                    elif monetization_type == "rent":
                        if presentation_type == "SD":
                            sd_rent.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                        elif presentation_type == "HD":
                            hd_rent.append((presentation_type, icon_destination, season_num, technical_name, title_id))
                        elif presentation_type == "4K":
                            uhd_rent.append((presentation_type, icon_destination, season_num, technical_name, title_id))
        self.content_stream_list = {"SD": {"flatrate": sd_flatrate,
                                           "rent": sd_rent,
                                           "buy": sd_buy}}
        self.content_stream_list.update({"HD": {"flatrate": hd_flatrate,
                                                "rent": hd_rent,
                                                "buy": hd_buy}})
        self.content_stream_list.update({"4K": {"flatrate": uhd_flatrate,
                                                "rent": uhd_rent,
                                                "buy": uhd_buy}})

        selected_quality = self.content_list_select if self.content_list_select in self.content_stream_list else None
        if not selected_quality or not any(self.content_stream_list.get(selected_quality, {}).get(kind) for kind in ("flatrate", "rent", "buy")):
            self.content_list_select = _first_nonempty_quality(self.content_stream_list, fallback="HD")
            if self.content_list_select in self.content_list:
                self.content_list_index = self.content_list.index(self.content_list_select)
            self.content_stream_index = 0
            try:
                config.justwatch.content_mode.value = self.content_list_select
            except Exception:
                pass
        jw_debug('%s build_gui offers grouped SD=%s HD=%s 4K=%s selected=%s' % (self.__class__.__name__, sum(len(self.content_stream_list["SD"][k]) for k in ("flatrate", "rent", "buy")), sum(len(self.content_stream_list["HD"][k]) for k in ("flatrate", "rent", "buy")), sum(len(self.content_stream_list["4K"][k]) for k in ("flatrate", "rent", "buy")), self.content_list_select))

        jw_debug('%s build_gui title=%r genres=%r description_len=%s' % (self.__class__.__name__, self.title, self.genres, len(self.description or '')))
        self['JustWatchTitleText'].setText(self.title)
        self['JustWatchGenresText'].setText(self.genres)
        self['JustWatchDescriptionText'].setText(self.description)

    def build_actors(self):
        credits = self.data.get("credits")
        if credits:
            for actor in credits:
                if actor.get("role") == "ACTOR":
                    name = actor.get("name") if actor.get("name") else None
                    character_name = actor.get("character_name") if actor.get(
                        "character_name") else ""
                    if name:
                        self.actors_list.append((name, character_name, actor.get("person_id")))
        self.update_actor_gui()

    def build_trailers(self):
        trailers = self.data.get("clips")
        if trailers:
            for item in trailers:
                if item.get("provider") == "youtube":
                    name = item.get("name") if item.get("name") else None
                    external_id = item.get("external_id") if item.get("external_id") else None
                    if name and external_id:
                        self.trailers_list.append((name, external_id))
        self.update_trailer_gui()

    def build_season(self):
        seasons = self.data.get("seasons")
        if seasons:
            for season in seasons:
                title = season.get("title") if season.get("title") else ""
                season_number = season.get("season_number")
                season_id = season.get("id")
                season_backend_id = season.get("jw_entity_id") or season.get("node_id") or season_id
                cover_destination = "%s/%s-season-poster.jpg" % (config.justwatch.cache_destination.value, str(season_id))
                cover_size = "big" if skinFactor == 1 else "small"
                cover_url = get_poster_url(season.get("poster"), size=cover_size) if season.get("poster") else None
                self.cover_list.append((cover_destination, cover_url))
                self.season_list.append((title, season_id, season_number, cover_destination, season_backend_id))
        self.season_list = sorted(self.season_list, key=lambda item: int(item[2]))
        self.setDownloadCoverList()
        self.update_season_gui()

    def update_season_gui(self, callback=None):
        data = [self.season_index, self.gui_mode, self.season_list]
        self.chooseJustWatchSeasonList.setList(list(map(season_entry, [data])))
        self.chooseJustWatchSeasonList.selectionEnabled(0)
        self.downloadPicList()

    def update_trailer_gui(self):
        data = [self.trailer_index, self.gui_mode, self.trailers_list]
        self.chooseJustWatchTrailersList.setList(list(map(trailer_entry, [data])))
        self.chooseJustWatchTrailersList.selectionEnabled(0)

    def update_actor_gui(self):
        data = [self.actor_index, self.gui_mode, self.actors_list]
        self.chooseJustWatchActorsList.setList(list(map(actors_entry, [data])))
        self.chooseJustWatchActorsList.selectionEnabled(0)

    def load_backdrop(self):
        jw_debug('%s load_backdrop list_count=%s index=%s' % (self.__class__.__name__, len(self.backdrop_list), getattr(self, 'backdrop_list_index', None)))
        if self.backdrop_list:
            (drop_url, drop_destination) = self.backdrop_list[self.backdrop_list_index]
            if not os.path.isfile(drop_destination):
                download_file(drop_url, drop_destination, self.update_backdrop)
            else:
                self.update_backdrop()

    def update_backdrop(self, callback=None):
        data = [self.backdrop_list_index, self.backdrop_list]
        self.chooseJustWatchBackdropList.setList(list(map(backdrop_entry, [data])))
        self.chooseJustWatchBackdropList.selectionEnabled(0)

    def keyOk(self):
        if self.gui_mode == 1:
            if self.content_list_index <= 2:
                self.content_list_select = self.content_list[self.content_list_index]
                config.justwatch.content_mode.value = self.content_list_select
                config.justwatch.content_mode.save()
                configfile.save()
            else:
                if self.is_watchlist:
                    remove_item_watchlist(self.data, object_type="show")
                else:
                    add_item_watchlist(self.data, object_type="show")
                text = REMOVE_WATCHLIST_INFO_STR if self.is_watchlist else ADD_WATCHLIST_INFO_STR
                self.session.open(MessageBox, windowTitle="JustWatch Watchlist", text=text,
                                  type=MessageBox.TYPE_INFO)
            self.build_content()
        elif 2 <= self.gui_mode <= 4:
            if self.gui_mode == 2:
                item = "flatrate"
            elif self.gui_mode == 3:
                item = "rent"
            else:
                item = "buy"
            data = self.content_stream_list[self.content_list_select][item]
            if data:
                (presentation_type, icon_destination, season_num, technical_name, title_id) = self.content_stream_list[self.content_list_select][item][self.content_stream_index]
                if "amazon" in technical_name and title_id:
                    if self.amazon.getIsLogin():
                        self.startJustWatchSpinner()
                        self.amazon.getItemDetails("amazon", title_id, self.cbReceivedWatchlistMode)
                    else:
                        self.session.open(MessageBox, windowTitle="JustWatch Amazon", text=_("Login failed"),
                                          type=MessageBox.TYPE_ERROR)
                elif "netflix" in technical_name and title_id:
                    if self.netflix.getIsLogin():
                        self.startJustWatchSpinner()
                        self.netflix.getProfileMode(technical_name, title_id, "show", self.cbReceivedWatchlistMode)
                    else:
                        self.session.open(MessageBox, windowTitle="JustWatch Netflix", text=_("Login failed"),
                                          type=MessageBox.TYPE_ERROR)
                elif "disneyplus" in technical_name and title_id:
                    if self.disney.getIsLogin():
                        self.startJustWatchSpinner()
                        self.disney.getProfiles(title_id, "show", self.cbReceivedWatchlistMode)
                    else:
                        self.session.open(MessageBox, windowTitle="JustWatch Disney+", text=_("Login failed"),
                                          type=MessageBox.TYPE_ERROR)
        elif self.gui_mode == 5:
            self.startJustWatchSpinner()
            season_backend_id = self.season_list[self.season_index][4] if len(self.season_list[self.season_index]) > 4 else self.season_list[self.season_index][1]
            get_season(self.cbReceivedSeason, season_backend_id)
        elif self.gui_mode == 6:
            (name, character_name, id) = self.actors_list[self.actor_index]
            self.startJustWatchSpinner()
            get_person_detail(callback=self.cbReceivedActor, person_id=id)
        elif self.gui_mode == 7:
            if self.trailers_list:
                (name, external_id) = self.trailers_list[self.trailer_index]
                self.startJustWatchSpinner()
                get_play_url(self.playTrailer, external_id, name)
        elif self.gui_mode == 8:
            technical_name = self["JustWatchProviderModeList"].getCurrent()[0][1]
            if technical_name == "amazon":
                details = self["JustWatchProviderModeList"].getCurrent()[0][2]
                if self["JustWatchProviderModeList"].getCurrent()[0][3] == "w":
                    do = self.amazon.setWatchlistAction(details)
                    if not do[1]:
                        self.session.open(MessageBox, WATCHLIST_ERROR_STR, MessageBox.TYPE_ERROR)
                    else:
                        text = REMOVE_WATCHLIST_INFO_STR if details.get("onWatchlist") else ADD_WATCHLIST_INFO_STR
                        self.session.open(MessageBox, windowTitle="JustWatch Amazon", text=text,
                                          type=MessageBox.TYPE_INFO)
                    self['BackgroundProviderModeList'].hide()
                    self['JustWatchProviderModeList'].hide()
                    self.gui_mode = self.last_gui_mode
                    if details.get("onWatchlist"):
                        remove_item_watchlist(self.data, object_type="show")
                    else:
                        add_item_watchlist(self.data, object_type="show")
                    self.build_content()
                    return
                elif self["JustWatchProviderModeList"].getCurrent()[0][3] == "o":
                    self.amazon.dream(details, "show")
                    return
            if technical_name == "netflix":
                onWatchlist = self["JustWatchProviderModeList"].getCurrent()[0][3]
                profile_url = self["JustWatchProviderModeList"].getCurrent()[0][2]
                title_id = self["JustWatchProviderModeList"].getCurrent()[0][4]
                if self["JustWatchProviderModeList"].getCurrent()[0][5] == "w":
                    if not self.netflix.getProfileId() == profile_url:
                        self.netflix.doSelectProfile(profile_url)
                    self.netflix.updateMyList(title_id, onWatchlist)
                    text = REMOVE_WATCHLIST_INFO_STR if onWatchlist else ADD_WATCHLIST_INFO_STR
                    self.session.open(MessageBox, windowTitle="JustWatch Netflix", text=text,
                                      type=MessageBox.TYPE_INFO)
                    self['BackgroundProviderModeList'].hide()
                    self['JustWatchProviderModeList'].hide()
                    self.gui_mode = self.last_gui_mode
                    if onWatchlist:
                        remove_item_watchlist(self.data, object_type="show")
                    else:
                        add_item_watchlist(self.data, object_type="show")
                    self.build_content()
                    return
                elif self["JustWatchProviderModeList"].getCurrent()[0][5] == "o":
                    self.netflix.netflixDream(title_id)
                    return
            if technical_name == "disney":
                onWatchlist = self["JustWatchProviderModeList"].getCurrent()[0][3]
                profile_url = self["JustWatchProviderModeList"].getCurrent()[0][2]
                title_id = self["JustWatchProviderModeList"].getCurrent()[0][4]
                if self["JustWatchProviderModeList"].getCurrent()[0][5] == "w":
                    watchlistMode = "remove" if onWatchlist else "add"
                    self.disney.setProfileWatchlist(profile_url, watchlistMode, title_id)
                    #text = REMOVE_WATCHLIST_INFO_STR if onWatchlist else ADD_WATCHLIST_INFO_STR
                    #self.session.open(MessageBox, windowTitle="JustWatch Disney+", text=text,
                    #                  type=MessageBox.TYPE_INFO)
                    self['BackgroundProviderModeList'].hide()
                    self['JustWatchProviderModeList'].hide()
                    self.gui_mode = self.last_gui_mode
                    if onWatchlist:
                        remove_item_watchlist(self.data, object_type="show")
                    else:
                        add_item_watchlist(self.data, object_type="show")
                    self.build_content()
                    return
                elif self["JustWatchProviderModeList"].getCurrent()[0][5] == "o":
                    self.disney.disneyDream(title_id, "SHOW")
                    return

    def cbReceivedWatchlistMode(self, callback):
        (technical_name, details) = callback
        self.stopJustWatchSpinner()
        if technical_name == "amazon":
            if self.gui_mode == 2:
                item = "flatrate"
            elif self.gui_mode == 3:
                item = "rent"
            else:
                item = "buy"
            data = self.content_stream_list[self.content_list_select][item]
            series_id = ""
            if data:
                series_id = data[self.content_stream_index][4]
            self.last_gui_mode = self.gui_mode
            self.gui_mode = 8
            text = REMOVE_WATCHLIST_STR if details.get("onWatchlist") else ADD_WATCHLIST_STR
            data = [(text, technical_name, details, "w")]
            if AMAZONDREAM:
                data.append(("Amazon", technical_name, series_id, "o"))
            self.chooseJustWatchProviderModeList.setList(list(map(provider_mode_entry, data)))
            self.chooseJustWatchProviderModeList.selectionEnabled(1)
            self['BackgroundProviderModeList'].show()
            self['JustWatchProviderModeList'].show()
        elif technical_name == "netflix":
            data = []
            if self.gui_mode == 2:
                item = "flatrate"
            elif self.gui_mode == 3:
                item = "rent"
            else:
                item = "buy"
            self.last_gui_mode = self.gui_mode
            self.gui_mode = 8
            if details:
                for profile_name, onWatchlist, profile_url, title_id in details:
                    text = REMOVE_WATCHLIST_STR if onWatchlist else ADD_WATCHLIST_STR
                    text = text + " --> " + profile_name
                    data.append((text, technical_name, profile_url, onWatchlist, title_id, "w"))
            if NETFLIXDREAM:
                data_id = self.content_stream_list[self.content_list_select][item]
                movie_id = ""
                if data_id:
                    movie_id = data_id[self.content_stream_index][4]
                data.append(("Netflix", technical_name, None, None, movie_id, "o"))
            self.chooseJustWatchProviderModeList.setList(list(map(provider_mode_entry, data)))
            self.chooseJustWatchProviderModeList.selectionEnabled(1)
            self['BackgroundProviderModeList'].show()
            self['JustWatchProviderModeList'].show()

        elif technical_name == "disney":
            data = []
            self.last_gui_mode = self.gui_mode
            if self.gui_mode == 2:
                item = "flatrate"
            elif self.gui_mode == 3:
                item = "rent"
            else:
                item = "buy"
            self.gui_mode = 8
            if details:
                for profileName, profileId, title_id, onWatchlist, contentId in details:
                    text = REMOVE_WATCHLIST_STR if onWatchlist else ADD_WATCHLIST_STR
                    text = text + " --> " + profileName
                    data.append((text, technical_name, profileId, onWatchlist, contentId, "w"))
            if DISNEYDREAM:
                data_id = self.content_stream_list[self.content_list_select][item]
                movie_id = ""
                if data_id:
                     movie_id = data_id[self.content_stream_index][4]
                data.append(("Disney+", technical_name, None, None, movie_id, "o"))
            self.chooseJustWatchProviderModeList.setList(list(map(provider_mode_entry, data)))
            self.chooseJustWatchProviderModeList.selectionEnabled(1)
            self['BackgroundProviderModeList'].show()
            self['JustWatchProviderModeList'].show()

    def cbReceivedActor(self, data):
        self.stopJustWatchSpinner()
        self.session.open(JustWatchPersonSearchScreen, data, self.providers, self.amazon, self.netflix)

    def cbReceivedSeason(self, season_data):
        if season_data:
            self.stopJustWatchSpinner()
            self.session.open(JustWatchEpisodesScreen, season_data, self.providers)

    def keyCancel(self):
        if self.gui_mode == 8:
            self['BackgroundProviderModeList'].hide()
            self['JustWatchProviderModeList'].hide()
            self.gui_mode = self.last_gui_mode
            return
        os.system("rm %s/*-backdrop.jpg" % config.justwatch.cache_destination.value)
        self.close()

    def keyLeft(self):
        if self.gui_mode == 0:
            if self.backdrop_list_index != 0:
                self.backdrop_list_index -= 1
            else:
                self.backdrop_list_index = len(self.backdrop_list) - 1
            self.load_backdrop()
        elif self.gui_mode == 1:
            if self.content_list_index != 0:
                self.content_list_index -= 1
                self.build_content()
        elif self.gui_mode == 2 or self.gui_mode == 3 or self.gui_mode == 4:
            if self.content_stream_index != 0:
                self.content_stream_index -= 1
                self.build_content()
        elif self.gui_mode == 5:
            if self.season_index != 0:
                self.season_index -= 1
                self.update_season_gui()
        elif self.gui_mode == 6:
            if self.actor_index != 0:
                self.actor_index -= 1
                self.update_actor_gui()
        elif self.gui_mode == 7:
            if self.trailer_index != 0:
                self.trailer_index -= 1
                self.update_trailer_gui()

    def keyRight(self):
        if self.gui_mode == 0:
            if self.backdrop_list_index != len(self.backdrop_list) - 1:
                self.backdrop_list_index += 1
            else:
                self.backdrop_list_index = 0
            self.load_backdrop()
        elif self.gui_mode == 1:
            if self.content_list_index != 3:
                self.content_list_index += 1
                self.build_content()
        elif self.gui_mode == 2:
            if self.content_stream_index < len(self.content_stream_list[self.content_list_select]["flatrate"]) - 1:
                self.content_stream_index += 1
                self.build_content()
        elif self.gui_mode == 3:
            if self.content_stream_index < len(self.content_stream_list[self.content_list_select]["rent"]) - 1:
                self.content_stream_index += 1
                self.build_content()
        elif self.gui_mode == 4:
            if self.content_stream_index < len(self.content_stream_list[self.content_list_select]["buy"]) - 1:
                self.content_stream_index += 1
                self.build_content()
        elif self.gui_mode == 5:
            if self.season_index < len(self.season_list) - 1:
                self.season_index += 1
            else:
                self.season_index = 0
            self.update_season_gui()
        elif self.gui_mode == 6:
            if self.actor_index < len(self.actors_list) - 1:
                self.actor_index += 1
            else:
                self.actor_index = 0
            self.update_actor_gui()
        elif self.gui_mode == 7:
            if self.trailer_index < len(self.trailers_list) - 1:
                self.trailer_index += 1
            else:
                self.trailer_index = 0
            self.update_trailer_gui()

    def keyUp(self):
        if self.gui_mode == 1:
            self.gui_mode -= 1
            self.do_show_gui_mode()
        elif self.gui_mode == 2 or self.gui_mode == 3 or self.gui_mode == 4 or self.gui_mode == 5:
            self.gui_mode -= 1
            self.season_index = 0
            self.content_stream_index = 0
            self.build_content()
            self.update_season_gui()
        elif self.gui_mode == 6:
            self.actor_index = 0
            self.gui_mode -= 1
            self.update_actor_gui()
            self.update_season_gui()
            self.do_show_gui_mode()
        elif self.gui_mode == 7:
            self.gui_mode -= 1
            self.trailer_index = 0
            self.update_trailer_gui()
            self.update_actor_gui()
        elif self.gui_mode == 8:
            self['JustWatchProviderModeList'].up()

    def keyDown(self):
        if self.gui_mode == 0:
            self.gui_mode += 1
            self.do_show_gui_mode()
        elif self.gui_mode == 1 or self.gui_mode == 2 or self.gui_mode == 3:
            self.gui_mode += 1
            self.content_stream_index = 0
            self.build_content()
        elif self.gui_mode == 4:
            self.gui_mode += 1
            self.build_content()
            self.season_index = 0
            self.update_season_gui()
        elif self.gui_mode == 5:
            self.gui_mode += 1
            self.do_show_gui_mode()
            self.update_actor_gui()
        elif self.gui_mode == 6 and self.trailers_list:
            self.gui_mode += 1
            self.actor_index = 0
            self.update_actor_gui()
            self.update_trailer_gui()
        elif self.gui_mode == 8:
            self['JustWatchProviderModeList'].down()

    def show_cover(self, data=None):
        if os.path.isfile(self.cover_destination):
            self['JustWatchCover'].instance.setPixmap(gPixmapPtr())
            self.scale = AVSwitch().getFramebufferScale()
            self.picload = ePicLoad()
            size = self['JustWatchCover'].instance.size()
            self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#001b1e25"))
            decode = self.picload.startDecode(self.cover_destination, 0, 0, False)
            if decode == 0:
                ptr = self.picload.getData()
                if ptr != None:
                    self['JustWatchCover'].instance.setPixmap(ptr)

    def playTrailer(self, callback):
        self.stopJustWatchSpinner()
        (ytlink, name) = callback
        if ytlink:
            sref = eServiceReference(4097, 0, ytlink)
            sref.setName(name)
            self.session.open(MoviePlayer, sref)
        else:
            self.session.open(MessageBox, TRAILER_ERROR_STR, MessageBox.TYPE_ERROR)

    def reloadCover(self):
        if not self.CoverTimerStatus:
            self.setLoad.reverse()
            if self.setLoad:
                (cover, link) = self.setLoad[0]
                if os.path.isfile(cover):
                    delete = self.setLoad[0]
                    self.setLoad.remove(delete)
                    self.CoverTimer.start(600, True)
                else:
                    self.CoverTimer.start(900, True)
            else:
                self.CoverTimerStatus = True
                self.CoverTimer.start(1100, True)
            self.update_season_gui()
        else:
            self.CoverTimerStatus = True
            self.stopTimer()
            self.update_season_gui()

    def stopTimer(self):
        if self.CoverTimer is not None:
            self.CoverTimer.stop()

    def setDownloadCoverList(self):
        self.download_list = setDownloadListCover(self.cover_list)
        self.downloadPicList()

    def downloadPicList(self):
        if self.download_list:
            self.setLoad = []
            x = 0
            for start, ende, dataList in self.download_list:
                if int(start) <= self.season_index <= int(ende):
                    self.setLoad = dataList
                    self.download_list.remove(self.download_list[x])
                x = x + 1
            x = 1
            if self.setLoad:
                self.CoverTimerStatus = False
                self.CoverTimer.start(300, True)
                for picSave, coverUrl in self.setLoad:
                    if not os.path.isfile(picSave):
                        if coverUrl is not None:
                            d = download_file(coverUrl, picSave)
                            if x % 2:
                                d.addCallback(self.update_season_gui)
                    x += 1


def provider_mode_entry(entry):
    res = [entry]
    res.append(MultiContentEntryText(pos=(int(10 / skinFactor), int(10 / skinFactor)),
                                     size=(int(780 / skinFactor), int(40 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0],
                                     backcolor=0x1a2632))

    res.append(MultiContentEntryText(pos=(0, int(58 / skinFactor)),
                                     size=(int(790 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0x545a5f))
    return res


def season_entry(entry):
    res = [entry]
    index = entry[0]
    mode = entry[1]
    data = entry[2]

    max_range = len(data) - index
    x = index

    if mode == 5:
        res.append(MultiContentEntryText(pos=(int(15 / skinFactor), int(15 / skinFactor)),
                                         size=(int(230 / skinFactor), int(322 / skinFactor)),
                                         flags=0 | 0,
                                         font=0,
                                         text="",
                                         backcolor=0xcac253))

    w_pos = int(20 / skinFactor)
    for i in range(max_range):  # title, season_id, season_number, cover_destination
        if w_pos > int(1800):
            break
        png_destination = data[x][3]
        if os.path.isfile(png_destination):
            png = load_pic_scale(png_destination, int(220 / skinFactor), int(312 / skinFactor), "#001a2632")
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, int(20 / skinFactor),
                        int(220 / skinFactor), int(312 / skinFactor), png))

        color = 0xcac253 if mode == 5 and i == 0 else 0xffffff
        res.append(MultiContentEntryText(pos=(w_pos, int(345 / skinFactor)),
                                         size=(int(220 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=data[x][0],
                                         color=color,
                                         backcolor=0x1a2632))

        x += 1
        w_pos = w_pos + int(250 / skinFactor)

    return res


def trailer_entry(entry):
    res = [entry]
    index = entry[0]
    mode = entry[1]
    data = entry[2]

    res.append(MultiContentEntryText(pos=(int(15 / skinFactor), int(5 / skinFactor)),
                                     size=(int(600 / skinFactor), int(46 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=1,
                                     text=TRAILER_STR,
                                     color=0x545a5f,
                                     backcolor=0x1a2632))

    if data:
        max_range = len(data) - index
        x = index
        w_pos = int(5 / skinFactor)
        for i in range(max_range):
            if w_pos > int(1790 / skinFactor):
                break
            (name, external_id) = data[x]

            color = 0xcac253 if mode == 7 and i == 0 else 0x545a5f
            res.append(MultiContentEntryText(pos=(w_pos, int(55 / skinFactor)),
                                             size=(int(400 / skinFactor), int(80 / skinFactor)),
                                             flags=RT_HALIGN_CENTER | RT_WRAP,
                                             font=0,
                                             text=name,
                                             color=color,
                                             backcolor=0x1a2632))

            w_pos = w_pos + int(450 / skinFactor)
            x += 1
    else:
        color = 0xcac253 if mode == 7 else 0xffffff
        res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(55 / skinFactor)),
                                         size=(int(800 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=NO_OFFERS_STR,
                                         color=color,
                                         backcolor=0x1a2632))

    return res


def actors_entry(entry):
    res = [entry]
    index = entry[0]
    mode = entry[1]
    data = entry[2]

    res.append(MultiContentEntryText(pos=(int(15 / skinFactor), int(5 / skinFactor)),
                                     size=(int(600 / skinFactor), int(46 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=1,
                                     text=ACTOR_STR,
                                     color=0x545a5f,
                                     backcolor=0x1a2632))
    if data:
        max_range = len(data) - index
        x = index
        w_pos = int(5 / skinFactor)
        for i in range(max_range):
            if w_pos > int(1790 / skinFactor):
                break
            (name, character_name, id) = data[x]

            w_name_len = len(name) * int(20 / skinFactor)
            w_character_name_len = len(character_name) * int(20 / skinFactor)

            item_len = w_character_name_len if w_name_len < w_character_name_len else w_name_len

            color = 0xcac253 if mode == 6 and i == 0 else 0x545a5f
            res.append(MultiContentEntryText(pos=(w_pos, int(55 / skinFactor)),
                                             size=(item_len, int(40 / skinFactor)),
                                             flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                             font=0,
                                             text=name,
                                             color=color,
                                             backcolor=0x1a2632))

            res.append(MultiContentEntryText(pos=(w_pos, int(110 / skinFactor)),
                                             size=(item_len, int(40 / skinFactor)),
                                             flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                             font=0,
                                             text=character_name,
                                             color=0xffffff,
                                             backcolor=0x1a2632))
            w_pos = w_pos + item_len + int(20 / skinFactor)
            x += 1
    else:
        color = 0xcac253 if mode == 6 else 0xffffff
        res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(55 / skinFactor)),
                                         size=(int(800 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=NO_OFFERS_STR,
                                         color=color,
                                         backcolor=0x1a2632))

    return res


def content_provider_entry(entry):
    res = [entry]
    # self.content_stream_index, self.gui_mode, self.content_list_select, data)
    index = entry[0]
    mode = entry[1]
    select = entry[2]
    data = entry[3]
    flatrate = data[select]["flatrate"]
    rent = data[select]["rent"]
    buy = data[select]["buy"]

    res.append(MultiContentEntryText(pos=(0, 0),
                                     size=(int(30 / skinFactor), int(180 / skinFactor)),
                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                     font=0,
                                     text=_("S\nt\nr\ne\na\nm"),
                                     color=0x000000,
                                     backcolor=0xffffff))

    w_size = int(40 / skinFactor)
    s = index if mode == 2 else 0
    max_range = len(flatrate) - s
    x = s
    if flatrate:
        for i in range(max_range):
            (presentation_type, icon_destination, season_num, technical_name, title_id) = flatrate[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                item_len = len(season_num) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(20 / skinFactor),
                            int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 2 and i == 0:
                    w_pos = w_size - int(5 / skinFactor) + icon_value
                    h_pos = int(15 / skinFactor)
                    size = int(110 / skinFactor)
                    png = LoadPixmap(SELECT_PROVIDER)
                else:
                    w_pos = w_size + icon_value
                    h_pos = int(20 / skinFactor)
                    size = int(100 / skinFactor)
                    png = LoadPixmap(RADIUS_PROVIDER)

                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, h_pos, size, size, png))
                res.append(MultiContentEntryText(pos=(w_size, int(130 / skinFactor)),
                                                 size=(item_len, int(40 / skinFactor)),
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                                 font=0,
                                                 text=season_num,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 2 else 0xffffff
        res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(60 / skinFactor)),
                                         size=(int(400 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=NO_OFFERS_STR,
                                         color=color,
                                         backcolor=0x1a2632))

    res.append(MultiContentEntryText(pos=(0, int(178 / skinFactor)),
                                     size=(int(1390 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0xffffff))

    res.append(MultiContentEntryText(pos=(0, int(180 / skinFactor)),
                                     size=(int(30 / skinFactor), int(180 / skinFactor)),
                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                     font=0,
                                     text=_("R\ne\nn\nt"),
                                     color=0xffffff,
                                     backcolor=0x545a5f))

    w_size = int(40 / skinFactor)
    s = index if mode == 3 else 0
    max_range = len(rent) - s
    x = s
    if rent:
        for i in range(max_range):
            (presentation_type, icon_destination, season_num, technical_name, title_id) = rent[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                item_len = len(season_num) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(200 / skinFactor),
                            int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 3 and i == 0:
                    w_pos = w_size - int(5 / skinFactor) + icon_value
                    h_pos = int(195 / skinFactor)
                    size = int(110 / skinFactor)
                    png = LoadPixmap(SELECT_PROVIDER)
                else:
                    w_pos = w_size + icon_value
                    h_pos = int(200 / skinFactor)
                    size = int(100 / skinFactor)
                    png = LoadPixmap(RADIUS_PROVIDER)
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, h_pos, size, size, png))
                res.append(MultiContentEntryText(pos=(w_size, int(310 / skinFactor)),
                                                 size=(item_len, int(40 / skinFactor)),
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                                 font=0,
                                                 text=season_num,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 3 else 0xffffff
        res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(240 / skinFactor)),
                                         size=(int(400 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=NO_OFFERS_STR,
                                         color=color,
                                         backcolor=0x1a2632))

    res.append(MultiContentEntryText(pos=(0, int(358 / skinFactor)),
                                     size=(int(1390 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0x545a5f))

    res.append(MultiContentEntryText(pos=(0, int(360 / skinFactor)),
                                     size=(int(30 / skinFactor), int(180 / skinFactor)),
                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                     font=0,
                                     text=_("B\nu\ny"),
                                     color=0xffffff,
                                     backcolor=0x383c3f))

    w_size = int(40 / skinFactor)
    s = index if mode == 4 else 0
    max_range = len(buy) - s
    x = s
    if buy:
        for i in range(max_range):
            (presentation_type, icon_destination, season_num, technical_name, title_id) = buy[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                item_len = len(season_num) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(380 / skinFactor),
                            int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 4 and i == 0:
                    w_pos = w_size - int(5 / skinFactor) + icon_value
                    h_pos = int(375 / skinFactor)
                    size = int(110 / skinFactor)
                    png = LoadPixmap(SELECT_PROVIDER)
                else:
                    w_pos = w_size + icon_value
                    h_pos = int(380 / skinFactor)
                    size = int(100 / skinFactor)
                    png = LoadPixmap(RADIUS_PROVIDER)
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, h_pos, size, size, png))
                res.append(MultiContentEntryText(pos=(w_size, int(490 / skinFactor)),
                                                 size=(item_len, int(40 / skinFactor)),
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                                 font=0,
                                                 text=season_num,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 4 else 0xffffff
        res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(420 / skinFactor)),
                                         size=(int(400 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=NO_OFFERS_STR,
                                         color=color,
                                         backcolor=0x1a2632))

    res.append(MultiContentEntryText(pos=(0, int(538 / skinFactor)),
                                     size=(int(1390 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0x383c3f))
    return res


def content_entry(entry):
    res = [entry]
    index = entry[0]
    mode = entry[1]
    select = entry[2]
    data = entry[3]
    watchlist_mode = entry[4]

    x = 0
    p_size = 0
    png = LoadPixmap(BACKGROUND_CONTENT_PNG)
    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 0, 0,
                int(596 / skinFactor), int(50 / skinFactor), png))
    for i in range(3):
        item = data[i]
        if x == index and mode == 1:
            png = LoadPixmap(CONTENT_SELECT_PNG)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, p_size, 0,
                        int(100 / skinFactor), int(50 / skinFactor), png))
        color = 0xcac253 if select == item else 0x545a5f
        res.append(MultiContentEntryText(pos=(p_size + int(7 / skinFactor), int(5 / skinFactor)),
                                         size=(int(100 / skinFactor) - int(14 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=item,
                                         color=color,
                                         backcolor=0x1b1e25))
        plus = 115 if DESKTOPSIZE.width() > 1280 else 77
        p_size = p_size + plus
        x += 1

    color = 0xcac253 if index == 3 and mode == 1 else 0x545a5f
    if index == 3 and mode == 1:
        png = LoadPixmap(CONTENT_WATCHLIST_SELECT_PNG)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, p_size, 0,
                    int(250 / skinFactor), int(50 / skinFactor), png))
    res.append(MultiContentEntryText(pos=(p_size + int(40 / skinFactor), int(5 / skinFactor)),
                                     size=(int(150 / skinFactor), int(40 / skinFactor)),
                                     flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                     font=0,
                                     text=watchlist_mode,
                                     color=color,
                                     backcolor=0x1b1e25))

    return res


def backdrop_entry(entry):
    res = [entry]
    index = entry[0]
    data = entry[1]
    if data:
        (drop_url, drop_destination) = data[index]
        if os.path.isfile(drop_destination):
            png = load_pic_scale(drop_destination, int(1840 / skinFactor), int(958 / skinFactor), "#001b1e25")
            res.append(
                (eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 0, 0,
                 int(1840 / skinFactor), int(958 / skinFactor), png))
            if len(data) % 2:
                x = int(len(data) / 2) * int(40 / skinFactor) - int(10 / skinFactor)
            else:
                x = int(len(data) / 2) * int(40 / skinFactor) - int(15 / skinFactor)
            w_pos = int(920 / skinFactor) - x
            for i in range(len(data)):
                icon = BACKDROP_SELECT_PNG if i == index else BACKDROP_NO_SELECT_PNG
                png = LoadPixmap(icon)
                res.append(
                    (eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, int(550 / skinFactor),
                     int(30 / skinFactor), int(30 / skinFactor), png))
                w_pos = w_pos + int(40 / skinFactor)

    return res


def load_pic_scale(pic, pwidth, pheight, color):
    scale = AVSwitch().getFramebufferScale()
    picload = ePicLoad()
    picload.setPara((pwidth, pheight, scale[0], scale[1], False, 1, color))
    if not picload.startDecode(pic, 0, 0, False):
        ptr = picload.getData()
        if ptr != None:
            del picload
            return ptr


def setDownloadListCover(coverList):
    downloadListe = []
    split = 12
    if len(coverList) > split:
        listSplit = len(coverList) // split
        listSplitLast = len(coverList) - (listSplit * split)

        x = 0
        data = []
        for i in range(listSplit):
            liste = []
            for i in range(split):
                liste.append((coverList[x]))
                x = x + 1
            data.append(liste)

        if not listSplitLast == 0:
            liste = []
            for i in range(listSplitLast):
                liste.append((coverList[x]))
                x = x + 1
            data.append(liste)

        if data:
            start = 0 - 6
            ende = len(data[0]) + 2
            for dataList in data:
                downloadListe.append((start, ende, dataList))
                start = start + len(dataList)
                ende = ende + len(dataList)
    else:
        x = len(coverList) - 1
        downloadListe.append((0, x, coverList))
    return downloadListe
