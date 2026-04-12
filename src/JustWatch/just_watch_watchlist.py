from os.path import isfile

from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import NumberActionMap
from Components.AVSwitch import AVSwitch
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText
from Components.config import config
from enigma import ePicLoad, gFont, eTimer, getDesktop, eListboxPythonMultiContent, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_WRAP

from .justWatch import get_watchlist, get_poster_url, download_file, get_title
from .just_watch_spinner import JustWatchSpinner
from .just_watch_movie import JustWatchMovieScreen
from .just_watch_series import JustWatchSeriesScreen

from .__init__ import _

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    BACKGROUND_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_480x50.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_100x100.png"
    SELECT_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_150x50.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_110x110.png"
    SELECT_BIG_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_250x50.png"
else:
    skinFactor = 1.5
    BACKGROUND_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_320x33.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_66x66.png"
    SELECT_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_100x33.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_73x73.png"
    SELECT_BIG_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_166x33.png"

TITLE_STR = _(" Title")
WATCHLIST_STR = _("Watchlist")

COUNTRY_DIRECTORY = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/country/"


class JustWatchWatchlist(Screen, JustWatchSpinner):
    def __init__(self, session, providers_data_gui, providers, amazon, netflix):
        if DESKTOPSIZE.width() >= 1920:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1920,1080" title="JustWatch">
                               <ePixmap name="JustWatchLogo" position="40,10" size="296,70" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_296x70.png" zPosition="1" />
                               <widget name="JustWatchHomeText" position="610,10" size="700,70" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 46" valign="center" halign="center"/>
                               <!-- Provider -->
                               <eLabel name="background" position="0,100" size="1920,250" backgroundColor="#001a2632" transparent="0" zPosition="1" />
                               <widget name="JustWatchProvider" position="40,100" size="1840,110" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
                               <!-- Content -->
                               <widget name="JustWatchContentType" position="40,225" size="480,50" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
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
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1280,720" title="JustWatch">
                               <ePixmap name="JustWatchLogo" position="26,6" size="197,46" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_197x46.png" zPosition="1" />
                               <widget name="JustWatchHomeText" position="406,6" size="466,46" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 30" valign="center" halign="center"/>
                               <!-- Provider -->
                               <eLabel name="background" position="0,66" size="1280,166" backgroundColor="#001a2632" transparent="0" zPosition="1" />
                               <widget name="JustWatchProvider" position="26,66" size="1226,73" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
                               <!-- Content -->
                               <widget name="JustWatchContentType" position="26,150" size="320,33" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
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

        self.chooseJustWatchProviderList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchProviderList.l.setItemHeight(int(110 / skinFactor))
        self['JustWatchProvider'] = self.chooseJustWatchProviderList

        self.chooseJustWatchContentTypeList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchContentTypeList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchContentTypeList.l.setItemHeight(int(50 / skinFactor))
        self['JustWatchContentType'] = self.chooseJustWatchContentTypeList

        self['JustWatchHomeText'] = Label(WATCHLIST_STR)
        self['JustWatchItemText'] = Label("")

        self.chooseJustWatchCoverList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchCoverList.l.setItemHeight(int(670 / skinFactor))
        self.chooseJustWatchCoverList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchCover'] = self.chooseJustWatchCoverList

        self.chooseJustWatchSelectCoverList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchSelectCoverList.l.setItemHeight(int(670 / skinFactor))
        self.chooseJustWatchSelectCoverList.l.setFont(0, gFont('JW', 0))
        self['JustWatchSelectCover'] = self.chooseJustWatchSelectCoverList

        self.cover_list = []
        self.setLoad = []
        self.download_list = []
        self.cover_gui_list = []
        self.providers_gui_data = providers_data_gui
        self.videos = {}
        self.video_data = []
        self.content_type_data = ["All", "Movies", "Series"]
        self.providers_gui_index = 0
        self.content_type_index = 0
        self.cover_index = 0
        self.cover_select = 0
        self.content_type = "All"
        self.gui_mode = 0

        self.providers_data = providers
        self.amazon = amazon
        self.netflix = netflix

        self.CoverTimer = eTimer()
        self.CoverTimerStatus = False
        self.CoverTimer.callback.append(self.reloadCover)

        self.onLayoutFinish.append(self.createSetup)

    def createSetup(self):
        self.updateContentTypeList()
        self.updateProviderList()
        self.startJustWatchSpinner()
        self.videos = get_watchlist()
        self.createVideoData()

    def createVideoData(self, update=None):
        if self.videos:
            for item in self.videos.get("items"):
                is_sort = False
                cover_destination = "%s/%s-poster.jpg" % (config.justwatch.cache_destination.value, str(item.get("id")))
                cover_size = "big" if skinFactor == 1 else "small"
                cover_url = get_poster_url(item.get("poster"), size=cover_size) if item.get(
                    "poster") else None
                object_type = item.get("object_type")
                title = item.get("title") if item.get("title") else ""
                sort = self.content_type_data[self.content_type_index]
                if sort == "All":
                    is_sort = True
                elif sort == "Series" and object_type == "show":
                    is_sort = True
                elif sort == "Movies" and object_type == "movie":
                    is_sort = True
                if is_sort:
                    if not isfile(cover_destination):
                        self.cover_list.append((cover_destination, cover_url))
                    self.cover_gui_list.append((cover_destination, object_type, title))
                    self.video_data.append(item)
            item_text = str(len(self.video_data)) + TITLE_STR
            self['JustWatchItemText'].setText(item_text)
            if update:
                if self.cover_index + 1 > len(self.video_data):
                    self.cover_index = len(self.video_data) - 1
                    if self.cover_select - 1 < 0:
                        self.cover_select = 7
                    else:
                        self.cover_select -= 1
        else:
            item_text = "0" + TITLE_STR
            self['JustWatchItemText'].setText(item_text)
        self.stopJustWatchSpinner()
        self.setDownloadCoverList()
        self.updateCoverList()
        self.updateSelectCoverList()

    def updateSelectCoverList(self):
        data = [self.cover_select, self.gui_mode]
        self.chooseJustWatchSelectCoverList.setList(list(map(select_cover_entry, [data])))
        self.chooseJustWatchSelectCoverList.selectionEnabled(0)

    def updateCoverList(self, callback=None):
        data = [self.cover_index, self.cover_gui_list]
        self.chooseJustWatchCoverList.setList(list(map(cover_gui_entry, [data])))
        self.chooseJustWatchCoverList.selectionEnabled(0)
        self.downloadPicList()

    def updateProviderList(self, callback=None):
        data = [self.providers_gui_index, self.providers_gui_data, self.gui_mode]
        self.chooseJustWatchProviderList.setList(list(map(provider_gui_entry, [data])))
        self.chooseJustWatchProviderList.selectionEnabled(0)

    def updateContentTypeList(self):
        data = [self.content_type_index, self.gui_mode, self.content_type, self.content_type_data]
        self.chooseJustWatchContentTypeList.setList(list(map(content_gui_entry, [data])))
        self.chooseJustWatchContentTypeList.selectionEnabled(0)

    def keyOk(self):
        if self.gui_mode == 1:
            self.content_type = self.content_type_data[self.content_type_index]
            self.updateContentTypeList()
            self.video_data = []
            self.cover_list = []
            self.download_list = []
            self.cover_gui_list = []
            self.cover_index = 0
            self.cover_select = 0
            self.createVideoData()
        elif self.gui_mode == 2:
            if self.video_data:
                item_id = self.video_data[self.cover_index].get("id")
                item_content_type = self.video_data[self.cover_index].get("object_type")
                if item_content_type == "movie":
                    callback = self.cbReceivedMovieData
                else:
                    callback = self.cbReceivedSeriesData
                self.startJustWatchSpinner()
                get_title(title_id=item_id, content_type=item_content_type, callback=callback)

    def cbReceivedMovieData(self, movie_data):
        if movie_data:
            self.stopJustWatchSpinner()
            self.session.openWithCallback(self.updateVideoGui, JustWatchMovieScreen, movie_data, self.providers_data, self.amazon, self.netflix)

    def cbReceivedSeriesData(self, series_data):
        if series_data:
            self.stopJustWatchSpinner()
            self.session.openWithCallback(self.updateVideoGui, JustWatchSeriesScreen, series_data, self.providers_data, self.amazon, self.netflix)

    def updateVideoGui(self, callback=None):
        self.video_data = []
        self.cover_list = []
        self.download_list = []
        self.cover_gui_list = []
        self.videos = get_watchlist()
        if not self.videos.get("items"):
            self.gui_mode = 1
        self.createVideoData(update=True)
        self.updateSelectCoverList()
        self.updateContentTypeList()

    def keyCancel(self):
        if self.gui_mode == 2:
            self.gui_mode = 1
            self.updateSelectCoverList()
            self.updateContentTypeList()
            return
        self.close()

    def keyLeft(self):
        if self.gui_mode == 0:
            if self.providers_gui_index != 0:
                self.providers_gui_index -= 1
                self.updateProviderList()
        elif self.gui_mode == 1:
            if self.content_type_index != 0:
                self.content_type_index -= 1
                self.updateContentTypeList()
        elif self.gui_mode == 2:
            if self.cover_index != 0:
                if self.cover_select != 0:
                    self.cover_select -= 1
                    self.cover_index -= 1
                    self.updateSelectCoverList()

    def keyRight(self):
        if self.gui_mode == 0:
            if self.providers_gui_index < len(self.providers_gui_data) - 1:
                self.providers_gui_index += 1
            else:
                self.providers_gui_index = 0
            self.updateProviderList()
        elif self.gui_mode == 1:
            if self.content_type_index < 2:
                self.content_type_index += 1
                self.updateContentTypeList()
        elif self.gui_mode == 2:
            if self.cover_index + 2 <= len(self.cover_gui_list):
                if self.cover_select < 7:
                    self.cover_index += 1
                    self.cover_select += 1
                    self.updateSelectCoverList()

    def keyUp(self):
        if self.gui_mode == 2:
            if self.cover_index < 8:
                self.gui_mode = 1
                self.updateSelectCoverList()
                self.updateContentTypeList()
            else:
                self.cover_index -= 8
                self.updateCoverList()
                self.updateSelectCoverList()
            return

        self.gui_mode -= 1
        if self.gui_mode < 1:
            self.updateProviderList()
        self.updateContentTypeList()
        self.updateSelectCoverList()

    def keyDown(self):
        if self.gui_mode == 2:
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
            return

        self.gui_mode += 1
        if self.gui_mode <= 1:
            self.updateProviderList()
        elif self.gui_mode == 2 and not self.video_data:
            self.gui_mode = 1
        self.updateContentTypeList()
        self.updateSelectCoverList()

    def pageUp(self):
        if self.gui_mode == 2:
            if self.cover_index + 16 <= len(self.cover_gui_list) - 1:
                self.cover_index += 16
                self.updateCoverList()

    def pageDown(self):
        if self.gui_mode == 2:
            if self.cover_index - 16 >= 0:
                self.cover_index -= 16
                self.updateCoverList()

    def reloadCover(self):
        if not self.CoverTimerStatus:
            self.setLoad.reverse()
            if self.setLoad:
                (cover, link) = self.setLoad[0]
                if isfile(cover):
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
                    if not isfile(picSave):
                        if coverUrl is not None:
                            download_file(coverUrl, picSave)


