from Screens.Screen import Screen
import os

from Components.AVSwitch import AVSwitch
from Components.ActionMap import NumberActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.config import config
from enigma import ePicLoad, gFont, eTimer, \
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_WRAP

from .justWatch import download_file, get_poster_url, get_title
from .just_watch_spinner import JustWatchSpinner
from .__init__ import _

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
else:
    skinFactor = 1.5

TITLE_STR = _(" Title")


class JustWatchPersonSearchScreen(Screen, JustWatchSpinner):
    def __init__(self, session, data, providers, amazon, netflix):
        if DESKTOPSIZE.width() >= 1920:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1920,1080" title=" ">
                           <ePixmap name="JustWatchLogo" position="40,10" size="296,70" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_296x70.png" zPosition="1" />
                           <widget name="JustWatchActorText" position="610,10" size="700,70" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 46" valign="center" halign="center"/>
                           <!-- Description -->
                           <eLabel name="background" position="0,100" size="1920,250" backgroundColor="#001a2632" transparent="0" zPosition="1" />
                           <widget name="JustWatchDescription" position="40,100" size="1840,230" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="2" font="JW; 28" valign="center" halign="center"/>
                           <!-- Cover Gui -->
                           <widget name="JustWatchItemText" position="460,370" size="1000,42" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 28" valign="center" halign="center"/>
                           <widget name="JustWatchSelectCover" position="40,420" size="1880,670" backgroundColor="#001b1e25" zPosition="2" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchCover" position="40,420" size="1880,670" backgroundColor="#001b1e25" zPosition="3" transparent="1" enableWrapAround="1" />
                           <!-- Spinner -->
                           <widget name="BackgroundSpinner" position="460,370" size="1000,42" backgroundColor="#001b1e25" transparent="0" zPosition="98" />
                           <widget name="JustWatchSpinner" position="925,350" size="70,70" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/spinner/1.png" alphatest="blend" zPosition="99" />
                           </screen>
                        """
        else:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1280,720" title=" ">
                           <ePixmap name="JustWatchLogo" position="26,6" size="197,46" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_296x70.png" zPosition="1" />
                           <widget name="JustWatchActorText" position="406,6" size="466,46" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 30" valign="center" halign="center"/>
                           <!-- Description -->
                           <eLabel name="background" position="0,66" size="1280,166" backgroundColor="#001a2632" transparent="0" zPosition="1" />
                           <widget name="JustWatchDescription" position="26,66" size="1226,153" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="2" font="JW; 18" valign="center" halign="center"/>
                           <!-- Cover Gui -->
                           <widget name="JustWatchItemText" position="306,246" size="666,28" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 18" valign="center" halign="center"/>
                           <widget name="JustWatchSelectCover" position="26,280" size="1253,446" backgroundColor="#001b1e25" zPosition="2" transparent="1" enableWrapAround="1" />
                           <widget name="JustWatchCover" position="26,280" size="1253,446" backgroundColor="#001b1e25" zPosition="3" transparent="1" enableWrapAround="1" />
                           <!-- Spinner -->
                           <widget name="BackgroundSpinner" position="306,246" size="666,28" backgroundColor="#001b1e25" transparent="0" zPosition="98" />
                           <widget name="JustWatchSpinner" position="616,233" size="46,46" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/spinner/1.png" alphatest="blend" zPosition="99" />
                           </screen>
                        """
        Screen.__init__(self, session)

        JustWatchSpinner.__init__(self, background=True)

        self['actions'] = NumberActionMap(['JustWatch_Actions'], {'ok': self.keyOk,
                                                                  'cancel': self.keyCancel,
                                                                  'left': self.keyLeft,
                                                                  'right': self.keyRight,
                                                                  'up': self.keyUp,
                                                                  'down': self.keyDown,
                                                                  'nextBouquet': self.pageUp,
                                                                  'prevBouquet': self.pageDown
                                                                  }, -1)

        self.chooseJustWatchCoverList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchCoverList.l.setItemHeight(int(670 / skinFactor))
        self.chooseJustWatchCoverList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchCover'] = self.chooseJustWatchCoverList

        self.chooseJustWatchSelectCoverList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchSelectCoverList.l.setItemHeight(int(670 / skinFactor))
        self.chooseJustWatchSelectCoverList.l.setFont(0, gFont('JW', 0))
        self['JustWatchSelectCover'] = self.chooseJustWatchSelectCoverList

        self['JustWatchActorText'] = Label(data[0])
        description = data[2]
        self['JustWatchDescription'] = Label(description)
        self['JustWatchItemText'] = Label("")

        self.data = data[3]
        self.providers = providers

        self.setLoad = []
        self.cover_list = []
        self.download_list = []
        self.cover_gui_list = []
        self.cover_select = 0
        self.cover_index = 0

        self.providers_data = providers
        self.amazon = amazon
        self.netflix = netflix

        self.CoverTimer = eTimer()
        self.CoverTimerStatus = False
        self.CoverTimer.callback.append(self.reloadCover)

        self.onLayoutFinish.append(self.build_gui)

    def build_gui(self):
        item_text = str(self.data.get("total_results")) + TITLE_STR if self.data.get(
            "total_results") else "0" + TITLE_STR
        self['JustWatchItemText'].setText(item_text)
        for item in self.data["items"]:
            cover_destination = "%s/%s-poster.jpg" % (config.justwatch.cache_destination.value, str(item.get("id")))
            cover_size = "big" if skinFactor == 1 else "small"
            cover_url = get_poster_url(item.get("poster"), size=cover_size) if item.get(
                "poster") else None
            object_type = item.get("object_type")
            title = item.get("title") if item.get("title") else ""
            if not os.path.isfile(cover_destination):
                self.cover_list.append((cover_destination, cover_url))
            self.cover_gui_list.append((cover_destination, object_type, title))

        self.setDownloadCoverList()
        self.updateSelectCoverList()
        self.updateCoverList()

    def keyOk(self):
        item_id = self.data.get("items")[self.cover_index].get("id")
        item_content_type = self.data.get("items")[self.cover_index].get("object_type")
        if item_content_type == "movie":
            callback = self.cbReceivedMovieData
        else:
            callback = self.cbReceivedSeriesData
        self.startJustWatchSpinner()
        get_title(title_id=item_id, content_type=item_content_type, callback=callback)

    def keyCancel(self):
        self.close()

    def cbReceivedMovieData(self, movie_data):
        if movie_data:
            self.stopJustWatchSpinner()
            from .just_watch_movie import JustWatchMovieScreen
            self.session.open(JustWatchMovieScreen, movie_data, self.providers_data, self.amazon, self.netflix)

    def cbReceivedSeriesData(self, series_data):
        if series_data:
            self.stopJustWatchSpinner()
            from .just_watch_series import JustWatchSeriesScreen
            self.session.open(JustWatchSeriesScreen, series_data, self.providers_data, self.amazon, self.netflix)

    def keyLeft(self):
        if self.cover_index != 0:
            if self.cover_select != 0:
                self.cover_select -= 1
                self.cover_index -= 1
                self.updateSelectCoverList()

    def keyRight(self):
        if self.cover_index + 2 <= len(self.cover_gui_list):
            if self.cover_select < 7:
                self.cover_index += 1
                self.cover_select += 1
                self.updateSelectCoverList()

    def keyUp(self):
        if self.cover_index >= 8:
            self.cover_index -= 8
            self.updateCoverList()
            self.updateSelectCoverList()

    def keyDown(self):
        update = False
        if self.cover_index + 8 <= len(self.cover_gui_list) - 1:
            self.cover_index += 8
            update = True
        else:
            x = len(self.cover_gui_list) - (len(self.cover_gui_list) / 8 * 8)
            if x > 0:
                self.cover_index = len(self.cover_gui_list) - 1
                self.cover_select = x - 1
                update = True
        if update:
            self.updateCoverList()
            self.updateSelectCoverList()

    def pageUp(self):
        if self.cover_index + 16 <= len(self.cover_gui_list) - 1:
            self.cover_index += 16
            self.updateCoverList()

    def pageDown(self):
        if self.cover_index - 16 >= 0:
            self.cover_index -= 16
            self.updateCoverList()

    def updateSelectCoverList(self):
        data = [self.cover_select]
        self.chooseJustWatchSelectCoverList.setList(list(map(select_cover_entry, [data])))
        self.chooseJustWatchSelectCoverList.selectionEnabled(0)

    def updateCoverList(self, callback=None):
        data = [self.cover_index, self.cover_gui_list]
        self.chooseJustWatchCoverList.setList(list(map(cover_gui_entry, [data])))
        self.chooseJustWatchCoverList.selectionEnabled(0)
        self.downloadPicList()

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
                if int(start) <= self.cover_index <= int(ende):
                    self.setLoad = dataList
                    self.download_list.remove(self.download_list[x])
                x = x + 1
            if self.setLoad:
                self.CoverTimerStatus = False
                self.CoverTimer.start(300, True)
                for picSave, coverUrl in self.setLoad:
                    if not os.path.isfile(picSave):
                        if coverUrl is not None:
                            download_file(coverUrl, picSave)

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
            self.updateCoverList()
        else:
            self.CoverTimerStatus = True
            self.stopTimer()
            self.updateCoverList()


