from enigma import ePicLoad, eTimer, gPixmapPtr
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.Label import Label


SPINNER_DIRECTORY = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/spinner"


class JustWatchSpinner:
    def __init__(self, background=False):
        # Spinner Timer
        self['BackgroundSpinner'] = Label("")
        self['JustWatchSpinner'] = Pixmap()
        self['JustWatchSpinner'].hide()
        self['BackgroundSpinner'].hide()
        self.JustWatchSpinner = eTimer()
        self.JustWatchSpinnerBackground = background
        self.JustWatchSpinnerStatusSpinner = False
        self.JustWatchSpinnerTimer = 1
        self.JustWatchSpinner.callback.append(self.loadJustWatchSpinner)

    def stopJustWatchSpinner(self):
        self.JustWatchSpinnerStatusSpinner = False

    def startJustWatchSpinner(self):
        self.JustWatchSpinnerStatusSpinner = True
        self.loadJustWatchSpinner()

    def loadJustWatchSpinner(self):
        if self.JustWatchSpinnerStatusSpinner:
            png = "%s/%s.png" % (SPINNER_DIRECTORY, str(self.JustWatchSpinnerTimer))
            self.showJustWatchSpinner(png)
        else:
            self['JustWatchSpinner'].hide()
            self['BackgroundSpinner'].hide()

    def showJustWatchSpinner(self, png):
        self['JustWatchSpinner'].instance.setPixmap(gPixmapPtr())
        self.scale = AVSwitch().getFramebufferScale()
        self.picload = ePicLoad()
        size = self['JustWatchSpinner'].instance.size()
        self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#ff1b1e25"))
        decode = self.picload.startDecode(png, 0, 0, False)
        if decode == 0:
            ptr = self.picload.getData()
            if ptr is not None:
                self['JustWatchSpinner'].instance.setPixmap(ptr)
                if self.JustWatchSpinnerBackground:
                    self['BackgroundSpinner'].show()
                self['JustWatchSpinner'].show()
                del self.picload
        if self.JustWatchSpinnerTimer != 8:
            self.JustWatchSpinnerTimer += 1
        else:
            self.JustWatchSpinnerTimer = 1
        self.JustWatchSpinner.start(100, True)
