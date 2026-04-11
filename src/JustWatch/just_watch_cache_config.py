from Screens.Screen import Screen
import os
import re
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.config import config, configfile
from Screens.Screen import Screen
from Components.FileList import FileList, FileEntryComponent
from enigma import ePicLoad, gFont, eServiceReference, gPixmapPtr, \
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_WRAP, RT_HALIGN_RIGHT

from .__init__ import _

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
else:
    skinFactor = 1.5


class JustWatchCacheScreen(Screen):
    def __init__(self, session):
        if DESKTOPSIZE.width() >= 1920:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1920,1080" title="JustWatch">
                           <ePixmap name="JustWatchLogo" position="40,10" size="296,70" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_296x70.png" zPosition="1" />  
                           <widget name="JustWatchConfig" position="40,100" size="1840,180" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchFolder" position="40,310" size="1840,750" itemHeight="50" scrollbarMode="showOnDemand" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           </screen>          
                        """
        else:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1280,720" title="JustWatch">
                           <ePixmap name="JustWatchLogo" position="26,6" size="197,46" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_197x46.png" zPosition="1" />
                           <widget name="JustWatchConfig" position="26,66" size="1226,120" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           <widget name="JustWatchFolder" position="26,206" size="1226,495" itemHeight="33" scrollbarMode="showOnDemand" backgroundColorSelected="#001a2632" foregroundColorSelected="#00cac253" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="1" transparent="0" enableWrapAround="1" />
                           </screen>          
                        """
        Screen.__init__(self, session)

        self['actions'] = NumberActionMap(['JustWatchFolder_Actions'], {'ok': self.keyOk,
                                                                        'cancel': self.keyCancel,
                                                                        'left': self.keyLeft,
                                                                        'right': self.keyRight,
                                                                        'up': self.keyUp,
                                                                        'down': self.keyDown,
                                                                        'OKLong': self.okLongClicked
                                                                        }, -1)

        self.chooseJustWatchConfigList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchConfigList.l.setItemHeight(int(60 / skinFactor))
        self.chooseJustWatchConfigList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchConfig'] = self.chooseJustWatchConfigList

        self['JustWatchFolder'] = FileList("/", inhibitMounts=False, inhibitDirs=False, showMountpoints=False,
                                           showFiles=False)
        self['JustWatchFolder'].hide()
        self.config_list = []
        self.folder_list = []

        self.gui_mode = 0

        self.onLayoutFinish.append(self.create_setup)

    def create_setup(self):
        self.config_list = [
            (_("Clear cache on exit"), config.justwatch.cache_clear.value, config.justwatch.cache_clear, "yes-no"),
            (_("Cache directory"), config.justwatch.cache_destination.value, config.justwatch.cache_destination,
             "destination"),
            (_("Clear cache"), get_cache_info(config.justwatch.cache_destination.value), None, "clear")]
        self.chooseJustWatchConfigList.setList(list(map(config_gui_entry, self.config_list)))

    def okLongClicked(self):
        if self.gui_mode == 1:
            currFolder = self['JustWatchFolder'].getSelection()[0]
            message = _("Create cache folder on ") + currFolder + " ?"
            self.session.openWithCallback(self.createCacheDirectory, MessageBox, message,
                                          MessageBox.TYPE_YESNO, default=True)

    def createCacheDirectory(self, answer):
        if answer:
            currFolder = self['JustWatchFolder'].getSelection()[0] + "JustWatch"
            config.justwatch.cache_destination.value = currFolder
            config.justwatch.cache_destination.save()
            configfile.save()
            message = _("New folder saved!")
            if not os.path.isdir(config.justwatch.cache_destination.value):
                os.system("mkdir %s" % config.justwatch.cache_destination.value)
            if not os.path.isdir("%s/provider" % config.justwatch.cache_destination.value):
                os.system("mkdir %s" % "%s/provider" % config.justwatch.cache_destination.value)
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)
            self.create_setup()

    def keyOk(self):
        if self.gui_mode == 0:
            mode = self['JustWatchConfig'].getCurrent()[0][3]
            if mode == "clear":
                self.session.openWithCallback(self.clear, MessageBox, _("Do you want to clear cache?"),
                                              MessageBox.TYPE_YESNO, default=True)
            elif mode == "yes-no":
                self.switchValue(self['JustWatchConfig'].getCurrent()[0][2])
            elif mode == "destination":
                self.gui_mode = 1
                self.chooseJustWatchConfigList.selectionEnabled(0)
                self['JustWatchFolder'].show()
        elif self.gui_mode == 1:
            if self['JustWatchFolder'].canDescent():
                self['JustWatchFolder'].descent()

    def clear(self, answer):
        if answer:
            os.system("rm %s/*.jpg" % config.justwatch.cache_destination.value)
            self.create_setup()

    def keyCancel(self):
        if self.gui_mode == 1:
            self.gui_mode = 0
            self.chooseJustWatchConfigList.selectionEnabled(1)
            self['JustWatchFolder'].hide()
            return
        self.close()

    def switchValue(self, conf_value):
        conf_value.value = False if conf_value.value else True
        conf_value.save()
        configfile.save()
        self.create_setup()

    def keyLeft(self):
        if self.gui_mode == 0:
            mode = self['JustWatchConfig'].getCurrent()[0][3]
            if mode == "yes-no":
                self.switchValue(self['JustWatchConfig'].getCurrent()[0][2])
        elif self.gui_mode == 1:
            self['JustWatchFolder'].pageUp()

    def keyRight(self):
        if self.gui_mode == 0:
            mode = self['JustWatchConfig'].getCurrent()[0][3]
            if mode == "yes-no":
                self.switchValue(self['JustWatchConfig'].getCurrent()[0][2])
        elif self.gui_mode == 1:
            self['JustWatchFolder'].pageDown()

    def keyUp(self):
        if self.gui_mode == 0:
            self['JustWatchConfig'].up()
        elif self.gui_mode == 1:
            self['JustWatchFolder'].up()

    def keyDown(self):
        if self.gui_mode == 0:
            self['JustWatchConfig'].down()
        elif self.gui_mode == 1:
            self['JustWatchFolder'].down()


