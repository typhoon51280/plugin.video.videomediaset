# import xbmc
from kodi_six import xbmc # pyright: reportMissingImports=false
import json
import time
import math
from phate89lib import kodiutils  # pyright: reportMissingImports=false
from resources.lib import sqlitequeue
from resources.lib.mediaset import Mediaset

class MediasetService:

    dispatchQueue = sqlitequeue.SqliteQueue()

    _actionMap = {
        'start': 'scrobble',
        'end': 'scrobble',
        'pause': 'scrobble',
        'stop': 'scrobble',
        'seek': 'scrobble',
        'scrobble': 'scrobble'
    }

    def __init__(self):
        self.med = Mediaset()
        self.med.setUserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        self.med.log = kodiutils.log
        self.scrobblingInterval = kodiutils.getSettingAsNum("scrobblingInterval")
        kodiutils.log('[mediasetservice] monitorService init')

    def _dispatchQueue(self, data):
        # kodiutils.log("[mediasetservice] Queuing for dispatch: %s" % data)
        self.dispatchQueue.append(data)

    def _action(self, actionName, **kwargs):
        # kodiutils.log("[mediasetservice] _action: {} => {}".format(actionName,str(kwargs)))
        if actionName in self._actionMap:
            method_name = self._actionMap[actionName]
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                method(**kwargs)

    def _dispatch(self, data):
        try:
            # kodiutils.log("[mediasetservice] Dispatch: %s" % data)
            actionName = data['action']
            guid = data['guid'] if 'guid' in data else 0
            position = data['position'] if 'position' in data else 0
            duration = data['duration'] if 'duration' in data else 0
            self._action(actionName, guid=guid, position=position, duration=duration)
        except Exception as ex:
            kodiutils.log(kodiutils.createError(ex), 1)

    def scrobble(self, guid=0, position=0, duration=0):
        kodiutils.log("[mediasetservice] scrobble: guid={}, position={}, duration={} ".format(str(guid),str(position),str(duration)))
        if position and guid and duration:
            user = kodiutils.getSetting('email')
            password = kodiutils.getSetting('password')
            if user and password and self.med.login(user, password):
                self.med.setProgress(guid, position, duration)

    def run(self):
        # startup_delay = kodiutils.getSettingAsNum('startup_delay')
        # if startup_delay:
        #     kodiutils.log("Delaying startup by {} seconds.".format(startup_delay), 4)
        #     xbmc.sleep(startup_delay * 1000)

        kodiutils.log("mediasetservice started", 1)

        # setup event driven classes
        self.cache = {}
        self.player = Player(cache=self.cache, action=self._dispatchQueue)
        self.monitor = Monitor(cache=self.cache, action=self._dispatchQueue)

        # start loop for events
        while not self.monitor.abortRequested():

            while len(self.dispatchQueue) and (not self.monitor.abortRequested()):
                data = self.dispatchQueue.get()
                self._dispatch(data)

            if self.monitor.waitForAbort(self.scrobblingInterval):
                # Abort was requested while waiting. We should exit
                break
            else:
                self.player._transitionCheck()

        # we are shutting down
        kodiutils.log("[mediasetservice] monitorService shut down.", 1)

        # delete player/monitor
        del self.player
        del self.monitor
        del self.cache


class Monitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        kodiutils.log("[mediasetservice] monitor initialiazed")
        self.cache = kwargs['cache'] if 'cache' in kwargs else {}
    
    def onNotification(self, sender, method, data):
        if sender != kodiutils.ID:
            return
        kodiutils.log("[mediasetservice] onNotification {}, {}".format(sender,method))
        if method and data and len(data)>0:
            action = method.split('.')[-1]
            self.cache['{}.{}'.format(sender,action)] = json.loads(data)
         
