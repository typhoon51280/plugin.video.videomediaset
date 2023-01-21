import xbmc
# from kodi_six import xbmc # pyright: reportMissingImports=false
import json
import time
import math
from phate89lib import kodiutils  # pyright: reportMissingImports=false
from resources.lib import sqlitequeue
from resources.lib.mediaset import Mediaset

class MediasetService:

    dispatchQueue = sqlitequeue.SqliteQueue()

    _actionMap = {
        'onAVStarted': 'check',
        'start': 'check',
        'offset': 'check',
        'pause': 'check',
        'resume': 'check',
        'seek': 'check',
        'end': 'scrobble',
        'stop': 'scrobble',
        'scrobble': 'scrobble'
    }

    def __init__(self):
        self.med = Mediaset()
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
            if actionName in self._actionMap:
                method_name = self._actionMap[actionName]
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    method(**data)
        except Exception as ex:
            kodiutils.log(kodiutils.createError(ex), 1)

    def scrobble(self, **data):
        guid = data['guid'] if 'guid' in data else ''
        position = data['position'] if 'position' in data else 0
        duration = data['duration'] if 'duration' in data else 0
        action = data['action'] if 'action' in data else ''
        kodiutils.log("[mediasetservice] scrobble: action={}, guid={}, position={}, duration={}".format(action,guid,position,duration))
        if position and guid and duration:
            if self.med.isAuthenticated():
                self.med.setProgress(guid, position, duration)
        # if action=='stop' or action=='end': # TBC Matrix
        #     self.player.resetResume()

    def check(self, **data):
        guid = data['guid'] if 'guid' in data else None
        url = data['url'] if 'url' in data else None
        path = data['path'] if 'path' in data else None
        offset = data['offset'] if 'offset' in data else None
        kodiutils.log("[mediasetservice] check: action={}, guid={}, offset={}, url={}, path={}".format(data['action'],guid,offset,url,path))
        if guid and url and path:
            self.player._clear(guid=guid, filename_url=url, filename_path=path, offset=offset, playing=True)
        self.player.transitionCheck()

    def run(self):
        # startup_delay = kodiutils.getSettingAsNum('startup_delay')
        # if startup_delay:
        #     kodiutils.log("Delaying startup by {} seconds.".format(startup_delay), 4)
        #     xbmc.sleep(startup_delay * 1000)

        kodiutils.log("mediasetservice started", 1)

        # setup event driven classes
        self.player = Player(action=self._dispatchQueue)
        self.monitor = Monitor(action=self._dispatchQueue)

        # start loop for events
        while not self.monitor.abortRequested():

            while len(self.dispatchQueue) and (not self.monitor.abortRequested()):
                data = self.dispatchQueue.get()
                self._dispatch(data)

            if self.monitor.waitForAbort(self.scrobblingInterval):
                # Abort was requested while waiting. We should exit
                break
            else:
                self.player.transitionCheck()

        # we are shutting down
        kodiutils.log("[mediasetservice] monitorService shut down.", 1)

        # delete player/monitor
        del self.player
        del self.monitor
class Monitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        kodiutils.log("[mediasetservice] monitor initialiazed")
        self.action = kwargs['action']
    
    def onNotification(self, sender, method, data):
        if sender != kodiutils.ID:
            return
        kodiutils.log("[mediasetservice] onNotification {}, {}".format(sender,method))
        if method and data:
            action = method.split('.')[-1]
            data = json.loads(data)
            data['action'] = action
            self.action(data)
         