def folder_gui_entry(entry):
    res = [entry]
    res.append(MultiContentEntryText(pos=(int(10 / skinFactor), int(5 / skinFactor)),
                                     size=(int(1820 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))

    res.append(MultiContentEntryText(pos=(0, int(58 / skinFactor)),
                                     size=(int(1840 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0x545a5f))

    return res


def config_gui_entry(entry):
    res = [entry]
    res.append(MultiContentEntryText(pos=(int(10 / skinFactor), int(5 / skinFactor)),
                                     size=(int(790 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=entry[0]))
    if entry[3] == "yes-no":
        text = _("on") if entry[1] else _("off")
    else:
        text = entry[1]
    res.append(MultiContentEntryText(pos=(int(800 / skinFactor), int(5 / skinFactor)),
                                     size=(int(1040 / skinFactor), int(50 / skinFactor)),
                                     flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER,
                                     font=0,
                                     text=text))

    res.append(MultiContentEntryText(pos=(0, int(58 / skinFactor)),
                                     size=(int(1840 / skinFactor), int(2 / skinFactor)),
                                     flags=0 | 0,
                                     font=0,
                                     text="",
                                     backcolor=0x545a5f))

    return res


def get_free_flash(path):
    try:
        flash_info = "free: N/A"
        fd = os.popen("df -m %s | tail -n1" % path)
        for line in fd.readlines():
            items = line.split()
            if len(items) > 5:
                flash_info = items[3]
                break
        fd.close()
        free_flash = int(flash_info) if flash_info else None
        if free_flash:
            free_flash = "free: " + str(int(free_flash / 1000)) + "GB" if free_flash / 1000 >= 1 else "free: " + str(
                free_flash) + "MB"
        else:
            free_flash = "free: N/A"
    except:
        free_flash = "free: N/A"
    return free_flash


def get_cache_info(path):
    try:
        cache_info = None
        fd = os.popen("du -sh %s" % config.justwatch.cache_destination.value)
        for line in fd.readlines():
            items = line.split()
            if items:
                cache_info = items[0]
                break
        fd.close()
        cache_size = cache_info if cache_info else None
    except:
        cache_size = None
    try:
        cover_info = None
        fd = os.popen("find %s -type f -maxdepth 1 | wc -l" % config.justwatch.cache_destination.value)
        result = fd.readlines()
        if result:
            cover_info = result[0]
        fd.close()
        cover_size = cover_info if cover_info else None
    except:
        cover_size = None
    try:
        flash_info = None
        fd = os.popen("df -m %s | tail -n1" % config.justwatch.cache_destination.value)
        for line in fd.readlines():
            items = line.split()
            if len(items) > 5:
                flash_info = items[3]
                break
        fd.close()
        free = int(flash_info) if flash_info else None
        if free:
            free = str(int(free / 1000)) + "GB" if free / 1000 >= 1 else str(free) + "MB"
    except:
        free = None
    info = ""
    if cover_size:
        info += "cover: " + str(cover_size)
    if cache_size:
        info += "  cache size: " + str(cache_size)
    if free:
        info += " free: " + free
    return re.sub("\n", "", info)