class Player(xbmc.Player):

    def __init__(self, *args, **kwargs):
        self.cache = kwargs['cache'] if 'cache' in kwargs else {}
        self.action = kwargs['action']
        self._scrobbling = kodiutils.getSettingAsNum("scrobbling")
        self._clear()
        kodiutils.log("[mediasetservice] player initialiazed")

    def _clear(self):
        self._playing = False
        self._guid = ''
        self._position = 0
        self._duration = 0

    def isScrobbling(self):
        return self._scrobbling and self._guid and self._playing

    def __getTime(self):
        activePlayers = kodiutils.kodiJsonRequest({"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1})
        playerId = int(activePlayers[0]['playerid']) if activePlayers else 0
        if playerId:
            result = kodiutils.kodiJsonRequest({'jsonrpc': '2.0', 'method': 'Player.GetProperties', 'params': {'playerid': playerId, "properties": ["time"]}, 'id': 1})
            # kodiutils.log("[mediasetservice] __getTime: {}".format(str(result)), 4)
            timeData = result['time'] if 'time' in result else None
            if timeData:
                hours = int(timeData['hours']) if 'hours' in timeData else 0
                minutes = int(timeData['minutes']) if 'minutes' in timeData else 0
                seconds = int(timeData['seconds']) if 'seconds' in timeData else 0
                return 3600*hours + 60*minutes + seconds
        return self._position

    def _transitionCheck(self):
        if self.isScrobbling() and self.isPlayingVideo():
            self._position =  self.__getTime()

    # called when kodi starts playing a file
    def onAVStarted(self):
        if self.isPlayingVideo():
            try:
                self._clear()
                item = self.cache.pop('{}.{}'.format(kodiutils.ID,'onAVStarted'), '')
                if item:
                    filename = self.getPlayingFile()
                    path = str(item['path'])
                    if path == filename:
                        self._playing = True
                        self._guid = item['guid'] if 'guid' in item else ''
                        self._duration = math.floor(self.getTotalTime())
                        self._position = self.__getTime()
                        offset = float(item['offset']) if 'offset' in item else 0.0
                        kodiutils.log("[mediasetservice] onAVStarted: guid={}, position={}, duration={}, offset={}".format(str(self._guid),str(self._position),str(self._duration),str(offset)), 4)
                        if offset and offset>self._position:
                            self.seekTime(offset)
                        # else:
                        #     data = {'action': 'start', 'guid': self._guid, 'position': self._position, 'duration': self._duration}
                        #     self.action(data)
                        
            except Exception as ex:
                kodiutils.log(kodiutils.createError(ex), 1)
    
    # called when kodi stops playing a file
    def onPlayBackEnded(self):
        if self.isScrobbling():
            # kodiutils.log("[mediasetservice] onPlayBackEnded")
            data = {'action': 'end', 'guid': self._guid, 'position': int(self._duration), 'duration': self._duration}
            self.action(data)
            self._clear()

    # called when user stops kodi playing a file
    def onPlayBackStopped(self):
        if self.isScrobbling():
            kodiutils.log("[mediasetservice] onPlayBackStopped")
            data = {'action': 'stop', 'guid': self._guid, 'position': self._position, 'duration': self._duration}
            self.action(data)
            self._clear()

    # called when user pauses a playing file
    def onPlayBackPaused(self):
        if self.isScrobbling():
            kodiutils.log("[mediasetservice] onPlayBackPaused")
            self._position = self.__getTime()

    # called when user resumes a paused file
    # def onPlayBackResumed(self):
        kodiutils.log("[mediasetservice] onPlayBackResumed")
        # time = self.__getTime()
        # data = {'action': 'resumed', 'time': time}
        # self.action(data)

    # called when user seeks to a time
    def onPlayBackSeek(self, time, offset):
        if self.isScrobbling():
            kodiutils.log("[mediasetservice] onPlayBackSeek")
            self._position = math.floor(time/1000)

    # called when user performs a chapter seek
    # def onPlayBackSeekChapter(self, chapter):
    #     kodiutils.log("[mediasetservice] onPlayBackSeekChapter")
        # data = {'action': 'seekchapter', 'chapter': chapter}
        # self.action(data)
    