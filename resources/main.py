# -*- coding: utf-8 -*-
from datetime import timedelta
import re
from resources.lib.mediaset import Mediaset
from resources.mediaset_datahelper import _gather_info, _gather_art, _gather_media_type
from phate89lib import kodiutils, staticutils  # pylint: disable=import-error


class KodiMediaset(object):

    def __init__(self):
        self.med = Mediaset()
        self.med.log = kodiutils.log
        self.iperpage = min(kodiutils.getSetting('itemsperpage'), 100)
        self.ua = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')

    def __imposta_tipo_media(self, prog):
        kodiutils.setContent(_gather_media_type(prog) + 's')

    def __analizza_elenco(self, progs, setcontent=False, titlewd=False):
        if not progs:
            return
        # scrobbling = kodiutils.getSettingAsNum('scrobbling')
        # kodiutils.log('scrobbling: {}'.format(str(scrobbling)), 4)
        if setcontent:
            self.__imposta_tipo_media(progs[0])
        for prog in progs:
            infos = _gather_info(prog, titlewd=titlewd)
            arts = _gather_art(prog)
            if 'media' in prog:
                # salta se non ha un media ma ha il tag perchè non riproducibile
                if prog['media']:
                    media = prog['media'][0]
                    args = {'mode': 'video'}
                    properties = {}
                    position = prog['position'] if 'position' in prog else 0
                    if 'pid' in media:
                        args['pid'] = media['pid']
                    elif 'publicUrl' in media:
                        args['pid'] = media['publicUrl'].split('/')[-1]
                    if 'guid' in media:
                        args['guid'] = media['guid']
                    if 'mediasetprogram$duration' in prog:
                        properties['TotalTime'] = str(prog['mediasetprogram$duration'])
                    properties['ResumeTime'] = '0.0'
                    # if not scrobbling:
                    #     properties['ResumeTime'] = '0.0'
                    # elif scrobbling == 2 and media['guid']:
                    #     user = kodiutils.getSetting('email')
                    #     password = kodiutils.getSetting('password')
                    #     if user and password and self.med.login(user, password):
                    #         offset = self.med.getProgress(media['guid'])
                    #         properties['ResumeTime'] = str(offset)
                    kodiutils.addListItem(infos["title"], args, videoInfo=infos, arts=arts, isFolder=False, properties=properties)
            elif 'tuningInstruction' in prog:
                data = {'mode': 'live'}
                if prog['tuningInstruction'] and not prog['mediasetstation$eventBased']:
                    vdata = prog['tuningInstruction']['urn:theplatform:tv:location:any']
                    for v in vdata:
                        if v['format'] == 'application/x-mpegURL':
                            data['id'] = v['releasePids'][0]
                        else:
                            data['mid'] = v['releasePids'][0]
                    kodiutils.addListItem(prog["title"], data, videoInfo=infos,
                                          arts=arts, isFolder=False)
            elif 'mediasetprogram$subBrandId' in prog:
                kodiutils.addListItem(prog["description"],
                                      {'mode': 'programma',
                                       'sub_brand_id': prog['mediasetprogram$subBrandId']},
                                      videoInfo=infos, arts=arts)
            elif 'mediasettvseason$brandId' in prog:
                # title = prog['title']
                # if 'mediasettvseason$displaySeason' in prog and  'mediasetprogram$seasonTitle' in prog:
                kodiutils.addListItem(prog["title"],
                                      {'mode': 'programma',
                                       'brand_id': prog['mediasettvseason$brandId']},
                                      videoInfo=infos, arts=arts)
            elif 'seriesId' in prog:
                title = prog['title']
                seriesTitle = prog['title']
                sort = 'tvSeasonNumber'
                order = 'asc'
                if 'mediasetprogram$pageUrl' in prog and 'programmi-tv' in str(prog['mediasetprogram$pageUrl'].encode('utf-8')).lower():
                    if 'mediasetprogram$seasonTitle' in prog and 'mediasetprogram$displaySeason' in prog:
                        seasonTitle = str(prog['mediasetprogram$seasonTitle'].encode('utf-8'))
                        displaySeason = str(prog['mediasetprogram$displaySeason'].encode('utf-8'))
                        seriesTitle = seasonTitle
                        title = seriesTitle
                        # if len(displaySeason)>0 and len(seasonTitle)>0 and not re.match("^.*(\d){4}$", seasonTitle):
                        #     title = '{} {}'.format(seasonTitle,displaySeason)
                        #     seriesTitle = seasonTitle
                        # elif len(seasonTitle)>0:
                        #     seriesTitle = seasonTitle
                        #     title = seriesTitle
                kodiutils.addListItem(title,
                                      {'mode': 'programma', 'series_id': prog['seriesId'],
                                       'sort': sort, 'order': order,
                                       'title': seriesTitle},
                                      videoInfo=infos, arts=arts)
            else:
                kodiutils.addListItem(prog["title"],
                                      {'mode': 'programma',
                                       'brand_id': prog['mediasetprogram$brandId']},
                                      videoInfo=infos, arts=arts)

    def root(self):
        kodiutils.addListItem('On Demand', {'mode': 'ondemand'})
        kodiutils.addListItem('TV', {'mode': 'tv'})
        kodiutils.addListItem('Play Cult', {'mode': 'cult'})
        kodiutils.addListItem(kodiutils.LANGUAGE(32107), {'mode': 'cerca'})
        kodiutils.addListItem('Le tue liste', {'mode': 'personal'})
        kodiutils.endScript()

    def elenco_cerca_root(self):
        kodiutils.addListItem(kodiutils.LANGUAGE(32115), {'mode': 'cerca', 'type': 'programmi'})
        kodiutils.addListItem(kodiutils.LANGUAGE(32116), {'mode': 'cerca', 'type': 'clip'})
        kodiutils.addListItem(kodiutils.LANGUAGE(32117), {'mode': 'cerca', 'type': 'episodi'})
        kodiutils.addListItem(kodiutils.LANGUAGE(32103), {'mode': 'cerca', 'type': 'film'})
        kodiutils.endScript()

    def apri_ricerca(self, sez):
        text = kodiutils.getKeyboardText(kodiutils.LANGUAGE(32131))
        self.elenco_cerca_sezione(sez, text, 1)

    def elenco_cerca_sezione(self, sez, text, page=None):
        switcher = {'programmi': 'CWSEARCHBRAND', 'clip': 'CWSEARCHCLIP',
                    'episodi': 'CWSEARCHEPISODE', 'film': 'CWSEARCHMOVIE'}
        sezcode = switcher.get(sez)
        if text:
            els, hasmore = self.med.Cerca(text, sezcode, pageels=self.iperpage, page=page)
            if els:
                exttitle = {'programmi': False, 'clip': True,
                            'episodi': True, 'film': False}
                self.__analizza_elenco(els, True, titlewd=exttitle.get(sez, False))
                if hasmore:
                    kodiutils.addListItem(kodiutils.LANGUAGE(32130),
                                          {'mode': 'cerca', 'search': text, 'type': sez,
                                           'page': page + 1 if page else 2})
        kodiutils.endScript()

    def elenco_ondemand_root(self):
        for item in self.med.OttieniOnDemand():
            kodiutils.addListItem(item["title"], {'mode': 'ondemand', 'id': item['_meta']['id']})
        kodiutils.endScript()

    def elenco_ondemand(self, id, template=None, sort=None, order='asc'):
        kodiutils.log(('template: {}').format(str(template)), 4)
        for sec in self.med.OttieniOnDemandGeneri(id, sort, order):
            if template and (('template' in sec and not str(sec['template']) in template.split('|')) or not 'template' in sec):
                continue
            if "uxReference" in sec:
                kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']})
            elif "newsFeedUrl" in sec:
                kodiutils.addListItem(sec["title"], {'mode': 'magazine', 'newsFeedUrl': sec['newsFeedUrl']})
            elif "feedurl" in sec:
                kodiutils.addListItem(sec["title"], {'mode': 'cult', 'feedurl': sec['feedurl']})
        # kodiutils.addListItem('Ordina {}'.format('DESC' if sort and order == 'asc' else 'ASC'), {
        #     'mode': 'ondemand',
        #     'id': id,
        #     'sort': sort if sort else 'title',
        #     'order': 'desc' if sort and order == 'asc' else 'asc'
        #     })
        kodiutils.endScript(closedir=True)

    def elenco_cult_root(self):
        kodiutils.addListItem('Home',{'mode': 'ondemand', 'id': '5dada71d23eec6001ba1a83b', 'template': 'video-mixed|playlist', 'sort': 'title'})
        kodiutils.addListItem('Tutti i Video', {'mode': 'ondemand', 'id': '5c0ff291a0e845001bb455bf', 'template': 'video-mixed|playlist', 'sort': 'title'})
        kodiutils.endScript()

    def elenco_cult(self, feedurl):
        els, nextPage = self.med.OttieniCult(feedurl)
        self.__analizza_elenco(els, True)
        if nextPage:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'cult', 'feedurl': nextPage})
        kodiutils.endScript()

    def elenco_magazine(self, newsFeedUrl):
        els, nextPage = self.med.OttieniMagazine(newsFeedUrl)
        for sec in els:
            if 'metainfo' in sec and 'ddg_url' in sec['metainfo']:
                kodiutils.addListItem(sec["title"], {'mode': 'magazine', 'ddg_url': sec['metainfo']['ddg_url']})
        if nextPage:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'magazine', 'newsFeedUrl': nextPage})
        kodiutils.endScript()

    def elenco_news(self, ddg_url):
        els = self.med.OttieniNews(ddg_url)
        self.__analizza_elenco(els)
        kodiutils.endScript()

    def elenco_sezione(self, id, page=1, sort=None, order='asc'):
        els, hasmore = self.med.OttieniProgrammiGenere(id, self.iperpage, page, sort, order)
        kodiutils.log('elenco_sezione {} {}: {}'.format(str(self.iperpage), str(hasmore), str(els)), 4)
        if els:
            self.__analizza_elenco(els, True)
            if hasmore:
                kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'sezione', 'id': id, 'page': int(page) + 1})
            # else:
            #     kodiutils.addListItem('Ordina {}'.format('DESC' if sort and order == 'asc' else 'ASC'), {
            #         'mode': 'sezione', 'id': id, 
            #         'sort': sort if sort else 'title',
            #         'order': 'desc' if sort and order == 'asc' else 'asc'})
        kodiutils.endScript()

    def elenco_stagioni_list(self, series_id, title, sort=None, order='asc'):
        els, _ = self.med.OttieniStagioni(series_id, sort, order)
        if len(els) == 1:
            self.elenco_sezioni_list(els[0]['mediasettvseason$brandId'])
        else:
            # workaround per controllare se è già una stagione e non una serie
            brandId = -1
            for el in els:
                kodiutils.log(('el: {}').format(str(el)), 4)
                if el['title'] == title:
                    brandId = el['mediasettvseason$brandId']
                    break
            kodiutils.log(('brandId: {}').format(str(brandId)), 4)
            if brandId == -1:
                self.__analizza_elenco(els)
                kodiutils.endScript()
            else:
                if sort:
                    kodiutils.addListItem('Tutte le Stagioni', {'mode': 'programma', 'series_id': series_id, 'title': '*', 'sort': sort, 'order': order})
                else:
                    kodiutils.addListItem('Tutte le Stagioni', {'mode': 'programma', 'series_id': series_id, 'title': '*'})
                self.elenco_sezioni_list(brandId)

    def elenco_sezioni_list(self, brandId):
        els, _ = self.med.OttieniSezioniProgramma(brandId, sort='mediasetprogram$order|asc')
        if len(els) == 2:
            self.elenco_video_list(els[1]['mediasetprogram$subBrandId'])
        else:
            els.pop(0)
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def elenco_video_list(self, sub_brand_id, mode='programma', sort='desc', page=0, size=0):
        if not size:
            size = self.iperpage
        els, hasMore = self.med.OttieniVideoSezione(
            sub_brand_id, sort='mediasetprogram$publishInfo_lastPublished|{}'.format(sort), page=page, size=size)
        self.__analizza_elenco(els, True)
        if hasMore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': mode, 'sub_brand_id': sub_brand_id, 'sort': sort, 'page': int(page)+1, 'size': size})
            # kodiutils.addListItem(kodiutils.LANGUAGE(32139), {'mode': mode, 'sub_brand_id': sub_brand_id, 'sort': 'desc' if sort=='asc' else 'asc', 'page': 0, 'size': size})
        kodiutils.endScript()

    def isAnon(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        return user == '' or password == ''

    def personal_root(self):
        if self.isAnon():
            kodiutils.showOkDialog('ATTENTION', 'Configurare Username e Password del proprio account Mediaset per accedere alla sezione personale di MediasetPlay')
            kodiutils.openSettings()
        if self.isAnon():
            self.root()
        else:
            kodiutils.addListItem('Continua a Guardare', {'mode': 'continuewatch'})
            kodiutils.addListItem('Preferiti', {'mode': 'favorites'})
            kodiutils.addListItem('Guarda Dopo', {'mode': 'watchlist'})
        kodiutils.endScript()

    def continuewatch(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if len(user) > 0 and len(password) > 0 and self.med.login(user, password):
            els, _ = self.med.OttieniContinuaGardare()
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def favorites(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if len(user) > 0 and len(password) > 0 and self.med.login(user, password):
            els, _ = self.med.OttieniFavoriti()
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def watchlist(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if len(user) > 0 and len(password) > 0 and self.med.login(user, password):
            els, _ = self.med.OttieniWatchlist()
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def tv_root(self):
        kodiutils.addListItem(kodiutils.LANGUAGE(32111), {'mode': 'canali_live'})
        kodiutils.addListItem(kodiutils.LANGUAGE(32113), {'mode': 'guida_tv'})
        kodiutils.endScript()
    
    def guida_tv_root(self):
        kodiutils.setContent('videos')
        els, _ = self.med.OttieniCanaliLive(sort='ShortTitle')
        for prog in els:
            kodiutils.log(('prog: {}').format(str(prog)), 4)
            infos = _gather_info(prog)
            arts = _gather_art(prog)
            if 'tuningInstruction' in prog:
                if prog['tuningInstruction'] and not prog['mediasetstation$eventBased']:
                    kodiutils.addListItem(prog["title"],
                                          {'mode': 'guida_tv', 'id': prog['callSign'],
                                           'week': staticutils.get_timestamp_midnight()},
                                          videoInfo=infos, arts=arts)
        kodiutils.endScript()

    def guida_tv_canale_settimana(self, cid, dt):
        dt = staticutils.get_date_from_timestamp(dt)
        for d in range(0, 16):
            currdate = dt - timedelta(days=d)
            kodiutils.addListItem(kodiutils.getFormattedDate(currdate),
                                  {'mode': 'guida_tv', 'id': cid,
                                   'day': staticutils.get_timestamp_midnight(currdate)})
        # kodiutils.addListItem(kodiutils.LANGUAGE(32136),
        #                       {'mode': 'guida_tv', 'id': cid,
        #                       'week': staticutils.get_timestamp_midnight(dt - timedelta(days=7))})
        kodiutils.endScript()

    def guida_tv_canale_giorno(self, cid, dt):
        res = self.med.OttieniGuidaTV(cid, dt, dt + 86399999)  # 86399999 is one day minus 1 ms
        if 'listings' in res:
            for el in res['listings']:
                if (kodiutils.getSettingAsBool('fullguide') or
                        ('mediasetprogram$hasVod' in el['program'] and
                         el['program']['mediasetprogram$hasVod'])):
                    infos = _gather_info(el)
                    arts = _gather_art(el)
                    s_time = staticutils.get_date_from_timestamp(
                        el['startTime']).strftime("%H:%M")
                    e_time = staticutils.get_date_from_timestamp(
                        el['endTime']).strftime("%H:%M")
                    s = "{s}-{e} - {t}".format(s=s_time, e=e_time,
                                               t=el['mediasetlisting$epgTitle'].encode('utf8'))
                    kodiutils.addListItem(s,
                                          {'mode': 'video', 'guid': el['program']['guid']},
                                          videoInfo=infos, arts=arts, isFolder=False)
        kodiutils.endScript()

    def canali_live_root(self):
        kodiutils.setContent('videos')
        now = staticutils.get_timestamp()
        els, _ = self.med.OttieniProgrammiLive()  # (sort='title')
        chans = {}
        for chan in els:
            if 'listings' in chan and chan['listings']:
                for prog in chan['listings']:
                    if prog['startTime'] <= now <= prog['endTime']:
                        guid = chan['guid']
                        chans[guid] = {'title': '{} - {}'.format(chan['title'],
                                                                 kodiutils.py2_encode(
                                                                     prog["mediasetlisting$epgTitle"])),
                                       'infos': _gather_info(prog),
                                       'arts': _gather_art(prog),
                                       'restartAllowed': prog['mediasetlisting$restartAllowed']}
        kodiutils.log(('chans: {}').format(str(chans)))
        els, _ = self.med.OttieniCanaliLive(sort='ShortTitle')
        for prog in els:
            if (prog['callSign'] in chans and 'tuningInstruction' in prog and
                    prog['tuningInstruction'] and (not prog['mediasetstation$eventBased'] or prog['mediasetstation$channelPool'])):
                chn = chans[prog['callSign']]
                if chn['arts'] == {}:
                    chn['arts'] = _gather_art(prog)
                if chn['restartAllowed']:
                    if kodiutils.getSettingAsBool('splitlive'):
                        kodiutils.addListItem(chn['title'], {'mode': 'live',
                                                             'guid': prog['callSign']},
                                              videoInfo=chn['infos'], arts=chn['arts'])
                        continue
                    vid = self.__ottieni_vid_restart(prog['callSign'])
                    if vid:
                        kodiutils.addListItem(chn['title'], {'mode': 'video', 'pid': vid},
                                              videoInfo=chn['infos'], arts=chn['arts'],
                                              isFolder=False)
                        continue
                data = {'mode': 'live'}
                vdata = prog['tuningInstruction']['urn:theplatform:tv:location:any']
                for v in vdata:
                    if v['format'] == 'application/x-mpegURL':
                        data['id'] = v['releasePids'][0]
                    else:
                        data['mid'] = v['releasePids'][0]
                kodiutils.addListItem(prog['title'], data,
                                      videoInfo=chn['infos'], arts=chn['arts'], isFolder=False)
        kodiutils.endScript()

    def __ottieni_vid_restart(self, guid):
        res = self.med.OttieniLiveStream(guid)
        if ('currentListing' in res[0] and
                res[0]['currentListing']['mediasetlisting$restartAllowed']):
            url = res[0]['currentListing']['restartUrl']
            return url.rpartition('/')[-1]
        return None

    def canali_live_play(self, guid):
        res = self.med.OttieniLiveStream(guid)
        infos = {}
        arts = {}
        title = ''
        if 'currentListing' in res[0]:
            self.__imposta_tipo_media(res[0]['currentListing']['program'])
            infos = _gather_info(res[0]['currentListing'])
            arts = _gather_art(res[0]['currentListing']['program'])
            title = ' - ' + infos['title']
        if 'tuningInstruction' in res[0]:
            data = {'mode': 'live'}
            vdata = res[0]['tuningInstruction']['urn:theplatform:tv:location:any']
            for v in vdata:
                if v['format'] == 'application/x-mpegURL':
                    data['id'] = v['releasePids'][0]
                else:
                    data['mid'] = v['releasePids'][0]
            kodiutils.addListItem(kodiutils.LANGUAGE(32137) + title, data, videoInfo=infos,
                                  arts=arts, isFolder=False)
        if ('currentListing' in res[0] and
                res[0]['currentListing']['mediasetlisting$restartAllowed']):
            url = res[0]['currentListing']['restartUrl']
            vid = url.rpartition('/')[-1]
            kodiutils.addListItem(kodiutils.LANGUAGE(32138) + title, {'mode': 'video', 'pid': vid},
                                  videoInfo=infos, arts=arts, isFolder=False)
        kodiutils.endScript()

    def riproduci_guid(self, guid):
        res = self.med.OttieniInfoDaGuid(guid)
        if not res or 'media' not in res:
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32136))
            kodiutils.setResolvedUrl(solved=False)
            return
        self.riproduci_video(guid=guid, pid=res['media'][0]['pid'])

    def riproduci_video(self, guid=None, pid=None, live=False):
        from inputstreamhelper import Helper  # pylint: disable=import-error
        kodiutils.log("Trying to get the video from pid %s" % pid)
        data = self.med.OttieniDatiVideo(pid, live)
        if data['type'] == 'video/mp4':
            kodiutils.setResolvedUrl(data['url'])
            return
        is_helper = Helper('mpd', 'com.widevine.alpha' if data['security'] else None)
        if not is_helper.check_inputstream():
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32133))
            kodiutils.setResolvedUrl(solved=False)
            return
        headers = '&User-Agent={useragent}'.format(
            useragent=self.ua)
        props = {'manifest_type': 'mpd', 'stream_headers': headers}
        properties = {}
        isAutenticated = False
        scrobbling = kodiutils.getSettingAsNum('scrobbling')
        if scrobbling:
            properties['guid'] = guid
            if scrobbling == 1:
                user = kodiutils.getSetting('email')
                password = kodiutils.getSetting('password')
                isAutenticated = self.med.login(user, password)
                if isAutenticated:
                    offset = self.med.getProgress(guid)
                    properties['offset'] = str(offset)

        if data['security']:
            if not isAutenticated:
                user = kodiutils.getSetting('email')
                password = kodiutils.getSetting('password')
                if user == '' or password == '':
                    kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32134))
                    kodiutils.setResolvedUrl(solved=False)
                    return
                if not self.med.login(user, password):
                    kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32135))
                    kodiutils.setResolvedUrl(solved=False)
                    return
            headers += '&Accept=*/*&Content-Type='
            props['license_type'] = 'com.widevine.alpha'
            props['stream_headers'] = headers
            url = self.med.OttieniWidevineAuthUrl(data['pid'])
            props['license_key'] = '{url}|{headers}|R{{SSM}}|'.format(url=url, headers=headers)

        headers = {'user-agent': self.ua,
                   't-apigw': self.med.apigw, 't-cts': self.med.cts}
        kodiutils.log("riproduci_video properties: %s" % properties)
        kodiutils.setResolvedUrl(data['url'], headers=headers, ins=is_helper.inputstream_addon,
                                 insdata=props,properties=properties)

    def sliceParams(self, params, keys):
        return {key:params[key] for key in set(keys) & set(params)}

    def main(self):
        # parameter values
        params = staticutils.getParams()
        if 'mode' in params:
            page = None
            if 'page' in params:
                try:
                    page = int(params['page'])
                except ValueError:
                    pass
            if params['mode'] == "cerca":
                if 'type' in params:
                    if 'search' in params:
                        self.elenco_cerca_sezione(params['type'], params['search'], page)
                    else:
                        self.apri_ricerca(params['type'])
                else:
                    self.elenco_cerca_root()
            if params['mode'] == "sezione":
                self.elenco_sezione(**self.sliceParams(params, ('id','page','sort','order')))
            if params['mode'] == "ondemand":
                if 'id' in params:
                    self.elenco_ondemand(**self.sliceParams(params, ('id','template','sort','order')))
                else:
                    self.elenco_ondemand_root()
            if params['mode'] == "cult":
                if 'feedurl' in params:
                    self.elenco_cult(params['feedurl'])
                else:
                    self.elenco_cult_root()
            if params['mode'] == "magazine":
                if 'newsFeedUrl' in params:
                    self.elenco_magazine(params['newsFeedUrl'])
                elif 'ddg_url' in params:
                    self.elenco_news(params['ddg_url'])
            if params['mode'] == "programma":
                if 'series_id' in params:
                    self.elenco_stagioni_list(**self.sliceParams(params, ('series_id','title','sort','order')))
                elif 'sub_brand_id' in params:
                    self.elenco_video_list(**self.sliceParams(params, ('sub_brand_id', 'mode', 'sort', 'page', 'size')))
                elif 'brand_id' in params:
                    self.elenco_sezioni_list(params['brand_id'])
            if params['mode'] == "video":
                if 'pid' in params:
                    self.riproduci_video(**self.sliceParams(params, ('guid','pid','offset')))
                else:
                    self.riproduci_guid(**self.sliceParams(params, ('guid','offset')))
            if params['mode'] == "live":
                if 'id' in params:
                    self.riproduci_video(pid=params['id'], live=True)
                else:
                    self.canali_live_play(params['guid'])
            if params['mode'] == "tv":
                self.tv_root()
            if params['mode'] == "personal":
                self.personal_root()
            elif params['mode'] == "continuewatch":
                self.continuewatch()
            elif params['mode'] == "favorites":
                self.favorites()
            elif params['mode'] == "watchlist":
                self.watchlist()
            if params['mode'] == "canali_live":
                self.canali_live_root()
            if params['mode'] == "guida_tv":
                if 'id' in params:
                    if 'week' in params:
                        self.guida_tv_canale_settimana(params['id'], int(params['week']))
                    elif 'day' in params:
                        self.guida_tv_canale_giorno(params['id'], int(params['day']))
                self.guida_tv_root()
        else:
            self.root()