def select_cover_entry(entry):
    res = [entry]
    select = entry[0]

    w_pos = select * int(230 / skinFactor)
    res.append(MultiContentEntryText(pos=(w_pos, 0),
                                     size=(int(230 / skinFactor), int(322 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0xcac253))
    return res


def cover_gui_entry(entry):
    res = [entry]
    index = entry[0]
    data = entry[1]

    x = int(index / 8) * 8

    if len(data) - x >= 8:
        max_range = 8
    else:
        max_range = len(data) - x

    w_pos = int(5 / skinFactor)
    for i in range(max_range):
        png_destination = data[x][0]
        if os.path.isfile(png_destination):
            png = load_pic_scale(png_destination, int(220 / skinFactor), int(312 / skinFactor), "#001a2632")
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, int(5 / skinFactor),
                        int(220 / skinFactor), int(312 / skinFactor), png))
        else:
            res.append(MultiContentEntryText(pos=(w_pos, int(5 / skinFactor)),
                                             size=(int(220 / skinFactor), int(312 / skinFactor)),
                                             flags=RT_HALIGN_CENTER | RT_WRAP,
                                             font=0,
                                             text=data[x][2],
                                             color=0xffffff,
                                             backcolor=0x1a2632))
        x += 1
        w_pos = w_pos + int(230 / skinFactor)

    if len(data) - x >= 8:
        max_range = 8
    else:
        max_range = len(data) - x
    w_pos = int(5 / skinFactor)
    for i in range(max_range):
        png_destination = data[x][0]
        if os.path.isfile(png_destination):
            png = load_pic_scale(png_destination, int(220 / skinFactor), int(312 / skinFactor), "#001a2632")
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, int(327 / skinFactor),
                        int(220 / skinFactor), int(312 / skinFactor), png))
        else:
            res.append(MultiContentEntryText(pos=(w_pos, int(327 / skinFactor)),
                                             size=(int(220 / skinFactor), int(312 / skinFactor)),
                                             flags=RT_HALIGN_CENTER | RT_WRAP,
                                             font=0,
                                             text=data[x][2],
                                             color=0xffffff,
                                             backcolor=0x1a2632))
        x += 1
        w_pos = w_pos + int(230 / skinFactor)
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


def setDownloadListCover(coverList):
    downloadListe = []
    split = 24
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
            start = 0 - 16
            ende = len(data[0]) + 2
            for dataList in data:
                downloadListe.append((start, ende, dataList))
                start = start + len(dataList)
                ende = ende + len(dataList)
    else:
        x = len(coverList) - 1
        downloadListe.append((0, x, coverList))
    return downloadListe
