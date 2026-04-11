from Components.MenuList import MenuList
from Components.AVSwitch import AVSwitch
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText
from Components.config import config, ConfigText, ConfigSubsection, configfile, ConfigPassword, ConfigYesNo, ConfigSubList
from enigma import ePicLoad, gFont, addFont, ePythonMessagePump, eServiceReference, eTimer, gPixmapPtr,\
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP
import os
import math
from .__init__ import _

SCROLLBARBACKCOLOR = 0x545a5f
SCROLLBARSLIDERCOLOR = 0xcac253

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    SELECT_COUNTRY = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_30x30.png"
else:
    skinFactor = 1.5
    SELECT_COUNTRY = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_20x20.png"

COUNTRY_STR = _("Please choose your country")


class country_scroll_bar():
    def __init__(self, height_list, label_height, value):
        self.CountryScrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.CountryScrollbar.l.setFont(0, gFont('Regular', 1))
        self.CountryScrollbar_value = value
        self[self.CountryScrollbar_value] = self.CountryScrollbar

        self.isShowCountry = False
        self.wight_country_config = None
        self.height_country_config = 1
        self.wight_country_config_slider = None
        self.height_country_config_slider = None
        self.height_country_config_list = height_list
        self.country_config_label_height = label_height
        self.country_config_max_label_page = None
        self.wight_country_config_background = None

        self.onLayoutFinish.append(self.doHideScrollbarCountryConfig)
        self.onLayoutFinish.append(self.setSizeCountryConfig)

    def doHideScrollbarCountryConfig(self):
        self[self.CountryScrollbar_value].hide()
        self.isShowCountry = False

    def doShowScrollbarCountryConfig(self):
        self[self.CountryScrollbar_value].show()
        self.isShowCountry = True

    def setSizeCountryConfig(self):
        self.country_config_max_label_page = (self.height_country_config_list // self.country_config_label_height)
        self.wight_country_config_slider = int(6 / skinFactor)
        self.wight_country_config = int(7 / skinFactor)
        self.wight_country_config_background = int(2 / skinFactor)

    def loadScrollbarCountryConfig(self, index=0, max_items=0, new_scall=None):
        if self.height_country_config_list and self.country_config_label_height and self.country_config_max_label_page < max_items:
            max_items_show = self.height_country_config_list // self.country_config_label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.height_country_config_slider = int(self.height_country_config_list / max_slider_pos)

            x = self.country_config_max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.height_country_config_list - self.height_country_config_slider
                    break
                x = x + self.country_config_max_label_page
                s = s + self.height_country_config_slider
            if not self.height_country_config == s or new_scall:
                self.height_country_config = s
                self.CountryScrollbar.setList(list(map(self.set_scrollbar_country_config, [1])))
                self[self.CountryScrollbar_value].selectionEnabled(0)
                if not self.isShowCountry:
                    self.doShowScrollbarCountryConfig()
        else:
            if self.isShowCountry:
                self.doHideScrollbarCountryConfig()

    def set_scrollbar_country_config(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.wight_country_config_background, self.height_country_config_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.wight_country_config, self.height_country_config), size=(self.wight_country_config_slider, self.height_country_config_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res


class CountryConfig(country_scroll_bar):
    def __init__(self):
        self.chooseJustWatchCountryConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchCountryConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchCountryConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchCountryConfig'] = self.chooseJustWatchCountryConfigList

        self['BackgroundCountryConfig'] = Label("")
        self['CountryText'] = Label(COUNTRY_STR)

        self.country_config = None
        self.country_config_gui_list = []
        self.country_config_list_show = False
        self.country_config_update = False

        country_scroll_bar.__init__(self, int(960 / skinFactor), int(60 / skinFactor), "MyScrollbarCountryConfig")

        self.onLayoutFinish.append(self.do_hide_country_config_gui)

    def do_hide_country_config_gui(self):
        self.country_config_list_show = False
        self.doHideScrollbarCountryConfig()
        self['BackgroundCountryConfig'].hide()
        self['JustWatchCountryConfig'].hide()
        self['CountryText'].hide()

    def do_show_country_config_gui(self, data, index):
        self.country_config_update = False
        self.country_config_list_show = True
        self.country_config_gui_list = data
        self.chooseJustWatchCountryConfigList.setList(list(map(country_config_gui_entry, self.country_config_gui_list)))
        self.chooseJustWatchCountryConfigList.moveToIndex(index)
        self.loadScrollbarCountryConfig(index=index, max_items=len(self.country_config_gui_list), new_scall=True)
        self['BackgroundCountryConfig'].show()
        self['JustWatchCountryConfig'].show()
        self['CountryText'].show()

    def key_country_config_ok(self):
        if self.country_config_gui_list:
            data = []
            self.country_config_update = True
            index = self['JustWatchCountryConfig'].getSelectionIndex()
            x = 0
            for title, iso, full_locale, country_png_destination, select in self.country_config_gui_list:
                new_select = True if x == index else False
                if new_select:
                    config.justwatch.locale.value = full_locale
                    config.justwatch.locale.save()
                    configfile.save()
                data.append((title, iso, full_locale, country_png_destination, new_select))
                x += 1
            self.country_config_gui_list = data
            self.chooseJustWatchCountryConfigList.setList(list(map(country_config_gui_entry, self.country_config_gui_list)))
            self.loadScrollbarCountryConfig(index=index, max_items=len(self.country_config_gui_list), new_scall=True)

    def key_country_config_up(self):
        self['JustWatchCountryConfig'].up()
        index = self['JustWatchCountryConfig'].getSelectionIndex()
        self.loadScrollbarCountryConfig(index=index, max_items=len(self.country_config_gui_list), new_scall=True)

    def key_country_config_down(self):
        self['JustWatchCountryConfig'].down()
        index = self['JustWatchCountryConfig'].getSelectionIndex()
        self.loadScrollbarCountryConfig(index=index, max_items=len(self.country_config_gui_list), new_scall=True)

    def key_country_config_left(self):
        self['JustWatchCountryConfig'].pageUp()
        index = self['JustWatchCountryConfig'].getSelectionIndex()
        self.loadScrollbarCountryConfig(index=index, max_items=len(self.country_config_gui_list), new_scall=True)

    def key_country_config_right(self):
        self['JustWatchCountryConfig'].pageDown()
        index = self['JustWatchCountryConfig'].getSelectionIndex()
        self.loadScrollbarCountryConfig(index=index, max_items=len(self.country_config_gui_list), new_scall=True)


def country_config_gui_entry(entry):
    res = [entry]
    # select icon
    if entry[4]:
        png = LoadPixmap(SELECT_COUNTRY)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(5 / skinFactor), int(15 / skinFactor),
                    int(30 / skinFactor), int(30 / skinFactor), png))
    # country icon
    if os.path.isfile(entry[3]):
        color = "#001a2632" if not entry[4] else "#001b1e25"
        png = load_pic_scale(entry[3], int(60 / skinFactor), int(30 / skinFactor), color)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(45 / skinFactor), int(15 / skinFactor),
                    int(60 / skinFactor), int(30 / skinFactor), png))

    res.append(MultiContentEntryText(pos=(int(120 / skinFactor), int(5 / skinFactor)),
                                     size=(int(575 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))

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
