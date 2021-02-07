# -*- coding: utf-8 -*-
#

import xbmc
import time
import logging
from phate89lib import kodiutils  # pyright: reportMissingImports=false
import math


logger = logging.getLogger(__name__)

class Scrobbler():
    isPlaying = False
    isPaused = False
    stopScrobbler = False
    isPVR = False
    isMultiPartEpisode = False
    lastMPCheck = 0
    curMPEpisode = 0
    videoDuration = 1
    watchedTime = 0
    pausedAt = 0
    curVideo = None
    curVideoInfo = None
    playlistIndex = 0
    cache = {}

    def __init__(self):
        logger.debug("init()")

    def playbackStarted(self, data):
        logger.debug("playbackStarted(data: %s)" % data)
        if not data:
            return
        self.curVideo = data
        self.curVideoInfo = None
        self.isPlaying = True

        if not kodiutils.getSettingAsBool('scrobble_fallback'):
            logger.debug('Aborting scrobble to avoid fallback: %s' % (self.curVideo))
            return

        if data and 'id' in data:
            self.cache[data['id']] = data

    def playbackResumed(self):
        if not self.isPlaying:
            return

        logger.debug("playbackResumed()")
        if self.isPaused:
            p = time.time() - self.pausedAt
            logger.debug("Resumed after: %s" % str(p))
            self.pausedAt = 0
            self.isPaused = False
            self.__scrobble('start')

    def playbackPaused(self):
        if not self.isPlaying or self.isPVR:
            return

        logger.debug("playbackPaused()")
        logger.debug("Paused after: %s" % str(self.watchedTime))
        self.isPaused = True
        self.pausedAt = time.time()
        self.__scrobble('pause')

    def playbackSeek(self):
        if not self.isPlaying:
            return

        logger.debug("playbackSeek()")
        self.transitionCheck(isSeek=True)

    def playbackEnded(self):
        if not self.isPVR:
            self.videosToRate.append(self.curVideoInfo)
        if not self.isPlaying:
            return

        logger.debug("playbackEnded()")
        if not self.videosToRate and not self.isPVR:
            logger.debug("Warning: Playback ended but video forgotten.")
            return
        self.isPlaying = False
        self.stopScrobbler = False
        if self.watchedTime != 0:
            if 'type' in self.curVideo:
                self.__scrobble('stop')
                ratingCheck(self.curVideo['type'], self.videosToRate, self.watchedTime, self.videoDuration)
            self.watchedTime = 0
            self.isPVR = False
            self.isMultiPartEpisode = False
        self.videosToRate = []
        self.curVideoInfo = None
        self.curVideo = None
        self.playlistIndex = 0

    def __scrobble(self, position):
        logger.debug("scrobble()")
                
                
    def __scrobbleNotification(self, info):
        if not self.curVideoInfo:
            return

        if kodiUtilities.getSettingAsBool("scrobble_notification"):
            s = utilities.getFormattedItemName(self.curVideo['type'], info[self.curVideo['type']])
            kodiUtilities.notification(kodiUtilities.getString(32015), s)
