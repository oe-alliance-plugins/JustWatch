import os
import stat
import subprocess
from twisted.internet import reactor, threads

BIN = '/usr/lib/enigma2/python/Plugins/Extensions/JustWatch/youtube-dl'


def got_play_url(callback, id, name):
    url = "https://youtu.be/%s" % id
    try:
        os.chmod(BIN, stat.S_IXOTH)
        ytLink_raw = subprocess.check_output([BIN, '--no-check-certificate', '-f 22', '-g', url])
        ytLink_raw = ytLink_raw.splitlines()
        ytLink = ytLink_raw[0]
    except:
        ytLink = None
    reactor.callFromThread(callback, (ytLink, name))


def get_play_url(callback, id, name):
    threads.deferToThread(got_play_url, callback, id, name)
