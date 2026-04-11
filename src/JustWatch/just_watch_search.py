from Components.MenuList import MenuList
from Tools.NumericalTextInput import NumericalTextInput
from Tools.LoadPixmap import LoadPixmap
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from Components.VariableText import VariableText
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend, MultiContentEntryPixmapAlphaTest
from enigma import ePicLoad, gFont, addFont, ePythonMessagePump, eServiceReference, eTimer, gPixmapPtr,\
    getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, getPrevAsciiCode, eTimer, eLabel


DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    desksize = "1920"
else:
    skinFactor = 1.5
    desksize = "1280"


class VirtualKeyBoardList(MenuList):
    def __init__(self, list, enableWrapAround=False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('JW', int(34 / skinFactor)))
        self.l.setItemHeight(int(68 / skinFactor))


class SearchInput:
    def __init__(self):
        self.keys_list = []
        self.shiftkeys_list = []
        self.shiftMode = False
        self.selectedKey = 0
        self.smsChar = None
        self.query = None
        self.sms = NumericalTextInput(self.smsOK)

        self.search_str = ""

        self.key_bg = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_bg.png' % desksize)
        self.key_sel = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_sel.png' % desksize)
        self.key_backspace = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_backspace.png' % desksize)
        self.key_shift_sel = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_shift_sel.png' % desksize)
        self.key_space = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_space.png' % desksize)
        self.key_left = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_left.png' % desksize)
        self.key_right = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_right.png' % desksize)
        self.key_backspace = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_backspace.png' % desksize)
        self.key_clr = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_clr.png' % desksize)
        self.key_shift = LoadPixmap(
            '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/images/search/%s/vkey_shift.png' % desksize)

        self.keyImages = {'BACKSPACE': self.key_backspace,
                          'CLEAR': self.key_clr,
                          'SHIFT': self.key_shift,
                          'SPACE': self.key_space,
                          'LEFT': self.key_left,
                          'RIGHT': self.key_right}
        self.keyImagesShift = {'BACKSPACE': self.key_backspace,
                               'SHIFT': self.key_shift_sel,
                               'SPACE': self.key_space,
                               'LEFT': self.key_left,
                               'RIGHT': self.key_right}

        self['text'] = Input(currPos=0, allMarked=False)
        self['list'] = VirtualKeyBoardList([])
        self['BackgroundSearch'] = Label("")

        self.search_show = False
        self.setLang()
        self.onExecBegin.append(self.setKeyboardModeAscii)
        self.onLayoutFinish.append(self.buildVirtualKeyBoard)
        self.onLayoutFinish.append(self.do_hide_search)
        self.onClose.append(self.__onClose)

    def __onClose(self):
        self.sms.timer.stop()

    def do_show_search(self):
        self.search_show = True
        self['list'].show()
        self['BackgroundSearch'].show()

    def do_hide_search(self):
        self.search_show = False
        self['list'].hide()
        self['BackgroundSearch'].hide()

    def setLang(self):
        self.keys_list = [[u'SHIFT',
                           u'1',
                           u'2',
                           u'3',
                           u'4',
                           u'5',
                           u'6',
                           u'7',
                           u'8',
                           u'9',
                           u'0',
                           u'BACKSPACE'],
                          [u'q',
                           u'w',
                           u'e',
                           u'r',
                           u't',
                           u'z',
                           u'u',
                           u'i',
                           u'o',
                           u'p',
                           u'\xfc',
                           u'+'],
                          [u'a',
                           u's',
                           u'd',
                           u'f',
                           u'g',
                           u'h',
                           u'j',
                           u'k',
                           u'l',
                           u'\xf6',
                           u'\xe4',
                           u'#'],
                          [u'<',
                           u'y',
                           u'x',
                           u'c',
                           u'v',
                           u'b',
                           u'n',
                           u'm',
                           u',',
                           '.',
                           u'-',
                           u'CLEAR'],
                          [u'SPACE',
                           u'LEFT',
                           u'RIGHT',
                           u'@',
                           u'\xdf']]
        self.shiftkeys_list = [[u'SHIFT',
                                u'!',
                                u'"',
                                u'\xa7',
                                u'$',
                                u'%',
                                u'&',
                                u'/',
                                u'(',
                                u')',
                                u'=',
                                u'BACKSPACE'],
                               [u'Q',
                                u'W',
                                u'E',
                                u'R',
                                u'T',
                                u'Z',
                                u'U',
                                u'I',
                                u'O',
                                u'P',
                                u'\xdc',
                                u'*'],
                               [u'A',
                                u'S',
                                u'D',
                                u'F',
                                u'G',
                                u'H',
                                u'J',
                                u'K',
                                u'L',
                                u'\xd6',
                                u'\xc4',
                                u"'"],
                               [u'>',
                                u'Y',
                                u'X',
                                u'C',
                                u'V',
                                u'B',
                                u'N',
                                u'M',
                                u';',
                                u':',
                                u'_'],
                               [u'SPACE',
                                u'LEFT',
                                u'RIGHT',
                                u'?',
                                u'\\']]

    def virtualKeyBoardEntryComponent(self, keys):
        # w, h = skin.parameters.get('VirtualKeyboard', (45, 45))
        w = int(68 / skinFactor)
        h = int(68 / skinFactor)
        key_bg_width = self.key_bg and self.key_bg.size().width() or w
        key_images = self.shiftMode and self.keyImagesShift or self.keyImages
        res = [keys]
        text = []
        x = 0
        for key in keys:
            png = key_images.get(key, None)
            if png:
                width = png.size().width()
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=png))
            else:
                width = key_bg_width
                res.append(MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=self.key_bg))
                text.append(MultiContentEntryText(pos=(x, 0), size=(width, h), font=0, text=key,
                                                  flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER))
            x += width

        return res + text

    def buildVirtualKeyBoard(self):
        self.previousSelectedKey = None
        self.list = []
        self.max_key = 0
        for keys in self.shiftMode and self.shiftkeys_list or self.keys_list:
            self.list.append(self.virtualKeyBoardEntryComponent(keys))
            self.max_key += len(keys)

        self.max_key -= 1
        self.markSelectedKey()
        return

    def markSelectedKey(self):
        # w, h = skin.parameters.get('VirtualKeyboard', (45, 45))
        w = int(68 / skinFactor)
        h = int(68 / skinFactor)
        if self.previousSelectedKey is not None:
            self.list[self.previousSelectedKey // 12] = self.list[self.previousSelectedKey // 12][:-1]
        width = self.key_sel.size().width()
        try:
            x = self.list[self.selectedKey // 12][self.selectedKey % 12 + 1][1]
        except IndexError:
            self.selectedKey = self.max_key
            x = self.list[self.selectedKey // 12][self.selectedKey % 12 + 1][1]

        self.list[self.selectedKey // 12].append(
            MultiContentEntryPixmapAlphaTest(pos=(x, 0), size=(width, h), png=self.key_sel))
        self.previousSelectedKey = self.selectedKey
        self['list'].setList(self.list)
        return

    def keyNumberGlobal(self, number):
        if self.search_show:
            self.smsChar = self.sms.getKey(number)
            self.selectAsciiKey(self.smsChar)

    def smsOK(self):
        if self.search_show:
            if self.smsChar and self.selectAsciiKey(self.smsChar):
                print('pressing ok now')
                self.search_ok()

    def keyGotAscii(self):
        if self.search_show:
            self.smsChar = None
            if self.selectAsciiKey(chr(getPrevAsciiCode())):
                self.search_ok()
            return

    def backClicked(self):
        if self.search_show:
            self['text'].deleteBackward()

    def forwardClicked(self):
        if self.search_show:
            self['text'].deleteForward()

    def shiftClicked(self):
        self.smsChar = None
        self.shiftMode = not self.shiftMode
        self.buildVirtualKeyBoard()
        return

    def search_ok(self):
        self.smsChar = None
        text = (self.shiftMode and self.shiftkeys_list or self.keys_list)[self.selectedKey // 12][self.selectedKey % 12]
        print("key text: ---------------", text)
        if text == 'BACKSPACE':
            self['text'].deleteBackward()
        elif text == 'SPACE':
            self['text'].char(' ')
        elif text == 'SHIFT':
            self.shiftClicked()
        elif text == 'CLEAR':
            self['text'].deleteAllChars()
        elif text == 'LEFT':
            self['text'].left()
        elif text == 'RIGHT':
            self['text'].right()
        else:
            self['text'].char(text)
        return

    def clearSearchText(self):
        self['text'].deleteAllChars()
        self['text'].update()

    def cursorRight(self):
        if self.search_show:
            self['text'].right()

    def cursorLeft(self):
        if self.search_show:
            self['text'].left()

    def search_left(self):
        self.smsChar = None
        self.selectedKey = self.selectedKey // 12 * 12 + (self.selectedKey + 11) % 12
        self.markSelectedKey()
        return

    def search_right(self):
        self.smsChar = None
        selectedKey = self.selectedKey // 12 * 12 + (self.selectedKey + 1) % 12
        self.selectedKey = selectedKey
        self.markSelectedKey()
        return

    def search_up(self):
        self.selectedKey -= 12
        if self.selectedKey < 0:
            self.selectedKey = self.max_key // 12 * 12 + self.selectedKey % 12
            if self.selectedKey > self.max_key:
                self.selectedKey -= 12
        self.markSelectedKey()

    def search_down(self):
        self.smsChar = None
        self.selectedKey += 12
        if self.selectedKey > self.max_key:
            self.selectedKey %= 12
        self.markSelectedKey()
        return

    def selectAsciiKey(self, char):
        if char == ' ':
            self['text'].char(' ')
            return False
        for keyslist in (self.shiftkeys_list, self.keys_list):
            selkey = 0
            for keys in keyslist:
                for key in keys:
                    if key == char:
                        self.selectedKey = selkey
                        if self.shiftMode != (keyslist is self.shiftkeys_list):
                            self.shiftMode = not self.shiftMode
                            self.buildVirtualKeyBoard()
                        else:
                            self.markSelectedKey()
                        return True
                    selkey += 1

        return False

    def get_search_text(self):
        return self['text'].getText()


class Input(VariableText, HTMLComponent, GUIComponent, NumericalTextInput):
    TEXT = 0
    PIN = 1
    NUMBER = 2

    def __init__(self, text='', maxSize=False, visible_width=False, type=TEXT, currPos=0, allMarked=True):
        NumericalTextInput.__init__(self, self.right)
        GUIComponent.__init__(self)
        VariableText.__init__(self)
        self.type = type
        self.allmarked = allMarked and text != '' and type != self.PIN
        self.maxSize = maxSize
        self.currPos = currPos
        self.visible_width = visible_width
        self.offset = 0
        self.overwrite = maxSize
        self.setText(text)

    def __len__(self):
        return len(self.text)

    def update(self):
        if self.visible_width:
            if self.currPos < self.offset:
                self.offset = self.currPos
            if self.currPos >= self.offset + self.visible_width:
                if self.currPos == len(self.Text):
                    self.offset = self.currPos - self.visible_width
                else:
                    self.offset = self.currPos - self.visible_width + 1
            if self.offset > 0 and self.offset + self.visible_width > len(self.Text):
                self.offset = max(0, len(self.Text) - self.visible_width)
        if self.allmarked:
            self.setMarkedPos(-2)
        else:
            self.setMarkedPos(self.currPos - self.offset)
        if self.visible_width:
            if self.type == self.PIN:
                self.text = ''
                for x in self.Text[self.offset:self.offset + self.visible_width]:
                    self.text += x == ' ' and ' ' or '*'

            else:
                self.text = self.Text[self.offset:self.offset + self.visible_width] + ' '
        elif self.type == self.PIN:
            self.text = ''
            for x in self.Text:
                self.text += x == ' ' and ' ' or '*'

        else:
            self.text = self.Text + ' '

    def setText(self, text):
        if not len(text):
            self.currPos = 0
            self.Text = u''
        elif isinstance(text, bytes):
            self.Text = text.decode('utf-8', 'ignore')
        else:
            self.Text = text
        self.update()

    def getText(self):
        return self.Text

    def createWidget(self, parent):
        if self.allmarked:
            return eLabel(parent, -2)
        else:
            return eLabel(parent, self.currPos - self.offset)

    def getSize(self):
        s = self.instance.calculateSize()
        return (s.width(), s.height())

    def markAll(self):
        self.allmarked = True
        self.update()

    def innerright(self):
        if self.allmarked:
            self.currPos = 0
            self.allmarked = False
        elif self.maxSize:
            if self.currPos < len(self.Text) - 1:
                self.currPos += 1
        elif self.currPos < len(self.Text):
            self.currPos += 1

    def right(self):
        if self.type == self.TEXT:
            self.timeout()
        self.innerright()
        self.update()

    def left(self):
        if self.type == self.TEXT:
            self.timeout()
        if self.allmarked:
            if self.maxSize:
                self.currPos = len(self.Text) - 1
            else:
                self.currPos = len(self.Text)
            self.allmarked = False
        elif self.currPos > 0:
            self.currPos -= 1
        self.update()

    def up(self):
        self.allmarked = False
        if self.type == self.TEXT:
            self.timeout()
        if self.currPos == len(self.Text) or self.Text[self.currPos] == '9' or self.Text[self.currPos] == ' ':
            newNumber = '0'
        else:
            newNumber = str(int(self.Text[self.currPos]) + 1)
        self.Text = self.Text[0:self.currPos] + newNumber + self.Text[self.currPos + 1:]
        self.update()

    def down(self):
        self.allmarked = False
        if self.type == self.TEXT:
            self.timeout()
        if self.currPos == len(self.Text) or self.Text[self.currPos] == '0' or self.Text[self.currPos] == ' ':
            newNumber = '9'
        else:
            newNumber = str(int(self.Text[self.currPos]) - 1)
        self.Text = self.Text[0:self.currPos] + newNumber + self.Text[self.currPos + 1:]
        self.update()

    def home(self):
        self.allmarked = False
        if self.type == self.TEXT:
            self.timeout()
        self.currPos = 0
        self.update()

    def end(self):
        self.allmarked = False
        if self.type == self.TEXT:
            self.timeout()
        if self.maxSize:
            self.currPos = len(self.Text) - 1
        else:
            self.currPos = len(self.Text)
        self.update()

    def insertChar(self, ch, pos=False, owr=False, ins=False):
        if isinstance(ch, bytes):
            ch = ch.decode('utf-8', 'ignore')
        if not pos:
            pos = self.currPos
        if ins and not self.maxSize:
            self.Text = self.Text[0:pos] + ch + self.Text[pos:]
        elif owr or self.overwrite:
            self.Text = self.Text[0:pos] + ch + self.Text[pos + 1:]
        elif self.maxSize:
            self.Text = self.Text[0:pos] + ch + self.Text[pos:-1]
        else:
            self.Text = self.Text[0:pos] + ch + self.Text[pos:]

    def deleteChar(self, pos):
        if not self.maxSize:
            self.Text = self.Text[0:pos] + self.Text[pos + 1:]
        elif self.overwrite:
            self.Text = self.Text[0:pos] + u' ' + self.Text[pos + 1:]
        else:
            self.Text = self.Text[0:pos] + self.Text[pos + 1:] + u' '

    def deleteAllChars(self):
        if self.maxSize:
            self.Text = u' ' * len(self.Text)
        else:
            self.Text = u''
        self.currPos = 0
        self.update()

    def tab(self):
        if self.type == self.TEXT:
            self.timeout()
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        else:
            self.insertChar(u' ', self.currPos, False, True)
            self.innerright()
        self.update()

    def delete(self):
        if self.type == self.TEXT:
            self.timeout()
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        else:
            self.deleteChar(self.currPos)
            if self.maxSize and self.overwrite:
                self.innerright()
        self.update()

    def deleteBackward(self):
        if self.type == self.TEXT:
            self.timeout()
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        elif self.currPos > 0:
            self.deleteChar(self.currPos - 1)
            if not self.maxSize and self.offset > 0:
                self.offset -= 1
            self.currPos -= 1
        self.update()

    def deleteForward(self):
        if self.type == self.TEXT:
            self.timeout()
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        else:
            self.deleteChar(self.currPos)
        self.update()

    def toggleOverwrite(self):
        if self.type == self.TEXT:
            self.timeout()
        self.overwrite = not self.overwrite
        self.update()

    def handleAscii(self, code):
        if self.type == self.TEXT:
            self.timeout()
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        self.insertChar(unichr(code), self.currPos, False, False)
        self.innerright()
        self.update()

    def number(self, number):
        if self.type == self.TEXT:
            owr = self.lastKey == number
            newChar = self.getKey(number)
        elif self.type == self.PIN or self.type == self.NUMBER:
            owr = False
            newChar = str(number)
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        self.insertChar(newChar, self.currPos, owr, False)
        if self.type == self.PIN or self.type == self.NUMBER:
            self.innerright()
        self.update()

    def char(self, char):
        if self.allmarked:
            self.deleteAllChars()
            self.allmarked = False
        self.insertChar(char)
        self.innerright()
        self.update()