def select_cover_entry(entry):
    res = [entry]
    select = entry[0]
    mode = entry[1]

    if mode == 2:
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

    if data:
        x = int(index / 8) * 8

        if len(data) - x >= 8:
            max_range = 8
        else:
            max_range = len(data) - x

        w_pos = int(5 / skinFactor)
        for i in range(max_range):
            png_destination = data[x][0]
            if isfile(png_destination):
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
            if isfile(png_destination):
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


def content_gui_entry(entry):
    res = [entry]
    index = entry[0]
    mode = entry[1]
    select = entry[2]
    data = entry[3]

    x = 0
    p_size = 0
    png = LoadPixmap(BACKGROUND_CONTENT)
    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 0, 0,
                int(480 / skinFactor), int(50 / skinFactor), png))
    for i in range(3):
        item = data[i]
        if x == index and mode == 1:
            png = LoadPixmap(SELECT_CONTENT)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, p_size, 0,
                        int(150 / skinFactor), int(50 / skinFactor), png))
        color = 0xcac253 if select == item else 0x545a5f
        res.append(MultiContentEntryText(pos=(p_size + int(7 / skinFactor), int(5 / skinFactor)),
                                         size=(int(150 / skinFactor) - int(14 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER,
                                         font=0,
                                         text=_(item),
                                         color=color,
                                         backcolor=0x1a2632))
        p_size = p_size + int(165 / skinFactor)
        x += 1
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


def provider_gui_entry(entry):
    res = [entry]
    index = entry[0]
    data = entry[1]
    mode = entry[2]

    w_size = int(5 / skinFactor)
    max_range = len(data) - index
    x = index
    for i in range(max_range):
        (short_name, icon_destination) = data[x]
        if w_size > 1840:
            break
        if isfile(icon_destination):
            png = load_pic_scale(icon_destination, int(100 / skinFactor), int(100 / skinFactor), "#001a2632")
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_size, int(5 / skinFactor),
                        int(100 / skinFactor), int(100 / skinFactor), png))

            if mode == 0 and i == 0:
                w_pos = w_size - int(5 / skinFactor)
                h_pos = 0
                size = int(110 / skinFactor)
                png = LoadPixmap(SELECT_PROVIDER)
            else:
                w_pos = w_size
                h_pos = int(5 / skinFactor)
                size = int(100 / skinFactor)
                png = LoadPixmap(RADIUS_PROVIDER)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, h_pos, size, size, png))
            w_size = w_size + int(120 / skinFactor)
            x += 1

    return res


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
