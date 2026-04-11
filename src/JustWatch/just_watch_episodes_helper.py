from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
from Components.AVSwitch import AVSwitch
from Components.Label import Label
from Components.config import config, configfile
from Components.MultiContent import MultiContentEntryText
from Components.Renderer.JustWatchVRunningText import JustWatchVRunningText
from enigma import ePicLoad, gFont, addFont, ePythonMessagePump, eServiceReference, eTimer, gPixmapPtr,\
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP
import math
from .justWatch import *
from .__init__ import _

SCROLLBARBACKCOLOR = 0x545a5f
SCROLLBARSLIDERCOLOR = 0xcac253

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    BACKDROP_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_select_30x30.png"
    BACKDROP_NO_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_no_select_30x30.png"
    BACKGROUND_CONTENT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_epi_330x50.png"
    CONTENT_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_select_100x50.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_110x110.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_100x100.png"

else:
    skinFactor = 1.5
    BACKDROP_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_select_20x20.png"
    BACKDROP_NO_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/backdrop_no_select_20x20.png"
    BACKGROUND_CONTENT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_epi_220x33.png"
    CONTENT_SELECT_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_select_66x33.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_73x73.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_66x66.png"


NO_OFFERS_STR = _("There are currently no offers.")
EPISODE_STR = _(" Episode")
EPISODES_STR = _(" Episodes")
DESCRIPTION_STR = _("Unfortunately no description available at the moment.")


