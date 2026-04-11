from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend, MultiContentEntryPixmapAlphaTest
from Components.config import config, ConfigText, ConfigSubsection, configfile, ConfigPassword, ConfigYesNo, ConfigSubList
from enigma import ePicLoad, gFont, addFont, ePythonMessagePump, eServiceReference, eTimer, gPixmapPtr, \
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, getPrevAsciiCode, eTimer, eLabel

from Screens.Console import Console
from Screens.Standby import TryQuitMainloop

config.justwatch = ConfigSubsection()
config.justwatch.locale = ConfigText(default="de_DE", fixed_size=False)
config.justwatch.country = ConfigText(default="DE", fixed_size=False)

config.justwatch.providers = ConfigText(default="", fixed_size=False)

config.justwatch.cache_destination = ConfigText(default="/tmp/JustWatch", fixed_size=False)
config.justwatch.cache_clear = ConfigYesNo(default=False)
config.justwatch.content_mode = ConfigText(default="SD", fixed_size=False)

from .justWatch import *
from .just_watch_provider_config import ProviderConfig
from .just_watch_fsk_config import FskConfig
from .just_watch_genre_config import GenreConfig
from .just_watch_century_config import CenturyConfig
from .just_watch_config import SettingsConfig
from .just_watch_country_config import CountryConfig
from .just_watch_spinner import JustWatchSpinner
from .just_watch_search import SearchInput
from .just_watch_movie import JustWatchMovieScreen
from .just_watch_series import JustWatchSeriesScreen
from .just_watch_cache_config import JustWatchCacheScreen
from .just_watch_watchlist import JustWatchWatchlist

from .__init__ import _

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    BACKGROUND_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_1840x50.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_100x100.png"
    SELECT_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_150x50.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_110x110.png"
    SELECT_BIG_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_250x50.png"
    NO_WATCHLIST = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/no_watchlist_20x36.png"
    IS_WATCHLIST = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_watchlist_20x36.png"
else:
    skinFactor = 1.5
    BACKGROUND_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/content_background_1226x33.png"
    RADIUS_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/radius_66x66.png"
    SELECT_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_100x33.png"
    SELECT_PROVIDER = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_73x73.png"
    SELECT_BIG_CONTENT = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/select_166x33.png"
    NO_WATCHLIST = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/no_watchlist_13x24.png"
    IS_WATCHLIST = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/is_watchlist_13x24.png"

VERSION = "2.0.0"

WELCOME_STR = _("Welcome to Just Watch")
TITLE_STR = _(" Title")
WATCHLIST_STR = _("Watchlist")

COUNTRY_DIRECTORY = "/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/country/"

INFO = (
    "JustWatch\n\n"
    "Version: " + VERSION + "\n"
    "Platform: openATV / Enigma2\n"
    "Runtime: Python 3\n\n"
    "This release is a maintained openATV port of the original JustWatch from murxer plugin.\n"
    "The codebase was migrated to Python 3 and updated to use a completely new API backend.\n"
)
VERSIONURL = ""


