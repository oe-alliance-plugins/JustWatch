from Screens.Screen import Screen
from Components.AVSwitch import AVSwitch
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.Renderer.JustWatchVRunningText import JustWatchVRunningText
from Components.config import config, configfile
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
from enigma import ePicLoad, gFont, eServiceReference, gPixmapPtr, \
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_WRAP

from .justWatch import *
from .just_watch_episodes_helper import EpisodesList
from .__init__ import _

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    BACKDROP_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_select_30x30.png"
    BACKDROP_NO_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_no_select_30x30.png"
    BACKGROUND_CONTENT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_330x50.png"
    CONTENT_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_select_100x50.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_110x110.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_100x100.png"

else:
    skinFactor = 1.5
    BACKDROP_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_select_20x20.png"
    BACKDROP_NO_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_no_select_20x20.png"
    BACKGROUND_CONTENT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_220x33.png"
    CONTENT_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_select_66x33.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_73x73.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_66x66.png"

NO_OFFERS_STR = _("There are currently no offers.")
EPISODE_STR = _(" Episode")
EPISODES_STR = _(" Episodes")
DESCRIPTION_STR = _("Unfortunately no description available at the moment.")


class JustWatchEpisodesScreen(Screen, EpisodesList):
    def __init__(self, session, data, providers):
        if DESKTOPSIZE.width() >= 1920:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatchEpisodesScreen" position="center,center" size="1920,1080" title="JustWatch">
                           <!-- Gui 1 -->
                           <widget name="JustWatchCover" position="40,20" size="422,600" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/transparent_422x600.png" alphatest="blend" zPosition="3" />
                           <widget name="JustWatchContent" position="490,20" size="350,50" backgroundColor="#001b1e25" zPosition="1" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchContentProvider" position="490,80" size="1390,540" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchTitleText" position="40,640" size="1840,50" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00ffffff" zPosition="1" font="JW; 38" valign="center" halign="left"/>
                           <widget name="JustWatchDescriptionText" position="40,725" size="1840,330" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 30" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="JustWatchDown" position="1836,1055" size="44,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/down_44x25.png" zPosition="1" />
                           <!-- Gui 2 -->
                           <widget name="JustWatchEpisodesGui" position="40,30" size="1820,660" foregroundColor="#00ffffff" backgroundColor="#001a2632" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" zPosition="4" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarEpisodes" position="1860,30" size="20,660" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="660" />
                           <widget name="JustWatchEpisodeDescriptionText" position="40,720" size="1840,330" backgroundColor="#001a2632" transparent="0" foregroundColor="#00545a5f" zPosition="5" font="JW; 30" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="BackgroundSelectEpiOffers" position="243,198" size="1434,644" backgroundColor="#00cac253" transparent="0" zPosition="6" />
                           <widget name="BackgroundEpiOffers" position="245,200" size="1430,640" backgroundColor="#001a2632" transparent="0" zPosition="7" />
                           <widget name="JustWatchEpisodeContent" position="265,220" size="350,50" backgroundColor="#001a2632" zPosition="8" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchEpisodeContentProvider" position="265,280" size="1390,540" backgroundColor="#001a2632" zPosition="8" transparent="1" enableWrapAround="1" />
                           </screen>
                        """
        else:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatchEpisodesScreen" position="center,center" size="1280,720" title="JustWatch">
                           <!-- Gui 1 -->
                           <widget name="JustWatchCover" position="26,13" size="281,400" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/transparent_281x400.png" alphatest="blend" zPosition="3" />
                           <widget name="JustWatchContent" position="326,13" size="233,33" backgroundColor="#001b1e25" zPosition="1" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchContentProvider" position="326,53" size="926,360" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchTitleText" position="26,426" size="1226,33" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00ffffff" zPosition="1" font="JW; 25" valign="center" halign="left"/>
                           <widget name="JustWatchDescriptionText" position="26,483" size="1226,220" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 20" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="JustWatchDown" position="1224,703" size="29,16" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/down_29x16.png" zPosition="1" />
                           <!-- Gui 2 -->
                           <widget name="JustWatchEpisodesGui" position="26,20" size="1213,440" foregroundColor="#00ffffff" backgroundColor="#001a2632" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" zPosition="4" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarEpisodes" position="1240,20" size="13,440" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="440" />
                           <widget name="JustWatchEpisodeDescriptionText" position="26,480" size="1226,220" backgroundColor="#001a2632" transparent="0" foregroundColor="#00545a5f" zPosition="5" font="JW; 20" valign="top" halign="left" options="movetype=swimming,startpoint=0,direction=top,always=0,steptime=150,repeat=999,startdelay=10000,wrap"/>
                           <widget name="BackgroundSelectEpiOffers" position="162,132" size="956,429" backgroundColor="#00cac253" transparent="0" zPosition="6" />
                           <widget name="BackgroundEpiOffers" position="163,133" size="953,426" backgroundColor="#001a2632" transparent="0" zPosition="7" />
                           <widget name="JustWatchEpisodeContent" position="176,146" size="233,33" backgroundColor="#001a2632" zPosition="8" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchEpisodeContentProvider" position="176,186" size="926,360" backgroundColor="#001a2632" zPosition="8" transparent="1" enableWrapAround="1" />
                           </screen>
                        """
        Screen.__init__(self, session)

        EpisodesList.__init__(self)

        self['actions'] = NumberActionMap(['JustWatch_Actions'], {'ok': self.keyOk,
                                                                  'cancel': self.keyCancel,
                                                                  'left': self.keyLeft,
                                                                  'right': self.keyRight,
                                                                  'up': self.keyUp,
                                                                  'down': self.keyDown,
                                                                  }, -1)

        self.chooseJustWatchContentList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchContentList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchContentList.l.setItemHeight(int(50 / skinFactor))
        self['JustWatchContent'] = self.chooseJustWatchContentList

        self.chooseJustWatchContentProviderList = MenuList([], enableWrapAround=True,
                                                           content=eListboxPythonMultiContent)
        self.chooseJustWatchContentProviderList.l.setFont(0, gFont('JW', int(22 / skinFactor)))
        self.chooseJustWatchContentProviderList.l.setItemHeight(int(540 / skinFactor))
        self['JustWatchContentProvider'] = self.chooseJustWatchContentProviderList

        self['JustWatchTitleText'] = Label("")
        self['JustWatchGenresText'] = Label("")
        self['JustWatchDescriptionText'] = JustWatchVRunningText("")
        self['JustWatchCover'] = Pixmap()
        self['JustWatchDown'] = Pixmap()

        self.title = ""
        self.description = ""
        self.cover_destination = "%s/%s-season-poster.jpg" % (
        config.justwatch.cache_destination.value, str(data.get("id")))
        self.data = data
        self.episode_data = []
        self.providers = providers
        self.content_list = ["SD", "HD", "4K"]
        self.content_list_select = config.justwatch.content_mode.value
        self.content_list_index = self.content_list.index(config.justwatch.content_mode.value)

        self.content_stream_list = {}
        self.content_stream_index = 0
        self.episode_index = 0

        self.gui_mode = 4

        self.onLayoutFinish.append(self.build_gui)
        self.onLayoutFinish.append(self.do_show_gui_mode)
        self.onLayoutFinish.append(self.show_cover)

    def do_show_gui_mode(self):
        if self.gui_mode <= 3:
            self.do_hide_episodes_gui()

            self['JustWatchCover'].show()
            self['JustWatchContent'].show()
            self['JustWatchContentProvider'].show()
            self['JustWatchTitleText'].show()
            self['JustWatchDescriptionText'].show()
            self['JustWatchDown'].show()
        else:
            self['JustWatchCover'].hide()
            self['JustWatchContent'].hide()
            self['JustWatchContentProvider'].hide()
            self['JustWatchTitleText'].hide()
            self['JustWatchDescriptionText'].hide()
            self['JustWatchDown'].hide()

            self.do_show_episodes_gui(self.episode_data)

    def build_content(self):
        data = [self.content_list_index, self.gui_mode, self.content_list_select, self.content_list]
        self.chooseJustWatchContentList.setList(list(map(content_entry, [data])))
        self.chooseJustWatchContentList.selectionEnabled(0)

        data = [self.content_stream_index, self.gui_mode, self.content_list_select, self.content_stream_list]
        self.chooseJustWatchContentProviderList.setList(list(map(content_provider_entry, [data])))
        self.chooseJustWatchContentProviderList.selectionEnabled(0)

    def _normalize_offer_values(self, item):
        monetization_type = (item.get("monetization_type") or "")
        monetization_type = str(monetization_type).strip().lower()

        presentation_type = (item.get("presentation_type") or "")
        presentation_type = str(presentation_type).strip().lower()
        if presentation_type in ("_4k", "4k", "uhd"):
            presentation_type = "4K"
        elif presentation_type == "hd":
            presentation_type = "HD"
        else:
            presentation_type = "SD"
        return monetization_type, presentation_type

    def _select_available_quality(self, offers_data, current_select):
        for quality in (current_select, "HD", "4K", "SD"):
            if quality in offers_data and any(offers_data[quality][k] for k in ("flatrate", "rent", "buy")):
                return quality
        return current_select

    def build_gui(self):
        century = " (" + str(self.data.get("original_release_year")) + ")" if self.data.get(
            "original_release_year") else ""
        original_title = " " + self.data.get("original_title") + " " if self.data.get(
            "original_title") else ""
        self.title = self.data.get("show_title") + original_title + century if self.data.get(
            "show_title") else "" + century
        self.description = self.data.get("short_description") if self.data.get(
            "short_description") else DESCRIPTION_STR

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
                monetization_type, presentation_type = self._normalize_offer_values(item)
                episode_num = str(item.get("element_count")) + EPISODE_STR if item.get("element_count") == 1 else str(
                    item.get("element_count")) + EPISODES_STR
                provider = get_provider_over_id(self.providers, item.get("provider_id"))
                technical_name = provider.get("technical_name") if provider.get(
                    "technical_name") else ""
                icon_destination = "%s/provider/%s.jpg" % (config.justwatch.cache_destination.value, technical_name)
                short_name = provider.get("short_name") if provider.get("short_name") else "no_provider"
                select_all = True if config.justwatch.providers.value == "" else False
                if short_name in config.justwatch.providers.value.split(",") or select_all:
                    if monetization_type == "buy":
                        if presentation_type == "SD":
                            sd_buy.append((presentation_type, icon_destination, episode_num))
                        elif presentation_type == "HD":
                            hd_buy.append((presentation_type, icon_destination, episode_num))
                        elif presentation_type == "4K":
                            uhd_buy.append((presentation_type, icon_destination, episode_num))
                    elif monetization_type == "flatrate":
                        if presentation_type == "SD":
                            sd_flatrate.append((presentation_type, icon_destination, episode_num))
                        elif presentation_type == "HD":
                            hd_flatrate.append((presentation_type, icon_destination, episode_num))
                        elif presentation_type == "4K":
                            uhd_flatrate.append((presentation_type, icon_destination, episode_num))
                    elif monetization_type == "rent":
                        if presentation_type == "SD":
                            sd_rent.append((presentation_type, icon_destination, episode_num))
                        elif presentation_type == "HD":
                            hd_rent.append((presentation_type, icon_destination, episode_num))
                        elif presentation_type == "4K":
                            uhd_rent.append((presentation_type, icon_destination, episode_num))
        self.content_stream_list = {"SD": {"flatrate": sd_flatrate,
                                           "rent": sd_rent,
                                           "buy": sd_buy}}
        self.content_stream_list.update({"HD": {"flatrate": hd_flatrate,
                                                "rent": hd_rent,
                                                "buy": hd_buy}})
        self.content_stream_list.update({"4K": {"flatrate": uhd_flatrate,
                                                "rent": uhd_rent,
                                                "buy": uhd_buy}})

        self.content_list_select = self._select_available_quality(self.content_stream_list, self.content_list_select)
        if self.content_list_select in self.content_list:
            self.content_list_index = self.content_list.index(self.content_list_select)
            self.content_stream_index = 0
            config.justwatch.content_mode.value = self.content_list_select

        self['JustWatchTitleText'].setText(self.title)
        self['JustWatchDescriptionText'].setText(self.description)
        self.build_content()
        self.build_episode_data()

    def build_episode_data(self):
        episodes = self.data.get("episodes")
        if episodes:
            for episode in episodes:
                episode_number = episode.get("episode_number")
                title = episode.get("title") if episode.get("title") else EPISODE_STR + " " + str(
                    episode_number)
                short_description = episode.get("short_description") if episode.get(
                    "short_description") else DESCRIPTION_STR
                runtime = str(episode.get("runtime")) + "Min." if episode.get("runtime") else ""
                season_number = episode.get("season_number")
                short_title = "S" + str(season_number) + " E" + str(episode_number) + " - "
                offers = self.get_offers(episode.get("offers"))
                self.episode_data.append((title, short_title, episode_number, short_description, runtime, offers))

    def get_offers(self, offers):
        sd_buy = []
        sd_flatrate = []
        sd_rent = []
        hd_buy = []
        hd_flatrate = []
        hd_rent = []
        uhd_buy = []
        uhd_flatrate = []
        uhd_rent = []
        if offers:
            for item in offers:
                monetization_type, presentation_type = self._normalize_offer_values(item)
                currency = item.get("currency") if item.get("currency") else None
                retail_price = item.get("retail_price")
                provider = get_provider_over_id(self.providers, item.get("provider_id"))
                technical_name = provider.get("technical_name") if provider.get(
                    "technical_name") else ""
                icon_destination = "%s/provider/%s.jpg" % (config.justwatch.cache_destination.value, technical_name)
                short_name = provider.get("short_name") if provider.get("short_name") else "no_provider"
                select_all = True if config.justwatch.providers.value == "" else False
                if short_name in config.justwatch.providers.value.split(",") or select_all:
                    if monetization_type == "buy":
                        if presentation_type == "SD":
                            sd_buy.append((currency, presentation_type, icon_destination, retail_price))
                        elif presentation_type == "HD":
                            hd_buy.append((currency, presentation_type, icon_destination, retail_price))
                        elif presentation_type == "4K":
                            uhd_buy.append((currency, presentation_type, icon_destination, retail_price))
                    elif monetization_type == "flatrate":
                        if presentation_type == "SD":
                            sd_flatrate.append((currency, presentation_type, icon_destination, retail_price))
                        elif presentation_type == "HD":
                            hd_flatrate.append((currency, presentation_type, icon_destination, retail_price))
                        elif presentation_type == "4K":
                            uhd_flatrate.append((currency, presentation_type, icon_destination, retail_price))
                    elif monetization_type == "rent":
                        if presentation_type == "SD":
                            sd_rent.append((currency, presentation_type, icon_destination, retail_price))
                        elif presentation_type == "HD":
                            hd_rent.append((currency, presentation_type, icon_destination, retail_price))
                        elif presentation_type == "4K":
                            uhd_rent.append((currency, presentation_type, icon_destination, retail_price))
        offers_data = {"SD": {"flatrate": sd_flatrate,
                              "rent": sd_rent,
                              "buy": sd_buy}}
        offers_data.update({"HD": {"flatrate": hd_flatrate,
                                   "rent": hd_rent,
                                   "buy": hd_buy}})
        offers_data.update({"4K": {"flatrate": uhd_flatrate,
                                   "rent": uhd_rent,
                                   "buy": uhd_buy}})
        return offers_data

    def keyOk(self):
        if self.gui_mode == 0:
            self.content_list_select = self.content_list[self.content_list_index]
            config.justwatch.content_mode.value = self.content_list_select
            config.justwatch.content_mode.save()
            configfile.save()
            self.build_content()
        elif self.gui_mode >= 4:
            gui_mode = self.key_episodes_ok()
            if gui_mode is not None:
                self.gui_mode = gui_mode

    def keyCancel(self):
        if 4 < self.gui_mode <= 8:
            self.do_hide_episode_offers()
            self.episode_gui_mode = 5
            self.gui_mode = 4
        else:
            self.close()

    def keyLeft(self):
        if self.gui_mode == 0:
            if self.content_list_index != 0:
                self.content_list_index -= 1
                self.build_content()
        elif self.gui_mode == 1 or self.gui_mode == 2 or self.gui_mode == 3:
            if self.content_stream_index != 0:
                self.content_stream_index -= 1
                self.build_content()
        elif self.gui_mode >= 4:
            self.key_episodes_left()

    def keyRight(self):
        if self.gui_mode == 0:
            if self.content_list_index != 2:
                self.content_list_index += 1
                self.build_content()
        elif self.gui_mode == 1:
            if self.content_stream_index < len(self.content_stream_list[self.content_list_select]["flatrate"]) - 1:
                self.content_stream_index += 1
                self.build_content()
        elif self.gui_mode == 2:
            if self.content_stream_index < len(self.content_stream_list[self.content_list_select]["rent"]) - 1:
                self.content_stream_index += 1
                self.build_content()
        elif self.gui_mode == 3:
            if self.content_stream_index < len(self.content_stream_list[self.content_list_select]["buy"]) - 1:
                self.content_stream_index += 1
                self.build_content()
                # self.update_epi_gui()
        elif self.gui_mode >= 4:
            self.key_episodes_right()

    def keyUp(self):
        if self.gui_mode == 1 or self.gui_mode == 2 or self.gui_mode == 3:
            self.gui_mode -= 1
            self.content_stream_index = 0
            self.build_content()
        elif self.gui_mode >= 4:
            if self.get_episodes_index() != 0 or self.episode_offers_show:
                self.key_episodes_up()
            else:
                self.gui_mode -= 1
                self.do_show_gui_mode()

    def keyDown(self):
        if self.gui_mode == 0 or self.gui_mode == 1 or self.gui_mode == 2:
            self.gui_mode += 1
            self.content_stream_index = 0
            self.build_content()
            return
        elif self.gui_mode == 3:
            self.gui_mode += 1
            self.do_show_gui_mode()
            return
        self.key_episodes_down()

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


