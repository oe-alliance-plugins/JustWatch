from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText
from enigma import gFont, getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, \
    RT_VALIGN_CENTER
import os
import math
from .__init__ import _

SCROLLBARBACKCOLOR = 0x545a5f
SCROLLBARSLIDERCOLOR = 0xcac253

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    COUNTRY_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/country_30x30.png"
    CACHE_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/cache_30x30.png"
    PROVIDER_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/provider_30x30.png"
else:
    skinFactor = 1.5
    COUNTRY_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/country_20x20.png"
    CACHE_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/cache_20x20.png"
    PROVIDER_PNG = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/provider_20x20.png"


SETTINGS_LIST = [(_("Country-Settings"), COUNTRY_PNG, "country"),
                 (_("Provider-Settings"), PROVIDER_PNG, "provider"),
                 (_("Cache-Settings"), CACHE_PNG, "cache")]
SETTINGS_STR = _("Settings")


class config_scroll_bar():
    def __init__(self, height_list, label_height, value):
        self.ConfigScrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.ConfigScrollbar.l.setFont(0, gFont('Regular', 1))
        self.ConfigScrollbar_value = value
        self[self.ConfigScrollbar_value] = self.ConfigScrollbar

        self.isShowConfig = False
        self.wight_config = None
        self.height_config = 1
        self.wight_config_slider = None
        self.height_config_slider = None
        self.height_config_list = height_list
        self.config_label_height = label_height
        self.config_max_label_page = None
        self.wight_config_background = None

        self.onLayoutFinish.append(self.doHideScrollbarConfig)
        self.onLayoutFinish.append(self.setSizeConfig)

    def doHideScrollbarConfig(self):
        self[self.ConfigScrollbar_value].hide()
        self.isShowConfig = False

    def doShowScrollbarConfig(self):
        self[self.ConfigScrollbar_value].show()
        self.isShowConfig = True

    def setSizeConfig(self):
        self.config_max_label_page = (self.height_config_list // self.config_label_height)
        self.wight_config_slider = int(6 / skinFactor)
        self.wight_config = int(7 / skinFactor)
        self.wight_config_background = int(2 / skinFactor)

    def loadScrollbarConfig(self, index=0, max_items=0, new_scall=None):
        if self.height_config_list and self.config_label_height and self.config_max_label_page < max_items:
            max_items_show = self.height_config_list // self.config_label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.height_config_slider = int(self.height_config_list / max_slider_pos)

            x = self.config_max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.height_config_list - self.height_config_slider
                    break
                x = x + self.config_max_label_page
                s = s + self.height_config_slider
            if not self.height_config == s or new_scall:
                self.height_config = s
                self.ConfigScrollbar.setList(list(map(self.set_scrollbar_config, [1])))
                self[self.ConfigScrollbar_value].selectionEnabled(0)
                if not self.isShowConfig:
                    self.doShowScrollbarConfig()
        else:
            if self.isShowConfig:
                self.doHideScrollbarConfig()

    def set_scrollbar_config(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.wight_config_background, self.height_config_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.wight_config, self.height_config), size=(self.wight_config_slider, self.height_config_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res


class SettingsConfig(config_scroll_bar):
    def __init__(self):
        self.chooseJustWatchSettingsConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchSettingsConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchSettingsConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchSettingsConfig'] = self.chooseJustWatchSettingsConfigList

        self['BackgroundSettingsConfig'] = Label("")
        self['SettingsText'] = Label(SETTINGS_STR)

        self.settings_config = None
        self.settings_config_gui_list = SETTINGS_LIST
        self.settings_config_list_show = False

        config_scroll_bar.__init__(self, int(960 / skinFactor), int(60 / skinFactor), "MyScrollbarConfig")

        self.onLayoutFinish.append(self.do_hide_settings_config_gui)

    def do_hide_settings_config_gui(self):
        self.settings_config_list_show = False
        self.doHideScrollbarConfig()
        self['BackgroundSettingsConfig'].hide()
        self['JustWatchSettingsConfig'].hide()
        self['SettingsText'].hide()

    def do_show_settings_config_gui(self):
        self.settings_config_list_show = True
        self.chooseJustWatchSettingsConfigList.setList(list(map(settings_config_gui_entry, self.settings_config_gui_list)))
        self.loadScrollbarConfig(index=0, max_items=len(self.settings_config_gui_list), new_scall=True)
        self['BackgroundSettingsConfig'].show()
        self['JustWatchSettingsConfig'].show()
        self['SettingsText'].show()

    def key_settings_config_ok(self):
        if self.settings_config_gui_list:
            index = self['JustWatchSettingsConfig'].getSelectionIndex()
            (country, icon, mode) = self.settings_config_gui_list[index]
            return mode

    def key_settings_config_up(self):
        self['JustWatchSettingsConfig'].up()
        index = self['JustWatchSettingsConfig'].getSelectionIndex()
        self.loadScrollbarConfig(index=index, max_items=len(self.settings_config_gui_list), new_scall=True)

    def key_settings_config_down(self):
        self['JustWatchSettingsConfig'].down()
        index = self['JustWatchSettingsConfig'].getSelectionIndex()
        self.loadScrollbarConfig(index=index, max_items=len(self.settings_config_gui_list), new_scall=True)

    def key_settings_config_left(self):
        self['JustWatchSettingsConfig'].pageUp()
        index = self['JustWatchSettingsConfig'].getSelectionIndex()
        self.loadScrollbarConfig(index=index, max_items=len(self.settings_config_gui_list), new_scall=True)

    def key_settings_config_right(self):
        self['JustWatchSettingsConfig'].pageDown()
        index = self['JustWatchSettingsConfig'].getSelectionIndex()
        self.loadScrollbarConfig(index=index, max_items=len(self.settings_config_gui_list), new_scall=True)


def settings_config_gui_entry(entry):
    res = [entry]
    # title, png

    if os.path.isfile(entry[1]):
        png = LoadPixmap(entry[1])
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(5 / skinFactor), int(15 / skinFactor),
                    int(30 / skinFactor), int(30 / skinFactor), png))

    res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(5 / skinFactor)),
                                     size=(int(650 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))

    return res
