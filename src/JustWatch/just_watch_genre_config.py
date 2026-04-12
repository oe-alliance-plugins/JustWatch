from Components.MenuList import MenuList
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText
from enigma import gFont, getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_VALIGN_CENTER
import math

SCROLLBARBACKCOLOR = 0x545a5f
SCROLLBARSLIDERCOLOR = 0xcac253

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_30x30.png"
else:
    skinFactor = 1.5
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_select_22x22.png"


class genre_scroll_bar():
    def __init__(self, height_list, label_height, value):
        self.GenreScrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.GenreScrollbar.l.setFont(0, gFont('Regular', 1))
        self.GenreScrollbar_value = value
        self[self.GenreScrollbar_value] = self.GenreScrollbar

        self.isShowGenre = False
        self.wight_genre = None
        self.height_genre = 1
        self.wight_genre_slider = None
        self.height_genre_slider = None
        self.height_genre_list = height_list
        self.genre_label_height = label_height
        self.genre_max_label_page = None
        self.wight_genre_background = None

        self.onLayoutFinish.append(self.doHideScrollbarGenre)
        self.onLayoutFinish.append(self.setSizeGenre)

    def doHideScrollbarGenre(self):
        self[self.GenreScrollbar_value].hide()
        self.isShowGenre = False

    def doShowScrollbarGenre(self):
        self[self.GenreScrollbar_value].show()
        self.isShowGenre = True

    def setSizeGenre(self):
        self.genre_max_label_page = (self.height_genre_list // self.genre_label_height)
        self.wight_genre_slider = int(6 / skinFactor)
        self.wight_genre = int(7 / skinFactor)
        self.wight_genre_background = int(2 / skinFactor)

    def loadScrollbarGenre(self, index=0, max_items=0, new_scall=None):
        if self.height_genre_list and self.genre_label_height and self.genre_max_label_page < max_items:
            max_items_show = self.height_genre_list // self.genre_label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.height_genre_slider = int(self.height_genre_list / max_slider_pos)

            x = self.genre_max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.height_genre_list - self.height_genre_slider
                    break
                x = x + self.genre_max_label_page
                s = s + self.height_genre_slider
            if not self.height_genre == s or new_scall:
                self.height_genre = s
                self.GenreScrollbar.setList(list(map(self.set_scrollbar_genre, [1])))
                self[self.GenreScrollbar_value].selectionEnabled(0)
                if not self.isShowGenre:
                    self.doShowScrollbarGenre()
        else:
            if self.isShowGenre:
                self.doHideScrollbarGenre()

    def set_scrollbar_genre(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.wight_genre_background, self.height_genre_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.wight_genre, self.height_genre), size=(self.wight_genre_slider, self.height_genre_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res


class GenreConfig(genre_scroll_bar):
    def __init__(self):
        self.chooseJustWatchGenreConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchGenreConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchGenreConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchGenreConfig'] = self.chooseJustWatchGenreConfigList

        self['BackgroundGenreConfig'] = Label("")

        self.genre_config_list = []
        self.genre_config_gui_list = []
        self.genre_config_list_show = False
        self.genre_update = False

        genre_scroll_bar.__init__(self, int(660 / skinFactor), int(60 / skinFactor), "MyScrollBarGenre")

        self.onLayoutFinish.append(self.do_hide_genre_config_gui)

    def do_hide_genre_config_gui(self):
        self.genre_config_list_show = False
        self.doHideScrollbarGenre()
        self['BackgroundGenreConfig'].hide()
        self['JustWatchGenreConfig'].hide()

    def do_show_genre_config_gui(self, data):
        self.genre_update = False
        self.genre_config_list_show = True
        self.genre_config_gui_list = data
        self.chooseJustWatchGenreConfigList.setList(list(map(genre_config_gui_entry, self.genre_config_gui_list)))
        self.loadScrollbarGenre(index=0, max_items=len(self.genre_config_gui_list), new_scall=True)
        self['BackgroundGenreConfig'].show()
        self['JustWatchGenreConfig'].show()

    def key_genre_config_ok(self):
        if self.genre_config_gui_list:
            index = self['JustWatchGenreConfig'].getSelectionIndex()
            (title, short_name, sort_index, select) = self.genre_config_gui_list[index]
            data = []
            if short_name == '__all__':
                self.genre_config_list = []
                for row_title, row_short_name, row_sort_index, row_select in self.genre_config_gui_list:
                    data.append((row_title, row_short_name, row_sort_index, row_short_name == '__all__'))
            else:
                if short_name in self.genre_config_list:
                    self.genre_config_list.remove(short_name)
                else:
                    self.genre_config_list.append(short_name)
                self.genre_config_list = [x for x in self.genre_config_list if x != '__all__']
                for row_title, row_short_name, row_sort_index, row_select in self.genre_config_gui_list:
                    if row_short_name == '__all__':
                        row_selected = not self.genre_config_list
                    else:
                        row_selected = row_short_name in self.genre_config_list
                    data.append((row_title, row_short_name, row_sort_index, row_selected))
            self.genre_config_gui_list = data
            self.chooseJustWatchGenreConfigList.setList(list(map(genre_config_gui_entry, self.genre_config_gui_list)))
            self.genre_update = True

    def key_genre_config_up(self):
        self['JustWatchGenreConfig'].up()
        index = self['JustWatchGenreConfig'].getSelectionIndex()
        self.loadScrollbarGenre(index=index, max_items=len(self.genre_config_gui_list), new_scall=True)

    def key_genre_config_down(self):
        self['JustWatchGenreConfig'].down()
        index = self['JustWatchGenreConfig'].getSelectionIndex()
        self.loadScrollbarGenre(index=index, max_items=len(self.genre_config_gui_list), new_scall=True)

    def key_genre_config_left(self):
        self['JustWatchGenreConfig'].pageUp()
        index = self['JustWatchGenreConfig'].getSelectionIndex()
        self.loadScrollbarGenre(index=index, max_items=len(self.genre_config_gui_list), new_scall=True)

    def key_genre_config_right(self):
        self['JustWatchGenreConfig'].pageDown()
        index = self['JustWatchGenreConfig'].getSelectionIndex()
        self.loadScrollbarGenre(index=index, max_items=len(self.genre_config_gui_list), new_scall=True)


def genre_config_gui_entry(entry):
    res = [entry]
    # title, short_name, sort_index, select
    if entry[3]:
        png = LoadPixmap(SELECT_PROVIDER)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(5 / skinFactor), int(15 / skinFactor),
                    int(30 / skinFactor), int(30 / skinFactor), png))

    res.append(MultiContentEntryText(pos=(int(45 / skinFactor), int(5 / skinFactor)),
                                     size=(int(650 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))

    return res