def episode_offer_entry(entry):
    res = [entry]
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
    s = index if mode == 5 else 0
    max_range = len(flatrate) - s
    x = s
    if flatrate:
        for i in range(max_range):
            (currency, presentation_type, icon_destination, retail_price) = flatrate[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size, int(20 / skinFactor),
                            int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 5 and i == 0:
                    w_pos = w_size - int(5 / skinFactor)
                    h_pos = int(15 / skinFactor)
                    size = int(110 / skinFactor)
                    png = LoadPixmap(SELECT_PROVIDER)
                else:
                    w_pos = w_size
                    h_pos = int(20 / skinFactor)
                    size = int(100 / skinFactor)
                    png = LoadPixmap(RADIUS_PROVIDER)
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, h_pos, size, size, png))
                res.append(MultiContentEntryText(pos=(w_size, int(130 / skinFactor)),
                                                 size=(int(100 / skinFactor), int(40 / skinFactor)),
                                                 flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                                 font=0,
                                                 text="Flat",
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + int(120 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 5 else 0xffffff
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
    s = index if mode == 6 else 0
    max_range = len(rent) - s
    x = s
    if rent:
        for i in range(max_range):
            (currency, presentation_type, icon_destination, retail_price) = rent[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                retail_price = get_currency(str(retail_price), currency)
                item_len = len(retail_price) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(200 / skinFactor),
                            int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 6 and i == 0:
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
                                                 text=retail_price,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 6 else 0xffffff
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
    s = index if mode == 7 else 0
    max_range = len(buy) - s
    x = s
    if buy:
        for i in range(max_range):
            (currency, presentation_type, icon_destination, retail_price) = buy[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                retail_price = get_currency(str(retail_price), currency)
                item_len = len(retail_price) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(380 / skinFactor),
                            int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 7 and i == 0:
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
                                                 text=retail_price,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 7 else 0xffffff
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
    s = index if mode == 1 else 0
    max_range = len(flatrate) - s
    x = s
    if flatrate:
        for i in range(max_range):
            (presentation_type, icon_destination, episode_num) = flatrate[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                item_len = len(episode_num) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append(
                    (eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(20 / skinFactor),
                     int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 1 and i == 0:
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
                                                 text=episode_num,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 1 else 0xffffff
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
    s = index if mode == 2 else 0
    max_range = len(rent) - s
    x = s
    if rent:
        for i in range(max_range):
            (presentation_type, icon_destination, episode_num) = rent[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                item_len = len(episode_num) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append(
                    (eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(200 / skinFactor),
                     int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 2 and i == 0:
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
                                                 text=episode_num,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 2 else 0xffffff
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
    s = index if mode == 3 else 0
    max_range = len(buy) - s
    x = s
    if buy:
        for i in range(max_range):
            (presentation_type, icon_destination, episode_num) = buy[x]
            if w_size > int(1800 / skinFactor):
                break
            if os.path.isfile(icon_destination):
                item_len = len(episode_num) * int(12 / skinFactor)
                icon_value = 0
                if item_len <= int(100 / skinFactor):
                    item_len = int(100 / skinFactor)
                else:
                    icon_value = (item_len - int(100 / skinFactor)) / 2
                png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
                res.append(
                    (eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size + icon_value, int(380 / skinFactor),
                     int(100 / skinFactor), int(100 / skinFactor), png))

                if mode == 3 and i == 0:
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
                                                 text=episode_num,
                                                 color=0xffffff,
                                                 backcolor=0x1a2632))
                w_size = w_size + item_len + int(20 / skinFactor)
                x += 1
    else:
        color = 0xcac253 if mode == 3 else 0xffffff
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

    x = 0
    p_size = 0
    png = LoadPixmap(BACKGROUND_CONTENT_PNG)
    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 0, 0,
                int(330 / skinFactor), int(50 / skinFactor), png))
    for i in range(3):
        item = data[i]
        if x == index and mode == 0:
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