class episodes_scroll_bar():
    def __init__(self, height_list, label_height, value):
        self.EpisodesScrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.EpisodesScrollbar.l.setFont(0, gFont('Regular', 1))
        self.EpisodesScrollbar_value = value
        self[self.EpisodesScrollbar_value] = self.EpisodesScrollbar

        self.isShowGenre = False
        self.wight_episodes = None
        self.height_episodes = 1
        self.wight_episodes_slider = None
        self.height_episodes_slider = None
        self.height_episodes_list = height_list
        self.genre_label_height = label_height
        self.genre_max_label_page = None
        self.wight_episodes_background = None

        self.onLayoutFinish.append(self.doHideScrollbarEpisodes)
        self.onLayoutFinish.append(self.setSizeEpisodes)

    def doHideScrollbarEpisodes(self):
        self[self.EpisodesScrollbar_value].hide()
        self.isShowGenre = False

    def doShowScrollbarEpisodes(self):
        self[self.EpisodesScrollbar_value].show()
        self.isShowGenre = True

    def setSizeEpisodes(self):
        self.genre_max_label_page = (self.height_episodes_list // self.genre_label_height)
        self.wight_episodes_slider = int(6 / skinFactor)
        self.wight_episodes = int(7 / skinFactor)
        self.wight_episodes_background = int(2 / skinFactor)

    def loadScrollbarEpisodes(self, index=0, max_items=0, new_scall=None):
        if self.height_episodes_list and self.genre_label_height and self.genre_max_label_page < max_items:
            max_items_show = self.height_episodes_list // self.genre_label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.height_episodes_slider = int(self.height_episodes_list / max_slider_pos)

            x = self.genre_max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.height_episodes_list - self.height_episodes_slider
                    break
                x = x + self.genre_max_label_page
                s = s + self.height_episodes_slider
            if not self.height_episodes == s or new_scall:
                self.height_episodes = s
                self.EpisodesScrollbar.setList(list(map(self.set_scrollbar_episodes, [1])))
                self[self.EpisodesScrollbar_value].selectionEnabled(0)
                if not self.isShowGenre:
                    self.doShowScrollbarEpisodes()
        else:
            if self.isShowGenre:
                self.doHideScrollbarEpisodes()

    def set_scrollbar_episodes(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.wight_episodes_background, self.height_episodes_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.wight_episodes, self.height_episodes), size=(self.wight_episodes_slider, self.height_episodes_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res


class EpisodesList(episodes_scroll_bar):
    def __init__(self):
        self.chooseJustWatchEpisodesList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchEpisodesList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchEpisodesList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchEpisodesGui'] = self.chooseJustWatchEpisodesList
        self['JustWatchEpisodeDescriptionText'] = JustWatchVRunningText("")

        self.chooseJustWatchEpisodeContentList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchEpisodeContentList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchEpisodeContentList.l.setItemHeight(int(50 / skinFactor))
        self['JustWatchEpisodeContent'] = self.chooseJustWatchEpisodeContentList

        self.chooseJustWatchEpisodeContentProviderList = MenuList([], enableWrapAround=True,
                                                           content=eListboxPythonMultiContent)
        self.chooseJustWatchEpisodeContentProviderList.l.setFont(0, gFont('JW', int(22 / skinFactor)))
        self.chooseJustWatchEpisodeContentProviderList.l.setItemHeight(int(540 / skinFactor))
        self['JustWatchEpisodeContentProvider'] = self.chooseJustWatchEpisodeContentProviderList

        self['BackgroundEpiOffers'] = Label("")
        self['BackgroundSelectEpiOffers'] = Label("")

        self.episodes_list = []
        self.episodes_list_show = False
        self.episode_offers_show = False
        self.episode_content_list = ["SD", "HD", "4K"]
        self.episode_content_stream_index = 0
        self.episode_gui_mode = 5

        self.episode_content_list_select = config.justwatch.content_mode.value
        self.episode_content_list_index = self.episode_content_list.index(config.justwatch.content_mode.value)

        episodes_scroll_bar.__init__(self, int(660 / skinFactor), int(60 / skinFactor), "MyScrollBarEpisodes")

        self.onLayoutFinish.append(self.do_hide_episodes_gui)
        self.onLayoutFinish.append(self.do_hide_episode_offers)

    def do_hide_episode_offers(self):
        self['BackgroundSelectEpiOffers'].hide()
        self['JustWatchEpisodeContent'].hide()
        self['JustWatchEpisodeContentProvider'].hide()
        self['BackgroundEpiOffers'].hide()
        self.episode_offers_show = False
        self.episode_content_stream_index = 0

    def do_show_episode_offers(self, offers):
        if self.episodes_list:
            self['BackgroundSelectEpiOffers'].show()
            self['BackgroundEpiOffers'].show()
            data = [self.episode_content_stream_index, self.episode_gui_mode, self.episode_content_list_select, offers]
            self.chooseJustWatchEpisodeContentProviderList.setList(list(map(epi_offer_entry, [data])))
            self.chooseJustWatchEpisodeContentProviderList.selectionEnabled(0)
            self['JustWatchEpisodeContentProvider'].show()
            self.episode_offers_show = True
            self.update_episode_content()

    def update_episode_offers(self):
        if self.episodes_list:
            index = self['JustWatchEpisodesGui'].getSelectionIndex()
            offers = self.episodes_list[index][5]
            data = [self.episode_content_stream_index, self.episode_gui_mode, self.episode_content_list_select, offers]
            self.chooseJustWatchEpisodeContentProviderList.setList(list(map(epi_offer_entry, [data])))
            self.chooseJustWatchEpisodeContentProviderList.selectionEnabled(0)

    def update_episode_content(self):
        if self.episodes_list:
            data = [self.episode_content_list_index, self.episode_gui_mode, self.episode_content_list_select,
                    self.episode_content_list]
            self.chooseJustWatchEpisodeContentList.setList(list(map(episode_content_entry, [data])))
            self.chooseJustWatchEpisodeContentList.selectionEnabled(0)
            self['JustWatchEpisodeContent'].show()

    def do_hide_episodes_gui(self):
        self.episodes_list_show = False
        self.doHideScrollbarEpisodes()
        self['JustWatchEpisodesGui'].hide()
        self['JustWatchEpisodeDescriptionText'].hide()

    def do_show_episodes_gui(self, data):
        self.episodes_list_show = True
        self.episodes_list = data
        if self.episodes_list:
            self.chooseJustWatchEpisodesList.setList(list(map(episodes_gui_entry, self.episodes_list)))
            self.loadScrollbarEpisodes(index=0, max_items=len(self.episodes_list), new_scall=True)
            self['JustWatchEpisodesGui'].show()
            self.updateDescription()
            self['JustWatchEpisodeDescriptionText'].show()

    def updateDescription(self):
        if self.episodes_list:
            index = self['JustWatchEpisodesGui'].getSelectionIndex()
            (title, short_title, episode_number, short_description, runtime, offers) = self.episodes_list[index]
            self['JustWatchEpisodeDescriptionText'].setText(short_description)

    def get_episodes_index(self):
        index = self['JustWatchEpisodesGui'].getSelectionIndex()
        return index

    def key_episodes_ok(self):
        if self.episodes_list and not self.episode_offers_show:
            if self.episodes_list:
                index = self['JustWatchEpisodesGui'].getSelectionIndex()
                offers = self.episodes_list[index][5]
                self.do_show_episode_offers(offers)
                return 5
        elif self.episode_gui_mode == 5:
            self.episode_content_stream_index = 0
            self.episode_content_list_select = self.episode_content_list[self.episode_content_list_index]
            config.justwatch.content_mode.value = self.episode_content_list_select
            config.justwatch.content_mode.save()
            configfile.save()
            self.update_episode_content()
            self.update_episode_offers()
            return
        return None

    def key_episodes_up(self):
        if self.episode_gui_mode >= 6:
            self.episode_content_stream_index = 0
            self.episode_gui_mode -= 1
            self.update_episode_content()
            self.update_episode_offers()
        elif self.episode_gui_mode == 5 and not self.episode_offers_show:
            self['JustWatchEpisodesGui'].up()
            index = self['JustWatchEpisodesGui'].getSelectionIndex()
            self.loadScrollbarEpisodes(index=index, max_items=len(self.episodes_list), new_scall=True)
            self.updateDescription()

    def key_episodes_down(self):
        if self.episode_gui_mode == 5 and self.episode_offers_show:
            self.episode_gui_mode += 1
            self.update_episode_content()
            self.update_episode_offers()
        elif self.episode_gui_mode == 5:
            self['JustWatchEpisodesGui'].down()
            index = self['JustWatchEpisodesGui'].getSelectionIndex()
            self.loadScrollbarEpisodes(index=index, max_items=len(self.episodes_list), new_scall=True)
            self.updateDescription()
            self.update_episode_offers()
        elif self.episode_gui_mode == 6 or self.episode_gui_mode == 7:
            self.episode_content_stream_index = 0
            self.episode_gui_mode += 1
            self.update_episode_content()
            self.update_episode_offers()

    def key_episodes_left(self):
        if self.episode_gui_mode == 5 and self.episode_offers_show:
            if self.episode_content_list_index != 0:
                self.episode_content_list_index -= 1
                self.update_episode_content()
            return
        elif self.episode_gui_mode > 5:
            return
        self['JustWatchEpisodesGui'].pageUp()
        index = self['JustWatchEpisodesGui'].getSelectionIndex()
        self.loadScrollbarEpisodes(index=index, max_items=len(self.episodes_list), new_scall=True)
        self.updateDescription()

    def key_episodes_right(self):
        if self.episode_gui_mode == 5 and self.episode_offers_show:
            if self.episode_content_list_index != 2:
                self.episode_content_list_index += 1
                self.update_episode_content()
            return
        elif self.episode_gui_mode > 5:
            return
        self['JustWatchEpisodesGui'].pageDown()
        index = self['JustWatchEpisodesGui'].getSelectionIndex()
        self.loadScrollbarEpisodes(index=index, max_items=len(self.episodes_list), new_scall=True)
        self.updateDescription()


def episodes_gui_entry(entry):
    res = [entry]
    item_text = entry[1] + entry[0]
    res.append(MultiContentEntryText(pos=(int(10 / skinFactor), int(5 / skinFactor)),
                                     size=(int(650 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=item_text))

    res.append(MultiContentEntryText(pos=(0, int(58 / skinFactor)),
                                     size=(int(1840 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0x545a5f))
    return res


def epi_offer_entry(entry):
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
    s = index if mode == 6 else 0
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

                if mode == 6 and i == 0:
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
        color = 0xcac253 if mode == 6 else 0xffffff
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
    s = index if mode == 7 else 0
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

                if mode == 7 and i == 0:
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
        color = 0xcac253 if mode == 7 else 0xffffff
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
    s = index if mode == 8 else 0
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

                if mode == 8 and i == 0:
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
        color = 0xcac253 if mode == 8 else 0xffffff
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


def episode_content_entry(entry):
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
        if x == index and mode == 5:
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
                                         backcolor=0x1a2632))
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