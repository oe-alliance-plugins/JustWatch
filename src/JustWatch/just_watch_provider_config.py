from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
from Components.AVSwitch import AVSwitch
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText
from enigma import ePicLoad, gFont, getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_VALIGN_CENTER
import os
import math

from .__init__ import _

SCROLLBARBACKCOLOR = 0x545a5f
SCROLLBARSLIDERCOLOR = 0xcac253

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_50x50.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_30x30.png"
else:
    skinFactor = 1.5
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_33x33.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_20x20.png"


PROVIDER_CONFIG_STR = _("My streaming providers")


class provider_scroll_bar():
    def __init__(self, height_list, label_height, value):
        self.ProviderScrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.ProviderScrollbar.l.setFont(0, gFont('Regular', 1))
        self.ProviderScrollbar_value = value
        self[self.ProviderScrollbar_value] = self.ProviderScrollbar

        self.isProviderShow = False
        self.provider_wight = None
        self.provider_height = 1
        self.provider_wight_slider = None
        self.provider_height_slider = None
        self.provider_height_list = height_list
        self.provider_label_height = label_height
        self.provider_max_label_page = None
        self.provider_wight_background = None

        self.onLayoutFinish.append(self.doHideProviderScrollbar)
        self.onLayoutFinish.append(self.setProviderSize)

    def doHideProviderScrollbar(self):
        self[self.ProviderScrollbar_value].hide()
        self.isProviderShow = False

    def doShowProviderScrollbar(self):
        self[self.ProviderScrollbar_value].show()
        self.isProviderShow = True

    def setProviderSize(self):
        self.provider_max_label_page = (self.provider_height_list // self.provider_label_height)
        self.provider_wight_slider = int(6 / skinFactor)
        self.provider_wight = int(7 / skinFactor)
        self.provider_wight_background = int(2 / skinFactor)

    def loadProviderScrollbar(self, index=0, max_items=0, new_scall=None):
        if self.provider_height_list and self.provider_label_height and self.provider_max_label_page < max_items:
            max_items_show = self.provider_height_list // self.provider_label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.provider_height_slider = int(self.provider_height_list / max_slider_pos)

            x = self.provider_max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.provider_height_list - self.provider_height_slider
                    break
                x = x + self.provider_max_label_page
                s = s + self.provider_height_slider
            if not self.provider_height == s or new_scall:
                self.provider_height = s
                self.ProviderScrollbar.setList(list(map(self.set_provider_scrollbar, [1])))
                self[self.ProviderScrollbar_value].selectionEnabled(0)
                if not self.isProviderShow:
                    self.doShowProviderScrollbar()
        else:
            if self.isProviderShow:
                self.doHideProviderScrollbar()

    def set_provider_scrollbar(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.provider_wight_background, self.provider_height_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.provider_wight, self.provider_height), size=(self.provider_wight_slider, self.provider_height_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res


class ProviderConfig(provider_scroll_bar):
    def __init__(self):
        self.chooseJustWatchProviderConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchProviderConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchProviderConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchProviderConfig'] = self.chooseJustWatchProviderConfigList

        self['BackgroundProviderConfig'] = Label("")
        self['ProviderConfigText'] = Label(PROVIDER_CONFIG_STR)

        self.provider_config_list = []
        self.provider_config_list_show = False
        self.provider_update = False
        self.no_provider_select = False

        provider_scroll_bar.__init__(self, int(960 / skinFactor), int(60 / skinFactor), "MyScrollBarProvider")

        self.onLayoutFinish.append(self.do_hide_provider_config_gui)

    def do_hide_provider_config_gui(self):
        self.provider_config_list_show = False
        self.doHideProviderScrollbar()
        self['ProviderConfigText'].hide()
        self['BackgroundProviderConfig'].hide()
        self['JustWatchProviderConfig'].hide()

    def do_show_provider_config_gui(self, data):
        self.provider_update = False
        self.provider_config_list_show = True
        self.provider_config_list = data
        self.chooseJustWatchProviderConfigList.setList(list(map(provider_config_gui_entry, self.provider_config_list)))
        self.loadProviderScrollbar(index=0, max_items=len(self.provider_config_list), new_scall=True)
        self['ProviderConfigText'].show()
        self['BackgroundProviderConfig'].show()
        self['JustWatchProviderConfig'].show()

    def key_provider_config_ok(self):
        if self.provider_config_list:
            index = self['JustWatchProviderConfig'].getSelectionIndex()
            (title, short_name, sort_index, icon_destination, select) = self.provider_config_list[index]
            self.provider_config_list.remove(self.provider_config_list[index])
            if select:
                new_select = False
            else:
                new_select = True
            self.provider_config_list.insert(index, (title, short_name, sort_index, icon_destination, new_select))
            self.chooseJustWatchProviderConfigList.setList(list(map(provider_config_gui_entry, self.provider_config_list)))
            self.provider_update = True

    def key_provider_config_up(self):
        self['JustWatchProviderConfig'].up()
        index = self['JustWatchProviderConfig'].getSelectionIndex()
        self.loadProviderScrollbar(index=index, max_items=len(self.provider_config_list), new_scall=True)

    def key_provider_config_down(self):
        self['JustWatchProviderConfig'].down()
        index = self['JustWatchProviderConfig'].getSelectionIndex()
        self.loadProviderScrollbar(index=index, max_items=len(self.provider_config_list), new_scall=True)

    def key_provider_config_left(self):
        self['JustWatchProviderConfig'].pageUp()
        index = self['JustWatchProviderConfig'].getSelectionIndex()
        self.loadProviderScrollbar(index=index, max_items=len(self.provider_config_list), new_scall=True)

    def key_provider_config_right(self):
        self['JustWatchProviderConfig'].pageDown()
        index = self['JustWatchProviderConfig'].getSelectionIndex()
        self.loadProviderScrollbar(index=index, max_items=len(self.provider_config_list), new_scall=True)


def provider_config_gui_entry(entry):
    res = [entry]
    # title, short_name, sort_index, icon_destination, select
    if entry[4]:
        png = LoadPixmap(SELECT_PROVIDER)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(5 / skinFactor), int(15 / skinFactor),
                    int(30 / skinFactor), int(30 / skinFactor), png))
    if os.path.isfile(entry[3]):
        png = load_pic_scale(entry[3], int(50 / skinFactor), int(50 / skinFactor), "#ff000000")
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(50 / skinFactor), int(5 / skinFactor),
                    int(50 / skinFactor), int(50 / skinFactor), png))
        png = LoadPixmap(RADIUS_PROVIDER)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(50 / skinFactor), int(5 / skinFactor),
                    int(50 / skinFactor), int(50 / skinFactor), png))

    res.append(MultiContentEntryText(pos=(int(110 / skinFactor), int(5 / skinFactor)),
                                     size=(int(590 / skinFactor), int(50 / skinFactor)),
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
        if ptr is not None:
            del picload
            return ptr