class Player(xbmc.Player):

    def __init__(self, *args, **kwargs):
        self.action = kwargs['action']
        self._scrobbling = kodiutils.getSettingAsNum("scrobbling")
        self._clear()
        kodiutils.log("[mediasetservice] player initialiazed")

    def _clear(self, guid='', filename_url='', filename_path='', offset='', playing=False):
        self._guid = guid
        self._filenameUrl = filename_url
        self._filenamePath = filename_path
        self._offset = offset
        self._playing = playing
        self._position = 0
        self._duration = 0

    def isScrobbling(self):
        return self._scrobbling and self._guid and self._playing

    def __calculateSeconds(self, data):
        if data:
            hours = int(data['hours']) if 'hours' in data else 0
            minutes = int(data['minutes']) if 'minutes' in data else 0
            seconds = int(data['seconds']) if 'seconds' in data else 0
            return 3600*hours + 60*minutes + seconds
        return 0

    def __getTime(self):
        try:
            activePlayers = kodiutils.kodiJsonRequest({"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1})
            playerId = int(activePlayers[0]['playerid']) if activePlayers else 0
            if playerId:
                result = kodiutils.kodiJsonRequest({'jsonrpc': '2.0', 'method': 'Player.GetProperties', 'params': {'playerid': playerId, "properties": ["time","totaltime"]}, 'id': 1})
                timeData = result['time'] if 'time' in result else None
                totalTime = result['totaltime'] if 'totaltime' in result else None
                return self.__calculateSeconds(timeData), self.__calculateSeconds(totalTime)
        except Exception as ex:
            kodiutils.log(kodiutils.createError(ex), 1)
        return self._position, self._duration

    def __checkTime(self):
        position, duration = self.__getTime()
        if position:
            self._position = position
        if duration:
            self._duration = duration

    def __trySeek(self):
        if self._offset:
            offset = float(self._offset)
            if offset and offset>self._position:
                try:
                    self.seekTime(offset)
                except Exception as ex:
                    kodiutils.log(kodiutils.createError(ex), 1)
                position, _ = self.__getTime()
                if position < offset:
                    data = {'action': 'offset'}
                    self.action(data)
                else:
                    self._offset = ''
                
    def resetResume(self):
        kodiutils.kodiJsonRequest({"jsonrpc": "2.0", "method": "Files.SetFileDetails", "params": {"file": self._filenameUrl, "resume": {"position": 0}}, "id": 1})

    def transitionCheck(self):
        try:
            if self.isScrobbling() and self.isPlayingVideo():
                if self._filenamePath == self.getPlayingFile():
                    self.__checkTime()
                    # kodiutils.log("[mediasetservice] transitionCheck: guid={}, position={}, duration={}, offset={}".format(self._guid,self._position,self._duration,self._offset), 4)
                    self.__trySeek()
        except Exception as ex:
            kodiutils.log(kodiutils.createError(ex), 1)

    # called when kodi starts playing a file
    def onAVStarted(self):
        if self.isPlayingVideo():
            self.__checkTime()
            data = {'action': 'start'}
            self.action(data)
    
    # called when kodi stops playing a file
    def onPlayBackEnded(self):
        if self.isScrobbling():
            data = {'action': 'end', 'guid': self._guid, 'position': self._duration, 'duration': self._duration}
            self.action(data)
            self._clear()

    # called when user stops kodi playing a file
    def onPlayBackStopped(self):
        if self.isScrobbling():
            data = {'action': 'stop', 'guid': self._guid, 'position': self._position, 'duration': self._duration}
            self.action(data)
            self._clear()

    # called when user pauses a playing file
    def onPlayBackPaused(self):
        if self.isScrobbling():
            self.__checkTime()
            data = {'action': 'pause', 'guid': self._guid, 'position': self._position, 'duration': self._duration}
            self.action(data)

    # called when user resumes a paused file
    def onPlayBackResumed(self):
        if self.isScrobbling():
            self.__checkTime()
            data = {'action': 'resume', 'guid': self._guid, 'position': self._position, 'duration': self._duration}
            self.action(data)

    # called when user seeks to a time
    def onPlayBackSeek(self, time, offset):
        if self.isScrobbling():
            self.__checkTime()
            data = {'action': 'seek', 'guid': self._guid, 'position': self._position, 'duration': self._duration}
            self.action(data)

    # called when user performs a chapter seek
    # def onPlayBackSeekChapter(self, chapter):
        # data = {'action': 'seekchapter', 'chapter': chapter}
        # self.action(data)
    