class JustWatch(Screen, ProviderConfig, FskConfig, GenreConfig, CenturyConfig, SettingsConfig, CountryConfig, JustWatchSpinner, SearchInput):
    try:
        addFont("/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/font/OpenSans-Regular.ttf", "JW", 100,
                False)
    except Exception as ex:
        addFont("/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/font/OpenSans-Regular.ttf", "JW", 100,
                False,
                0)

    def __init__(self, session):
        if DESKTOPSIZE.width() >= 1920:
            self.skin = """<screen backgroundColor="#001b1e25" flags="wfNoBorder" name="JustWatch" position="center,center" size="1920,1080" title="JustWatch">
                           <ePixmap name="JustWatchLogo" position="40,10" size="296,70" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_logo_296x70.png" zPosition="1" />
                           <widget name="JustWatchHomeText" position="610,10" size="700,70" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="1" font="JW; 46" valign="center" halign="center"/>
                           <ePixmap name="JustWatchMenu" position="1820,20" size="60,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_menu_60x50.png" zPosition="1" />
                           <!-- Provider -->
                           <eLabel name="background" position="0,100" size="1920,250" backgroundColor="#001a2632" transparent="0" zPosition="1" />
                           <widget name="JustWatchProvider" position="40,100" size="1840,110" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
                           <widget name="BackgroundProviderConfig" position="600,10" size="740,1050" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="ProviderConfigText" position="610,15" size="700,60" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="5" font="JW; 46" valign="center" halign="left"/>
                           <widget name="JustWatchProviderConfig" position="610,80" size="700,960" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarProvider" position="1310,80" size="20,960" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="960" />
                           <!-- Content -->
                           <widget name="JustWatchContentType" position="40,225" size="1840,50" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
                           <!-- Settings -->
                           <widget name="BackgroundSettingsConfig" position="600,10" size="740,1050" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="SettingsText" position="610,15" size="700,60" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="5" font="JW; 46" valign="center" halign="left"/>
                           <widget name="JustWatchSettingsConfig" position="610,80" size="700,960" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollbarConfig" position="1310,80" size="20,960" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="960" />
                           <!-- Country -->
                           <widget name="BackgroundCountryConfig" position="600,10" size="740,1050" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="CountryText" position="610,15" size="700,60" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="5" font="JW; 46" valign="center" halign="left"/>
                           <widget name="JustWatchCountryConfig" position="610,80" size="700,960" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollbarCountryConfig" position="1310,80" size="20,960" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="960" />
                           <!-- Century -->
                           <widget name="BackgroundCenturyConfig" position="540,290" size="740,680" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="JustWatchCenturyConfig" position="555,300" size="700,660" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarCentury" position="1255,300" size="20,660" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="660" />
                           <!-- Genre -->
                           <widget name="BackgroundGenreConfig" position="705,290" size="740,680" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="JustWatchGenreConfig" position="715,300" size="700,660" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarGenre" position="1415,300" size="20,660" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="660" />
                           <!-- FSK -->
                           <widget name="BackgroundFskConfig" position="870,290" size="370,320" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="JustWatchFskConfig" position="880,300" size="350,300" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <!-- Search -->
                           <ePixmap name="JustWatchSearch" position="40,290" size="976,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search_975x50.png" zPosition="2" />
                           <widget name="JustWatchSearchSelect" position="40,290" size="976,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search_select_975x50.png" zPosition="3" />
                           <widget name="text" position="110,295" size="900,40" backgroundColor="#001a2632" foregroundColor="#00545a5f" zPosition="4" font="JW; 28" noWrap="1" valign="center" halign="left" />
                           <widget name="BackgroundSearch" position="532,580" size="856,390" backgroundColor="#001a2632" transparent="0" zPosition="5" />
                           <widget name="list" position="552,600" size="816,350" backgroundColor="#001a2632" foregroundColor="#00ffffff" selectionDisabled="1" transparent="1" zPosition="6" />
                           <!-- Watchlist -->
                           <ePixmap name="JustWatchWatchlist" position="1630,290" size="250,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/watchlist_background_250x50.png" zPosition="3" />
                           <widget name="JustWatchWatchlistText" position="1637,295" size="180,40" backgroundColor="#001a2632" foregroundColor="#00545a5f" zPosition="4" font="JW; 28" noWrap="1" valign="center" halign="left" />
                           <widget name="JustWatchWatchlistSelect" position="1630,290" size="250,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/watchlist_select_250x50.png" zPosition="4" />
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
                           <ePixmap name="JustWatchMenu" position="1213,13" size="40,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/just_menu_40x33.png" zPosition="1" />
                           <!-- Provider -->
                           <eLabel name="background" position="0,66" size="1280,166" backgroundColor="#001a2632" transparent="0" zPosition="1" />
                           <widget name="JustWatchProvider" position="26,66" size="1226,73" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
                           <widget name="BackgroundProviderConfig" position="400,6" size="493,700" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="ProviderConfigText" position="406,10" size="306,40" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="5" font="JW; 30" valign="center" halign="left"/>
                           <widget name="JustWatchProviderConfig" position="406,53" size="466,640" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarProvider" position="873,53" size="13,640" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="640" />
                           <!-- Content -->
                           <widget name="JustWatchContentType" position="26,150" size="1226,33" backgroundColor="#001a2632" zPosition="2" transparent="1" enableWrapAround="1" />
                           <!-- Settings -->
                           <widget name="BackgroundSettingsConfig" position="400,6" size="493,700" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="SettingsText" position="406,10" size="306,40" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="5" font="JW; 30" valign="center" halign="left"/>
                           <widget name="JustWatchSettingsConfig" position="406,53" size="466,640" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollbarConfig" position="873,53" size="13,640" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="640" />
                           <!-- Country -->
                           <widget name="BackgroundCountryConfig" position="400,6" size="493,700" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="CountryText" position="406,10" size="306,40" backgroundColor="#001b1e25" transparent="1" foregroundColor="#00545a5f" zPosition="5" font="JW; 30" valign="center" halign="left"/>
                           <widget name="JustWatchCountryConfig" position="406,53" size="466,640" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollbarCountryConfig" position="873,53" size="13,640" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="640" />
                           <!-- Century -->
                           <widget name="BackgroundCenturyConfig" position="360,193" size="493,453" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="JustWatchCenturyConfig" position="370,200" size="466,440" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarCentury" position="836,200" size="13,440" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="440" />
                           <!-- Genre -->
                           <widget name="BackgroundGenreConfig" position="470,193" size="493,453" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="JustWatchGenreConfig" position="476,200" size="466,440" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <widget name="MyScrollBarGenre" position="943,200" size="13,440" transparent="0" backgroundColor="#001a2632" zPosition="5" itemHeight="440" />
                           <!-- FSK -->
                           <widget name="BackgroundFskConfig" position="580,193" size="246,213" backgroundColor="#001a2632" transparent="0" zPosition="4" />
                           <widget name="JustWatchFskConfig" position="586,200" size="233,200" backgroundColorSelected="#001b1e25" foregroundColorSelected="#00ffffff" foregroundColor="#00545a5f" backgroundColor="#001a2632" zPosition="5" transparent="0" enableWrapAround="1" />
                           <!-- Search -->
                           <ePixmap name="JustWatchSearch" position="26,193" size="650,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search_650x33.png" zPosition="2" />
                           <widget name="JustWatchSearchSelect" position="26,193" size="650,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search_select_650x33.png" zPosition="3" />
                           <widget name="text" position="73,196" size="600,26" backgroundColor="#001a2632" foregroundColor="#00545a5f" zPosition="4" font="JW; 18" noWrap="1" valign="center" halign="left" />
                           <widget name="BackgroundSearch" position="354,386" size="570,260" backgroundColor="#001a2632" transparent="0" zPosition="5" />
                           <widget name="list" position="368,400" size="544,233" backgroundColor="#001a2632" foregroundColor="#00ffffff" selectionDisabled="1" transparent="1" zPosition="6" />
                           <!-- Watchlist -->
                           <ePixmap name="JustWatchWatchlist" position="1086,193" size="166,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/watchlist_background_166x33.png" zPosition="2" />
                           <widget name="JustWatchWatchlistText" position="1091,196" size="120,26" backgroundColor="#001a2632" foregroundColor="#00545a5f" zPosition="4" font="JW; 18" noWrap="1" valign="center" halign="left" />
                           <widget name="JustWatchWatchlistSelect" position="1086,193" size="166,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/watchlist_select_166x33.png" zPosition="3" />
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

        ProviderConfig.__init__(self)
        FskConfig.__init__(self)
        GenreConfig.__init__(self)
        CenturyConfig.__init__(self)
        SettingsConfig.__init__(self)
        CountryConfig.__init__(self)
        JustWatchSpinner.__init__(self, background=True)
        SearchInput.__init__(self)

        self['actions'] = NumberActionMap(['OkCancelActions',
                                           'WizardActions',
                                           'ColorActions',
                                           'KeyboardInputActions',
                                           'InputBoxActions',
                                           "MenuActions",
                                           'InputAsciiActions',
                                           'JustWatch_Actions'], {'gotAsciiCode': self.keyGotAscii,
                                                                  'ok': self.keyOk,
                                                                  'cancel': self.keyCancel,
                                                                  'cancelLong': self.keyExitLong,
                                                                  "menu": self.keyMenu,
                                                                  'left': self.keyLeft,
                                                                  'right': self.keyRight,
                                                                  'up': self.keyUp,
                                                                  'down': self.keyDown,
                                                                  'blue': self.keyBlue,
                                                                  'deleteBackward': self.backClicked,
                                                                  'deleteForward': self.forwardClicked,
                                                                  'nextBouquet': self.pageUp,
                                                                  'prevBouquet': self.pageDown,
                                                                  'info': self.keyInfo,
                                                                  '1': self.keyNumberGlobal,
                                                                  '2': self.keyNumberGlobal,
                                                                  '3': self.keyNumberGlobal,
                                                                  '4': self.keyNumberGlobal,
                                                                  '5': self.keyNumberGlobal,
                                                                  '6': self.keyNumberGlobal,
                                                                  '7': self.keyNumberGlobal,
                                                                  '8': self.keyNumberGlobal,
                                                                  '9': self.keyNumberGlobal,
                                                                  '0': self.keyNumberGlobal}, -2)

        self.chooseJustWatchProviderList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchProviderList.l.setItemHeight(int(110 / skinFactor))
        self['JustWatchProvider'] = self.chooseJustWatchProviderList

        self.chooseJustWatchContentTypeList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchContentTypeList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self.chooseJustWatchContentTypeList.l.setItemHeight(int(50 / skinFactor))
        self['JustWatchContentType'] = self.chooseJustWatchContentTypeList

        self['JustWatchHomeText'] = Label(WELCOME_STR)
        self['JustWatchItemText'] = Label("")

        self.chooseJustWatchCoverList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchCoverList.l.setItemHeight(int(670 / skinFactor))
        self.chooseJustWatchCoverList.l.setFont(0, gFont('JW', int(28 / skinFactor)))
        self['JustWatchCover'] = self.chooseJustWatchCoverList

        self.chooseJustWatchSelectCoverList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseJustWatchSelectCoverList.l.setItemHeight(int(670 / skinFactor))
        self.chooseJustWatchSelectCoverList.l.setFont(0, gFont('JW', 0))
        self['JustWatchSelectCover'] = self.chooseJustWatchSelectCoverList

        self['JustWatchSearchSelect'] = Pixmap()
        self['JustWatchSearchSelect'].hide()

        self['JustWatchWatchlistText'] = Label(WATCHLIST_STR)
        self['JustWatchWatchlistSelect'] = Pixmap()
        self['JustWatchWatchlistSelect'].hide()

        if not os.path.isdir(config.justwatch.cache_destination.value):
            os.system("mkdir %s" % config.justwatch.cache_destination.value)
        if not os.path.isdir("%s/provider" % config.justwatch.cache_destination.value):
            os.system("mkdir %s/provider" % config.justwatch.cache_destination.value)
        if not os.path.exists(WATCHLIST):
            os.system("mkdir /etc/enigma2/justWatch")

        self.cover_list = []
        self.setLoad = []
        self.download_list = []
        self.cover_gui_list = []
        self.providers_data = {}
        self.providers_gui_data = []
        self.video_data = {}
        self.content_type_data = ["All", "Movies", "Series", "Century", "Genres", "FSK", "Reset"]
        self.providers_gui_index = 0
        self.content_type_index = 0
        self.cover_index = 0
        self.cover_select = 0
        self.content_type = "All"
        self.gui_mode = 0
        self.select_watchlist = False
        self.page = 1

        self.amazon = None
        self.netflix = None
        self.disney = None

        self.CoverTimer = eTimer()
        self.CoverTimerStatus = False
        self.CoverTimer.callback.append(self.reloadCover)

        self.reloadSearchTimer = eTimer()
        self.reloadSearchTimerStatus = False
        self.reloadSearchTimer.callback.append(self.checkSearchInput)

        self.onLayoutFinish.append(self.do_import_providers)

    def check_free_space(self):
        get_free_flash(self.cbReceivedCheckSpace)

    def cbReceivedCheckSpace(self, free):
        if free:
            if free < 130:
                error = "Warning, only %sMB free on %s !" % (str(free), config.justwatch.cache_destination.value)
                try:
                    self.session.open(MessageBox, error, MessageBox.TYPE_ERROR)
                except:
                    print("JustWatch session error")

    def do_import_providers(self):
        self.providers_data = get_providers()
        self.createSetup()

    def createSetup(self):
        self.updateContentTypeList()
        if self.providers_data:
            self.providers_gui_index = 0
            self.providers_gui_data = []
            providers_active = config.justwatch.providers.value.split(",")
            select_all = True if config.justwatch.providers.value == "" else False
            for provider in self.providers_data:
                icon_url = get_provider_icon_url(provider.get("icon_url"))
                icon_destination = "%s/provider/%s.jpg" % (config.justwatch.cache_destination.value, provider.get("technical_name"))
                if provider.get("short_name") in providers_active or select_all:
                    self.providers_gui_data.append((provider.get("short_name"), icon_destination))
                if not os.path.isfile(icon_destination):
                    download_file(icon_url, icon_destination, self.updateProviderList)
            self.updateProviderList()
        self.createVideoData()
        self.check_free_space()

    def createVideoData(self):
        self.startJustWatchSpinner()
        self.clearTemp()
        self.cover_list = []
        self.download_list = []
        self.cover_gui_list = []
        self.cover_select = 0
        self.cover_index = 0
        self.page = 1
        self.video_data = {"items": [], "total_pages": 1, "total_results": 0}
        get_search_for_item(callback=self.cbReceivedVideoNextPage, query=self.query, page=self.page, content_types=self.content_type, genres=self.genre_config_list, age=self.fsk_config_list, century=self.century_config)
        #get_search_for_item(callback=self.cbReceivedVideo, query=self.query, content_types=self.content_type, genres=self.genre_config_list, age=self.fsk_config_list, century=self.century_config)

    def cbReceivedVideoNextPage(self, video):
        jw_debug('cbReceivedVideoNextPage called video_keys=%s' % (sorted(video.keys()) if isinstance(video, dict) else type(video).__name__))
        if not hasattr(self, "page") or self.page is None:
            self.page = 1
        if not hasattr(self, "video_data") or self.video_data is None:
            self.video_data = {"items": [], "total_pages": 1, "total_results": 0}
        if not isinstance(video, dict):
            video = {"items": [], "total_pages": 1, "total_results": 0}
        total_pages = int(video.get("total_pages") or self.video_data.get("total_pages") or 1)
        if not self.video_data.get("items"):
            self.video_data = video
            self.video_data["total_pages"] = total_pages
            if self.page < total_pages:
                self.page += 1
                get_search_for_item(callback=self.cbReceivedVideoNextPage, query=self.query, page=self.page, content_types=self.content_type, genres=self.genre_config_list, age=self.fsk_config_list, century=self.century_config)
            else:
                self.cbReceivedVideo(self.video_data)
        else:
            if video.get("items"):
                for item in video.get("items"):
                    self.video_data.setdefault("items", []).append(item)
                self.video_data["total_pages"] = total_pages
                if self.page < total_pages:
                    self.page += 1
                    get_search_for_item(callback=self.cbReceivedVideoNextPage, query=self.query, page=self.page, content_types=self.content_type, genres=self.genre_config_list, age=self.fsk_config_list, century=self.century_config)
                else:
                    self.cbReceivedVideo(self.video_data)
            else:
                self.cbReceivedVideo(self.video_data)

    def cbReceivedVideo(self, videos):
        jw_debug('cbReceivedVideo called videos_keys=%s total_results=%s items=%s' % ((sorted(videos.keys()) if isinstance(videos, dict) else type(videos).__name__), videos.get('total_results') if isinstance(videos, dict) else None, len(videos.get('items') or []) if isinstance(videos, dict) else None))
        self.video_data = videos
        if self.video_data:
            watchlistIdsMovie = get_watchlistIds(object_type="movie")
            watchlistIdsShow = get_watchlistIds(object_type="show")
            item_text = str(self.video_data.get("total_results")) + TITLE_STR if self.video_data.get("total_results") else "0" + TITLE_STR
            self['JustWatchItemText'].setText(item_text)
            for item in self.video_data["items"]:
                cover_destination = "%s/%s-poster.jpg" % (config.justwatch.cache_destination.value, str(item.get("id")))
                cover_size = "big" if skinFactor == 1 else "small"
                cover_url = get_poster_url(item.get("poster"), size=cover_size) if item.get("poster") else None
                object_type = item.get("object_type")
                title = item.get("title") if item.get("title") else ""
                if object_type == "movie":
                    watched = True if item.get("id") in watchlistIdsMovie else False
                else:
                    watched = True if item.get("id") in watchlistIdsShow else False
                if not os.path.isfile(cover_destination):
                    self.cover_list.append((cover_destination, cover_url))
                self.cover_gui_list.append((cover_destination, object_type, title, watched))
        else:
            self['JustWatchItemText'].setText("")
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
        if self.settings_config_list_show:
            screen_mode = self.key_settings_config_ok()
            self.do_hide_settings_config_gui()
            if screen_mode == "country":
                print("Get Country")
                data = []
                country_data = get_locale()
                index = 0
                x = 0
                for item in country_data:
                    if isinstance(item, dict):
                        title = item.get('country') or item.get('iso_3166_2') or ""
                        iso = item.get('iso_3166_2') or item.get('country') or ""
                        full_locale = item.get('full_locale') or config.justwatch.locale.value
                    else:
                        iso = str(item).upper()
                        title = iso
                        full_locale = config.justwatch.locale.value
                    if not iso:
                        continue
                    country_png_destination = "%s%s.png" % (COUNTRY_DIRECTORY, iso.lower())
                    select = True if config.justwatch.locale.value == full_locale else False
                    if select:
                        index = x
                    data.append((title, iso, full_locale, country_png_destination, select))
                    x += 1
                if data:
                    self.do_show_country_config_gui(data, index)
            elif screen_mode == "provider":
                data = []
                if self.providers_data:
                    providers_active = config.justwatch.providers.value.split(",")
                    for item in self.providers_data:
                        title = item.get("clear_name")
                        short_name = item.get("short_name")
                        sort_index = item.get("display_priority")
                        icon_destination = "%s/provider/%s.jpg" % (config.justwatch.cache_destination.value, item.get("technical_name"))
                        select = True if item.get("short_name") in providers_active else False
                        data.append((title, short_name, sort_index, icon_destination, select))
                if data:
                    self.gui_mode = 0
                    self.updateContentTypeList()
                    self.updateProviderList()
                    self.updateSelectCoverList()
                    self.do_show_provider_config_gui(data)
            elif screen_mode == "cache":
                self.session.openWithCallback(self.backSettings, JustWatchCacheScreen)
            elif screen_mode == "amazon":
                return
            elif screen_mode == "netflix":
                return
            elif screen_mode == "disney":
                return
        elif self.country_config_list_show:
            self.key_country_config_ok()
        elif self.gui_mode == 0 and not self.provider_config_list_show:
            data = []
            if self.providers_data:
                providers_active = config.justwatch.providers.value.split(",")
                for item in self.providers_data:
                    title = item.get("clear_name")
                    short_name = item.get("short_name")
                    sort_index = item.get("display_priority")
                    icon_destination = "%s/provider/%s.jpg" % (config.justwatch.cache_destination.value, item.get("technical_name"))
                    select = True if item.get("short_name") in providers_active else False
                    data.append((title, short_name, sort_index, icon_destination, select))
            if data:
                self.do_show_provider_config_gui(data)
        elif self.gui_mode == 0 and self.provider_config_list_show:
            self.key_provider_config_ok()
        elif self.gui_mode == 1:
            if self.content_type_index <= 2:
                self.content_type = self.content_type_data[self.content_type_index]
                self.updateContentTypeList()
                self.createVideoData()
            elif self.content_type_index == 3 and not self.century_config_list_show:
                print("Get Century")
                data = get_century(self.century_config)
                if data:
                    self.do_show_century_config_gui(data)
            elif self.content_type_index == 3 and self.century_config_list_show:
                self.key_century_config_ok()
                self.createVideoData()
                self.do_hide_century_config_gui()
                self.returnToMainScreen()
                return
            elif self.content_type_index == 4 and not self.genre_config_list_show:
                print("Get Genres")
                data = [("All", "__all__", -1, not self.genre_config_list)]
                genres = get_genres()
                if genres:
                    for item in genres:
                        title = item.get("translation")
                        short_name = item.get("short_name")
                        sort_index = item.get("id")
                        select = True if short_name in self.genre_config_list else False
                        data.append((title, short_name, sort_index, select))
                if data:
                    self.do_show_genre_config_gui(data)
            elif self.content_type_index == 4 and self.genre_config_list_show:
                self.key_genre_config_ok()
                self.createVideoData()
                self.do_hide_genre_config_gui()
                self.returnToMainScreen()
                return
            elif self.content_type_index == 5 and not self.fsk_config_list_show:
                print("Get FSK")
                data = []
                fsk = get_certifications()
                if fsk:
                    for item in fsk:
                        technical_name = item.get("technical_name")
                        sort_index = item.get("order")
                        custom_title = item.get("title")
                        if custom_title:
                            title = custom_title
                            select = True if not self.fsk_config_list else False
                        else:
                            title = item.get("organization") + ": " + item.get("technical_name")
                            select = True if technical_name in self.fsk_config_list else False
                        data.append((title, technical_name, sort_index, select))
                if data:
                    self.do_show_fsk_config_gui(data)
            elif self.content_type_index == 5 and self.fsk_config_list_show:
                self.key_fsk_config_ok()
                self.createVideoData()
                self.do_hide_fsk_config_gui()
                self.returnToMainScreen()
                return
            elif self.content_type_index == 6:
                self.century_config = None
                self.genre_config_list = []
                self.fsk_config_list = []
                self.query = None
                self.clearSearchText()
                self.createVideoData()
        elif self.gui_mode == 2 and not self.search_show and not self.select_watchlist:
            self.do_show_search()
            self.startSearchTimer()
        elif self.gui_mode == 2 and not self.search_show and self.select_watchlist:
            self.session.openWithCallback(self.updateVideoGui, JustWatchWatchlist, self.providers_gui_data, self.providers_data, None, None)
        elif self.gui_mode == 2 and self.search_show:
            self.search_ok()
        elif self.gui_mode == 3:
            current_item = self.video_data.get("items")[self.cover_index]
            item_id = current_item.get("jw_entity_id") or current_item.get("node_id") or current_item.get("id")
            item_content_type = current_item.get("object_type")
            if item_content_type == "movie":
                callback = self.cbReceivedMovieData
            else:
                callback = self.cbReceivedSeriesData
            jw_debug('detail request start item_id=%r item_content_type=%r callback=%s' % (item_id, item_content_type, getattr(callback, '__name__', repr(callback))))
            self.startJustWatchSpinner()
            get_title(title_id=item_id, content_type=item_content_type, callback=callback)

    def cbReceivedMovieData(self, movie_data):
        jw_debug('cbReceivedMovieData truthy=%s keys=%s' % (bool(movie_data), sorted(movie_data.keys()) if isinstance(movie_data, dict) else type(movie_data).__name__))
        self.stopJustWatchSpinner()
        if movie_data:
            self.session.openWithCallback(self.updateVideoGui, JustWatchMovieScreen, movie_data, self.providers_data, None, None, None)
        else:
            jw_debug('cbReceivedMovieData empty payload')

    def cbReceivedSeriesData(self, series_data):
        jw_debug('cbReceivedSeriesData truthy=%s keys=%s' % (bool(series_data), sorted(series_data.keys()) if isinstance(series_data, dict) else type(series_data).__name__))
        self.stopJustWatchSpinner()
        if series_data:
            self.session.openWithCallback(self.updateVideoGui, JustWatchSeriesScreen, series_data, self.providers_data, None, None, None)
        else:
            jw_debug('cbReceivedSeriesData empty payload')

    def updateVideoGui(self, callback=None):
        self.cover_gui_list = []
        if self.video_data.get("items"):
            watchlistIdsMovie = get_watchlistIds(object_type="movie")
            watchlistIdsShow = get_watchlistIds(object_type="show")
            item_text = str(self.video_data.get("total_results")) + TITLE_STR if self.video_data.get(
                "total_results") else "0" + TITLE_STR
            self['JustWatchItemText'].setText(item_text)
            for item in self.video_data["items"]:
                cover_destination = "%s/%s-poster.jpg" % (config.justwatch.cache_destination.value, str(item.get("id")))
                cover_size = "big" if skinFactor == 1 else "small"
                cover_url = get_poster_url(item.get("poster"), size=cover_size) if item.get(
                    "poster") else None
                object_type = item.get("object_type")
                title = item.get("title") if item.get("title") else ""
                if object_type == "movie":
                    watched = True if item.get("id") in watchlistIdsMovie else False
                else:
                    watched = True if item.get("id") in watchlistIdsShow else False
                self.cover_gui_list.append((cover_destination, object_type, title, watched))
        self.updateCoverList()

    def keyMenu(self):
        if self.century_config_list_show or self.fsk_config_list_show or self.genre_config_list_show or self.provider_config_list_show or self.settings_config_list_show or self.country_config_list_show or self.search_show:
            return
        self.do_show_settings_config_gui()

    def returnToMainScreen(self):
        if self.search_show:
            self.stopSearchTimer()
            self.do_hide_search()
        if self.settings_config_list_show:
            self.do_hide_settings_config_gui()
        if self.country_config_list_show:
            self.do_hide_country_config_gui()
        if self.provider_config_list_show:
            self.do_hide_provider_config_gui()
        if self.century_config_list_show:
            self.do_hide_century_config_gui()
        if self.genre_config_list_show:
            self.do_hide_genre_config_gui()
        if self.fsk_config_list_show:
            self.do_hide_fsk_config_gui()
        self.gui_mode = 2
        self.select_watchlist = False
        self['JustWatchSearchSelect'].show()
        self['JustWatchWatchlistSelect'].hide()
        self.updateContentTypeList()
        self.updateSelectCoverList()

    def keyExitLong(self):
        self.clearTemp()
        self.close(self.session, False)

    def keyCancel(self):
        if self.search_show:
            self.stopSearchTimer()
            self.do_hide_search()
            search_text = self.get_search_text()
            if len(search_text) <= 1:
                self.clearSearchText()
                self.query = None
            self.createVideoData()
            return
        if self.settings_config_list_show:
            self.do_hide_settings_config_gui()
            self.returnToMainScreen()
            return
        elif self.country_config_list_show:
            self.do_hide_country_config_gui()
            self.returnToMainScreen()
            return
        elif self.gui_mode == 0 and self.provider_config_list_show:
            self.do_hide_provider_config_gui()
            active_provider = []
            for title, short_name, sort_index, icon_destination, select in self.provider_config_list:
                if select:
                    active_provider.append(short_name)
            if not active_provider:
                config.justwatch.providers.value = ""
            else:
                config.justwatch.providers.value = ",".join(active_provider)
            config.justwatch.providers.save()
            configfile.save()
            self.createSetup()
            self.returnToMainScreen()
            return
        elif self.gui_mode == 1:
            if self.content_type_index == 3 and self.century_config_list_show:
                if self.century_update:
                    self.createVideoData()
                self.do_hide_century_config_gui()
                self.returnToMainScreen()
                return
            elif self.content_type_index == 4 and self.genre_config_list_show:
                if self.genre_update:
                    self.createVideoData()
                self.do_hide_genre_config_gui()
                self.returnToMainScreen()
                return
            elif self.content_type_index == 5 and self.fsk_config_list_show:
                if self.fsk_update:
                    self.createVideoData()
                self.do_hide_fsk_config_gui()
                self.returnToMainScreen()
                return
            self.returnToMainScreen()
            return
        elif self.gui_mode == 3:
            self.returnToMainScreen()
            return
        elif self.gui_mode == 2:
            self.returnToMainScreen()
            return

        self.returnToMainScreen()

    def backSettings(self, callback=None):
        self.close(self.session, True)

    def backAmazon(self, callback=None):
        self.close(self.session, True)

    def backNetflix(self, callback=None):
        self.close(self.session, True)

    def backDisney(self, callback=None):
        self.close(self.session, True)

    def checkSearchInput(self):
        search_text = self.get_search_text()
        if len(search_text) > 1:
            if not self.query == search_text:
                self.query = search_text
                self.createVideoData()
        self.startSearchTimer()

    def clearTemp(self):
        if config.justwatch.cache_clear.value:
            os.system("rm %s/*.jpg" % config.justwatch.cache_destination.value)

    def keyLeft(self):
        if self.settings_config_list_show:
            self.key_settings_config_left()
        elif self.country_config_list_show:
            self.key_country_config_left()
        elif self.gui_mode == 0 and not self.provider_config_list_show:
            if self.providers_gui_index != 0:
                self.providers_gui_index -= 1
                self.updateProviderList()
        elif self.gui_mode == 0 and self.provider_config_list_show:
            self.key_provider_config_left()
        elif self.gui_mode == 1:
            if self.content_type_index == 3 and self.century_config_list_show:
                self.key_century_config_left()
            elif self.content_type_index == 4 and self.genre_config_list_show:
                self.key_genre_config_left()
            elif self.content_type_index == 5 and self.fsk_config_list_show:
                self.key_fsk_config_left()
            elif self.content_type_index != 0:
                self.content_type_index -= 1
                self.updateContentTypeList()
        elif self.gui_mode == 2:
            if self.search_show:
                self.search_left()
            else:
                if self.select_watchlist:
                    self.select_watchlist = False
                    self['JustWatchSearchSelect'].show()
                    self['JustWatchWatchlistSelect'].hide()
        elif self.gui_mode == 3:
            if self.cover_index != 0:
                if self.cover_select != 0:
                    self.cover_select -= 1
                    self.cover_index -= 1
                    self.updateSelectCoverList()

    def keyRight(self):
        if self.settings_config_list_show:
            self.key_settings_config_right()
        elif self.country_config_list_show:
            self.key_country_config_right()
        elif self.gui_mode == 0 and not self.provider_config_list_show:
            if self.providers_gui_index < len(self.providers_gui_data) - 1:
                self.providers_gui_index += 1
            else:
                self.providers_gui_index = 0
            self.updateProviderList()
        elif self.gui_mode == 0 and self.provider_config_list_show:
            self.key_provider_config_right()
        elif self.gui_mode == 1:
            if self.content_type_index == 3 and self.century_config_list_show:
                self.key_century_config_right()
            elif self.content_type_index == 4 and self.genre_config_list_show:
                self.key_genre_config_right()
            elif self.content_type_index == 5 and self.fsk_config_list_show:
                self.key_fsk_config_right()
            elif self.content_type_index < 6:
                self.content_type_index += 1
                self.updateContentTypeList()
        elif self.gui_mode == 2:
            if self.search_show:
                self.search_right()
            else:
                if not self.select_watchlist:
                    self.select_watchlist = True
                    self['JustWatchSearchSelect'].hide()
                    self['JustWatchWatchlistSelect'].show()
        elif self.gui_mode == 3:
            if self.cover_index + 2 <= len(self.cover_gui_list):
                if self.cover_select < 7:
                    self.cover_index += 1
                    self.cover_select += 1
                    self.updateSelectCoverList()

    def keyUp(self):
        if self.settings_config_list_show:
            self.key_settings_config_up()
            return
        elif self.country_config_list_show:
            self.key_country_config_up()
            return
        elif self.gui_mode == 0:
            if self.provider_config_list_show:
                self.key_provider_config_up()
            return
        elif self.gui_mode == 1:
            if self.content_type_index == 3 and self.century_config_list_show:
                self.key_century_config_up()
                return
            elif self.content_type_index == 4 and self.genre_config_list_show:
                self.key_genre_config_up()
                return
            elif self.content_type_index == 5 and self.fsk_config_list_show:
                self.key_fsk_config_up()
                return
        elif self.gui_mode == 2 and self.search_show:
            self.search_up()
            return
        elif self.gui_mode == 3:
            if self.cover_index < 8:
                self.gui_mode = 2
                self.select_watchlist = False
                self['JustWatchSearchSelect'].show()
                self['JustWatchWatchlistSelect'].hide()
                self.updateSelectCoverList()
                self.updateContentTypeList()
            else:
                self.cover_index -= 8
                self.updateCoverList()
                self.updateSelectCoverList()
            return

        self.gui_mode -= 1
        if self.gui_mode == 2:
            self['JustWatchSearchSelect'].show()
        else:
            self['JustWatchSearchSelect'].hide()
            self['JustWatchWatchlistSelect'].hide()
        if self.gui_mode < 1:
            self.updateProviderList()
        self.updateContentTypeList()
        self.updateSelectCoverList()

    def keyDown(self):
        if self.settings_config_list_show:
            self.key_settings_config_down()
            return
        elif self.country_config_list_show:
            self.key_country_config_down()
            return
        elif self.gui_mode == 0 and self.provider_config_list_show:
            self.key_provider_config_down()
            return
        elif self.gui_mode == 1:
            self.select_watchlist = False
            if self.content_type_index == 3 and self.century_config_list_show:
                self.key_century_config_down()
                return
            elif self.content_type_index == 4 and self.genre_config_list_show:
                self.key_genre_config_down()
                return
            elif self.content_type_index == 5 and self.fsk_config_list_show:
                self.key_fsk_config_down()
                return
        elif self.gui_mode == 2 and self.search_show:
            self.search_down()
            return
        elif self.gui_mode == 3:
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
        if self.gui_mode == 2:
            if not self.select_watchlist:
                self['JustWatchSearchSelect'].show()
            else:
                self['JustWatchWatchlistSelect'].show()
        else:
            self['JustWatchSearchSelect'].hide()
            self['JustWatchWatchlistSelect'].hide()
        if self.gui_mode <= 1:
            self.updateProviderList()
        self.updateContentTypeList()
        self.updateSelectCoverList()

    def pageUp(self):
        if self.gui_mode == 3:
            if self.cover_index + 16 <= len(self.cover_gui_list) - 1:
                self.cover_index += 16
                self.updateCoverList()
        elif self.gui_mode == 2 and self.search_show:
            self.cursorRight()

    def pageDown(self):
        if self.gui_mode == 3:
            if self.cover_index - 16 >= 0:
                self.cover_index -= 16
                self.updateCoverList()
        elif self.gui_mode == 2 and self.search_show:
            self.cursorLeft()

    def keyBlue(self):
        if self.search_show:
            self.shiftClicked()

    def keyDeleteBackward(self):
        if self.search_show:
            self.backClicked()

    def keyDeleteForward(self):
        if self.search_show:
            self.forwardClicked()

    def keyInfo(self):
        self.session.open(MessageBox, windowTitle="JustWatch About", text=INFO, type=MessageBox.TYPE_INFO)

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

    def startSearchTimer(self):
        self.reloadSearchTimer.start(4000, True)

    def stopSearchTimer(self):
        if self.reloadSearchTimer is not None:
            self.reloadSearchTimer.stop()

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


def select_cover_entry(entry):
    res = [entry]
    select = entry[0]
    mode = entry[1]

    if mode == 3:
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

        watchlist_png = IS_WATCHLIST if data[x][3] else NO_WATCHLIST
        png = LoadPixmap(watchlist_png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, int(281 / skinFactor),
                    int(20 / skinFactor), int(36 / skinFactor), png))

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

        watchlist_png = IS_WATCHLIST if data[x][3] else NO_WATCHLIST
        png = LoadPixmap(watchlist_png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, w_pos, int(603 / skinFactor),
                    int(20 / skinFactor), int(36 / skinFactor), png))

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
                int(1840 / skinFactor), int(50 / skinFactor), png))
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
    for i in range(3):
        item = data[x]
        if x == index and mode == 1:
            png = LoadPixmap(SELECT_CONTENT)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, p_size, 0,
                        int(150 / skinFactor), int(50 / skinFactor), png))
        res.append(MultiContentEntryText(pos=(p_size + int(7 / skinFactor), int(5 / skinFactor)),
                                         size=(int(125 / skinFactor) - int(14 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                         font=0,
                                         text=_(item),
                                         color=0x545a5f,
                                         backcolor=0x1a2632))

        p_size = p_size + int(165 / skinFactor)
        x += 1

    for i in range(1):
        item = data[x]
        if x == index and mode == 1:
            png = LoadPixmap(SELECT_BIG_CONTENT)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(1590 / skinFactor), 0,
                        int(250 / skinFactor), int(50 / skinFactor), png))
        res.append(MultiContentEntryText(pos=(int(1597 / skinFactor), int(5 / skinFactor)),
                                         size=(int(200 / skinFactor), int(40 / skinFactor)),
                                         flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                                         font=0,
                                         text=_(item),
                                         color=0x545a5f,
                                         backcolor=0x1a2632))

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
        if os.path.isfile(icon_destination):
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


def exit(session, result):
    if result:
        session.openWithCallback(exit, JustWatch)


def main(session, **kwargs):
    session.openWithCallback(exit, JustWatch)


def sessionstart(reason, **kwargs):
    return


def Plugins(path, **kwwargs):
    return [
        PluginDescriptor(name='JustWatch', description=_('JustWatch streaming search'),
                         where=[PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main,
                         icon='plugin.png'),
        PluginDescriptor(name="JustWatch", where=PluginDescriptor.WHERE_SESSIONSTART, fnc=sessionstart)]
