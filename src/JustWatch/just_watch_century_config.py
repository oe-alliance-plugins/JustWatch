from Components.MenuList import MenuList
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText
from enigma import ePicLoad, gFont, addFont, ePythonMessagePump, eServiceReference, eTimer, gPixmapPtr,\
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP
import math
from .__init__ import _

SCROLLBARBACKCOLOR = 0x545a5f
SCROLLBARSLIDERCOLOR = 0xcac253

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_30x30.png"
else:
    skinFactor = 1.5
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_22x22.png"


class century_scroll_bar():
    def __init__(self, height_list, label_height, value):
        self.CenturyScrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.CenturyScrollbar.l.setFont(0, gFont('Regular', 1))
        self.CenturyScrollbar_value = value
        self[self.CenturyScrollbar_value] = self.CenturyScrollbar

        self.isShowCentury = False
        self.wight_century = None
        self.height_century = 1
        self.wight_century_slider = None
        self.height_century_slider = None
        self.height_century_list = height_list
        self.century_label_height = label_height
        self.century_max_label_page = None
        self.wight_century_background = None

        self.onLayoutFinish.append(self.doHideScrollbarCentury)
        self.onLayoutFinish.append(self.setSizeCentury)

    def doHideScrollbarCentury(self):
        self[self.CenturyScrollbar_value].hide()
        self.isShowCentury = False

    def doShowScrollbarCentury(self):
        self[self.CenturyScrollbar_value].show()
        self.isShowCentury = True

    def setSizeCentury(self):
        self.century_max_label_page = (self.height_century_list // self.century_label_height)
        self.wight_century_slider = int(6 / skinFactor)
        self.wight_century = int(7 / skinFactor)
        self.wight_century_background = int(2 / skinFactor)

    def loadScrollbarCentury(self, index=0, max_items=0, new_scall=None):
        if self.height_century_list and self.century_label_height and self.century_max_label_page < max_items:
            max_items_show = self.height_century_list // self.century_label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.height_century_slider = int(self.height_century_list / max_slider_pos)

            x = self.century_max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.height_century_list - self.height_century_slider
                    break
                x = x + self.century_max_label_page
                s = s + self.height_century_slider
            if not self.height_century == s or new_scall:
                self.height_century = s
                self.CenturyScrollbar.setList(list(map(self.set_scrollbar_century, [1])))
                self[self.CenturyScrollbar_value].selectionEnabled(0)
                if not self.isShowCentury:
                    self.doShowScrollbarCentury()
        else:
            if self.isShowCentury:
                self.doHideScrollbarCentury()

    def set_scrollbar_century(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.wight_century_background, self.height_century_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.wight_century, self.height_century), size=(self.wight_century_slider, self.height_century_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res


class CenturyConfig(century_scroll_bar):
    def __init__(self):
        self.chooseJustWatchCenturyConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchCenturyConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchCenturyConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchCenturyConfig'] = self.chooseJustWatchCenturyConfigList

        self['BackgroundCenturyConfig'] = Label("")

        self.century_config = None
        self.century_config_gui_list = []
        self.century_config_list_show = False
        self.century_update = False

        century_scroll_bar.__init__(self, int(660 / skinFactor), int(60 / skinFactor), "MyScrollBarCentury")

        self.onLayoutFinish.append(self.do_hide_century_config_gui)

    def do_hide_century_config_gui(self):
        self.century_config_list_show = False
        self.doHideScrollbarCentury()
        self['BackgroundCenturyConfig'].hide()
        self['JustWatchCenturyConfig'].hide()

    def do_show_century_config_gui(self, data):
        self.century_update = False
        self.century_config_list_show = True
        self.century_config_gui_list = data
        self.chooseJustWatchCenturyConfigList.setList(list(map(century_config_gui_entry, self.century_config_gui_list)))
        self.loadScrollbarCentury(index=0, max_items=len(self.century_config_gui_list), new_scall=True)
        self['BackgroundCenturyConfig'].show()
        self['JustWatchCenturyConfig'].show()

    def key_century_config_ok(self):
        if self.century_config_gui_list:
            data = []
            index = self['JustWatchCenturyConfig'].getSelectionIndex()
            x = 0
            for title, short_name, select in self.century_config_gui_list:
                if x == index:
                    if short_name == '__all__':
                        self.century_config = None
                        new_select = True
                    elif self.century_config != short_name:
                        new_select = True
                        self.century_config = short_name
                    else:
                        self.century_config = None
                        new_select = False
                else:
                    new_select = False
                if self.century_config is None and short_name == '__all__':
                    new_select = True
                data.append((title, short_name, new_select))
                x += 1
            self.century_config_gui_list = data
            self.chooseJustWatchCenturyConfigList.setList(list(map(century_config_gui_entry, self.century_config_gui_list)))
            self.century_update = True

    def key_century_config_up(self):
        self['JustWatchCenturyConfig'].up()
        index = self['JustWatchCenturyConfig'].getSelectionIndex()
        self.loadScrollbarCentury(index=index, max_items=len(self.century_config_gui_list), new_scall=True)

    def key_century_config_down(self):
        self['JustWatchCenturyConfig'].down()
        index = self['JustWatchCenturyConfig'].getSelectionIndex()
        self.loadScrollbarCentury(index=index, max_items=len(self.century_config_gui_list), new_scall=True)

    def key_century_config_left(self):
        self['JustWatchCenturyConfig'].pageUp()
        index = self['JustWatchCenturyConfig'].getSelectionIndex()
        self.loadScrollbarCentury(index=index, max_items=len(self.century_config_gui_list), new_scall=True)

    def key_century_config_right(self):
        self['JustWatchCenturyConfig'].pageDown()
        index = self['JustWatchCenturyConfig'].getSelectionIndex()
        self.loadScrollbarCentury(index=index, max_items=len(self.century_config_gui_list), new_scall=True)


def century_config_gui_entry(entry):
    res = [entry]
    # title, short_name, select
    if entry[2]:
        png = LoadPixmap(SELECT_PROVIDER)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(5 / skinFactor), int(15 / skinFactor),
                    int(30 / skinFactor), int(30 / skinFactor), png))

    res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(5 / skinFactor)),
                                     size=(int(650 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))

    return res

