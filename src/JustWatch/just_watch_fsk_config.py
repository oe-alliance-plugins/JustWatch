from Components.MenuList import MenuList
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText
from enigma import ePicLoad, gFont, addFont, ePythonMessagePump, eServiceReference, eTimer, gPixmapPtr,\
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP


DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_30x30.png"
else:
    skinFactor = 1.5
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_22x22.png"


class FskConfig:
    def __init__(self):
        self.chooseJustWatchFskConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchFskConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchFskConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchFskConfig'] = self.chooseJustWatchFskConfigList
        self['BackgroundFskConfig'] = Label("")

        self.fsk_config_list = []
        self.fsk_config_gui_list = []
        self.fsk_config_list_show = False
        self.fsk_update = False

        self.onLayoutFinish.append(self.do_hide_fsk_config_gui)

    def do_hide_fsk_config_gui(self):
        self.fsk_config_list_show = False
        self['BackgroundFskConfig'].hide()
        self['JustWatchFskConfig'].hide()

    def do_show_fsk_config_gui(self, data):
        self.fsk_config_list_show = True
        self.fsk_update = False
        self.fsk_config_gui_list = data
        self.chooseJustWatchFskConfigList.setList(list(map(fsk_config_gui_entry, self.fsk_config_gui_list)))
        self['BackgroundFskConfig'].show()
        self['JustWatchFskConfig'].show()

    def key_fsk_config_ok(self):
        if self.fsk_config_gui_list:
            index = self['JustWatchFskConfig'].getSelectionIndex()
            (title, technical_name, sort_index, select) = self.fsk_config_gui_list[index]

            data = []
            if technical_name == '__all__':
                self.fsk_config_list = []
                for row_title, row_technical_name, row_sort_index, row_select in self.fsk_config_gui_list:
                    data.append((row_title, row_technical_name, row_sort_index, row_technical_name == '__all__'))
            else:
                if technical_name in self.fsk_config_list:
                    self.fsk_config_list.remove(technical_name)
                else:
                    self.fsk_config_list = [x for x in self.fsk_config_list if x != '__all__']
                    self.fsk_config_list.append(technical_name)

                for row_title, row_technical_name, row_sort_index, row_select in self.fsk_config_gui_list:
                    if row_technical_name == '__all__':
                        row_selected = not self.fsk_config_list
                    else:
                        row_selected = row_technical_name in self.fsk_config_list
                    data.append((row_title, row_technical_name, row_sort_index, row_selected))

            self.fsk_config_gui_list = data
            self.chooseJustWatchFskConfigList.setList(list(map(fsk_config_gui_entry, self.fsk_config_gui_list)))
            self.fsk_update = True

    def key_fsk_config_up(self):
        self['JustWatchFskConfig'].up()

    def key_fsk_config_down(self):
        self['JustWatchFskConfig'].down()

    def key_fsk_config_left(self):
        self['JustWatchFskConfig'].pageUp()

    def key_fsk_config_right(self):
        self['JustWatchFskConfig'].pageDown()


def fsk_config_gui_entry(entry):
    res = [entry]
    # title, technical_name, sort_index, select
    if entry[3]:
        png = LoadPixmap(SELECT_PROVIDER)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(5 / skinFactor), int(15 / skinFactor),
                    int(30 / skinFactor), int(30 / skinFactor), png))

    res.append(MultiContentEntryText(pos=(int(50 / skinFactor), int(5 / skinFactor)),
                                     size=(int(290 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))

    return res

