# -*- coding: utf-8 -*-
from datetime import timedelta
from resources.lib.mediaset import Mediaset
from resources.mediaset_datahelper import _gather_info, _gather_art, _gather_media_type
from phate89lib import kodiutils, staticutils  # pylint: disable=import-error


class KodiMediaset(object):

    contextMenuMap = {'favorites': 'Favoriti', 'watchlist': 'Guarda Dopo', 'continuewatch':  'Continua Guardare'}
    ADDON_SCROBBLING_CUSTOM = 1
    ADDON_SCROBBLING_NONE = 0

    def __init__(self):
        self.med = Mediaset()
        self.med.log = kodiutils.log
        self.iperpage = kodiutils.getSetting('itemsperpage')
        self.detect_media_type = kodiutils.getSettingAsBool('detectmediatype')
        self.lookup_fullplot = kodiutils.getSettingAsBool('lookupfullplot')
        self.isAnonimous = self.checkCredentials()
        self.ua = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')

    def __imposta_tipo_media(self, prog):
        kodiutils.log('__analizza_elenco mediatype: {}'.format(_gather_media_type(prog)))
        if self.detect_media_type:
            kodiutils.setContent(_gather_media_type(prog) + 's')

    def __geItemtArt(self, icon='notify.png', poster='', fanart='fanart.jpg'):
        if not poster:
            poster = icon
        art = {}
        art["thumb"] = kodiutils.getMedia(icon)
        art["icon"] = kodiutils.getMedia(icon)
        art["poster"] = kodiutils.getMedia(poster)
        art["banner"] = kodiutils.getMedia(poster)
        art["landscape"] = kodiutils.getMedia(fanart)
        art["fanart"] = kodiutils.getMedia(fanart)
        art["clearart"] = kodiutils.getMedia(fanart)
        art["clearlogo"] = kodiutils.getMedia(poster)
        return art

    def __getDirectoryArt(self):
        return self.__geItemtArt("notify.png")

    def __getForwardArt(self):
        return self.__geItemtArt("forward.png")

    def __getBackwardArt(self):
        return self.__geItemtArt("backward.png")

    def __getFavouriteArt(self):
        return self.__geItemtArt("favourite.png")

    def __getWatchlaterArt(self):
        return self.__geItemtArt("watchlater.png")

    def __getContinueArt(self):
        return self.__geItemtArt("continue.png")

    def checkCredentials(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        return user == '' or password == ''

    def __analizza_elenco(self, progs, setcontent=False, titlewd=False, isDeletable=False, delete_list='', context_ui=''):
        if not progs:
            return
        if setcontent:
            self.__imposta_tipo_media(progs[0])
        defaultArt = self.__getDirectoryArt()
        for prog in progs:
            infos = _gather_info(prog, titlewd=titlewd, lookup_fullplot=self.lookup_fullplot)
            arts = _gather_art(prog) or defaultArt
            kodiutils.log('__analizza_elenco infos: {}'.format(infos))
            kodiutils.log('__analizza_elenco arts: {}'.format(arts))
            item_id = ''
            guid = ''
            args = {}
            properties = {}
            if 'media' in prog:
                kodiutils.log('__analizza_elenco media: {}'.format(str(prog)), 4)
                args['mode'] = 'video'
                # salta se non ha un media ma ha il tag perchè non riproducibile
                if prog['media']:
                    media = prog['media'][0]
                    if 'position' in prog:
                        args['offset'] = prog['position']
                    if 'pid' in media:
                        args['pid'] = media['pid']
                    elif 'publicUrl' in media:
                        args['pid'] = media['publicUrl'].split('/')[-1]
                    if 'guid' in media:
                        args['guid'] = media['guid']
                        guid = media['guid']
                    if 'mediasetprogram$duration' in prog:
                        properties['TotalTime'] = str(prog['mediasetprogram$duration'])
                    if 'mediasetprogram$brandId' in prog:
                        item_id = prog['mediasetprogram$brandId']
                    properties['ResumeTime'] = '0.0'
                    menuItems = self.menuItems(isDeletable=isDeletable, delete_list=delete_list, item_id=item_id, guid=guid, context_ui=context_ui)
                    kodiutils.addListItem(infos["title"], args, videoInfo=infos, arts=arts, isFolder=False, properties=properties, menuItems=menuItems)
            elif 'tuningInstruction' in prog:
                kodiutils.log('__analizza_elenco tuningInstruction: {}'.format(str(prog)), 4)
                args['mode'] = 'live'
                if prog['tuningInstruction'] and not prog['mediasetstation$eventBased']:
                    vdata = prog['tuningInstruction']['urn:theplatform:tv:location:any']
                    for v in vdata:
                        if v['format'] == 'application/x-mpegURL':
                            args['id'] = v['releasePids'][0]
                        else:
                            args['mid'] = v['releasePids'][0]
                    kodiutils.addListItem(prog["title"], args, videoInfo=infos, arts=arts, isFolder=False)
            elif 'mediasetprogram$subBrandId' in prog:
                kodiutils.log('__analizza_elenco subBrandId: {}'.format(str(prog)), 4)
                item_id = prog['mediasetprogram$brandId'] if prog['mediasetprogram$brandId'] else ''
                args['mode'] = 'programma'
                args['sub_brand_id'] = prog['mediasetprogram$subBrandId']
                menuItems = self.menuItems(isDeletable=isDeletable, delete_list=delete_list, item_id=item_id, guid=guid, context_ui=context_ui)
                kodiutils.addListItem(prog["description"], args, videoInfo=infos, arts=arts, menuItems=menuItems)
            elif 'mediasettvseason$brandId' in prog:
                kodiutils.log('__analizza_elenco brandId: {}'.format(str(prog)), 4)
                # title = prog['title']
                # if 'mediasettvseason$displaySeason' in prog and  'mediasetprogram$seasonTitle' in prog:
                item_id = prog['mediasettvseason$brandId'] if prog['mediasettvseason$brandId'] else ''
                args['mode'] = 'programma'
                args['brand_id'] = prog['mediasettvseason$brandId']
                menuItems = self.menuItems(isDeletable=isDeletable, delete_list=delete_list, item_id=item_id, guid=guid, context_ui=context_ui)
                kodiutils.addListItem(prog["title"], args, videoInfo=infos, arts=arts, menuItems=menuItems)
            elif 'seriesId' in prog:
                kodiutils.log('__analizza_elenco seriesId: {}'.format(str(prog)), 4)
                title = prog['title']
                seriesTitle = prog['title']
                sort = 'tvSeasonNumber'
                order = 'asc'
                item_id = prog['mediasetprogram$brandId'] if prog['mediasetprogram$brandId'] else ''
                if 'mediasetprogram$pageUrl' in prog and 'programmi-tv' in str(prog['mediasetprogram$pageUrl'].encode('utf-8')).lower():
                    if 'mediasetprogram$seasonTitle' in prog and 'mediasetprogram$displaySeason' in prog:
                        seasonTitle = str(prog['mediasetprogram$seasonTitle'].encode('utf-8'))
                        # displaySeason = str(prog['mediasetprogram$displaySeason'].encode('utf-8'))
                        seriesTitle = seasonTitle
                        title = seriesTitle
                args['mode'] = 'programma'
                args['series_id'] = prog['seriesId']
                args['sort'] = sort
                args['order'] = order
                args['title'] = seriesTitle
                menuItems = self.menuItems(isDeletable=isDeletable, delete_list=delete_list, item_id=item_id, guid=guid, context_ui=context_ui)
                kodiutils.addListItem(title, args, videoInfo=infos, arts=arts, menuItems=menuItems)
            else:
                kodiutils.log('__analizza_elenco other: {}'.format(str(prog)), 4)
                item_id = prog['mediasetprogram$brandId'] if prog['mediasetprogram$brandId'] else ''
                args['mode'] = 'programma'
                args['brand_id'] = prog['mediasetprogram$brandId']
                menuItems = self.menuItems(isDeletable=isDeletable, delete_list=delete_list, item_id=item_id, guid=guid, context_ui=context_ui)
                kodiutils.addListItem(prog["title"], args, videoInfo=infos, arts=arts, menuItems=menuItems)

    def menuItems(self, isDeletable=False, delete_list='', item_id='', guid='', context_ui=''):
        kodiutils.log('menuItems: isDeletable={},delete_list={},item_id={},guid={},context_ui={}'.format(isDeletable,delete_list,item_id,guid,context_ui))
        menuItems = []
        if self.isAnonimous:
            return menuItems
        if isDeletable:
            if delete_list=='favorites' and item_id:
                menuItems.append(('Rimuovi (MediasetPlay)', "RunPlugin(plugin://{}/?mode=contextmenu&context_menu={}&context_action=del&context_id={}&context_ui={})".format(kodiutils.ID,delete_list,item_id,context_ui)))
            elif delete_list=='watchlist' and guid:
                menuItems.append(('Rimuovi (MediasetPlay)', "RunPlugin(plugin://{}/?mode=contextmenu&context_menu={}&context_action=del&context_id={}&context_ui={})".format(kodiutils.ID,delete_list,guid,context_ui)))
        else:
            if guid:
                menuItems.append(('Guarda Dopo (MediasetPlay)', "RunPlugin(plugin://{}/?mode=contextmenu&context_menu=watchlist&context_action=add&context_id={}&context_ui={})".format(kodiutils.ID,guid,context_ui)))
            elif item_id:
                menuItems.append(('Preferiti (MediasetPlay)', "RunPlugin(plugin://{}/?mode=contextmenu&context_menu=favorites&context_action=add&context_id={}&context_ui={})".format(kodiutils.ID,item_id,context_ui)))
        return menuItems

    def root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem('On Demand', {'mode': 'ondemand'}, arts=arts)
        kodiutils.addListItem('TV', {'mode': 'tv'}, arts=arts)
        kodiutils.addListItem('Play Cult', {'mode': 'cult'}, arts=arts)
        kodiutils.addListItem(kodiutils.LANGUAGE(32107), {'mode': 'cerca'}, arts=arts)
        kodiutils.addListItem('Le tue liste', {'mode': 'personal'}, arts=arts)
        kodiutils.endScript()

    def elenco_cerca_root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem(kodiutils.LANGUAGE(32115), {'mode': 'cerca', 'type': 'programmi'}, arts=arts)
        kodiutils.addListItem(kodiutils.LANGUAGE(32116), {'mode': 'cerca', 'type': 'clip'}, arts=arts)
        kodiutils.addListItem(kodiutils.LANGUAGE(32117), {'mode': 'cerca', 'type': 'episodi'}, arts=arts)
        kodiutils.addListItem(kodiutils.LANGUAGE(32103), {'mode': 'cerca', 'type': 'film'}, arts=arts)
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
                if hasmore:
                    kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'cerca', 'search': text, 'type': sez, 'page': page + 1 if page else 2}, properties={'SpecialSort': 'top'}, arts=self.__getForwardArt())
                exttitle = {'programmi': False, 'clip': True,
                            'episodi': True, 'film': False}
                self.__analizza_elenco(els, titlewd=exttitle.get(sez, False))
        kodiutils.endScript()

    def elenco_ondemand_root(self):
        arts = self.__getDirectoryArt()
        for item in self.med.OttieniOnDemand():
            kodiutils.addListItem(item["title"], {'mode': 'ondemand', 'id': item['_meta']['id']}, arts=arts)
        kodiutils.endScript()

    def elenco_ondemand(self, id, template=None, sort='', order='asc'):
        kodiutils.log(('elenco_ondemand: id={},template={},sort={},order={}').format(str(id),str(template),str(sort),str(order)), 4)
        arts = self.__getDirectoryArt()
        for sec in self.med.OttieniOnDemandGeneri(id, sort, order):
            if template and (('template' in sec and not str(sec['template']) in template.split('|')) or not 'template' in sec):
                continue
            if "uxReference" in sec:
                kodiutils.log(('elenco_ondemand uxReference: {}').format(str(sec)), 4)
                kodiutils.addListItem(sec["title"], {'mode': 'sezione', 'id': sec['uxReference']}, arts=arts)
            elif "newsFeedUrl" in sec:
                kodiutils.log(('elenco_ondemand newsFeedUrl: {}').format(str(sec)), 4)
                kodiutils.addListItem(sec["title"], {'mode': 'magazine', 'newsFeedUrl': sec['newsFeedUrl']}, arts=arts)
            elif "feedurl" in sec:
                kodiutils.log(('elenco_ondemand feedurl: {}').format(str(sec)), 4)
                kodiutils.addListItem(sec["title"], {'mode': 'cult', 'feedurl': sec['feedurl']}, arts=arts)
        # kodiutils.addListItem('Ordina {}'.format('DESC' if sort and order == 'asc' else 'ASC'), {
        #     'mode': 'ondemand',
        #     'id': id,
        #     'sort': sort if sort else 'title',
        #     'order': 'desc' if sort and order == 'asc' else 'asc'
        #     })
        kodiutils.endScript(closedir=True)

    def elenco_cult_root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem('Home',{'mode': 'ondemand', 'id': '5dada71d23eec6001ba1a83b', 'template': 'video-mixed|playlist', 'sort': 'title'}, arts=arts)
        kodiutils.addListItem('Tutti i Video', {'mode': 'ondemand', 'id': '5c0ff291a0e845001bb455bf', 'template': 'video-mixed|playlist', 'sort': 'title'}, arts=arts)
        kodiutils.endScript()

    def elenco_cult(self, feedurl, page_action=""):
        els, nextPage, prevPage = self.med.OttieniCult(feedurl, self.iperpage)
        update_listing = (page_action=='next' or page_action=='prev')
        kodiutils.log(('elenco_cult: {}').format(str(update_listing)), 4)
        if nextPage:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'cult', 'feedurl': nextPage, 'page_action': 'next'}, properties={'SpecialSort': 'top'}, arts=self.__getForwardArt())
        if prevPage:
            kodiutils.addListItem(kodiutils.LANGUAGE(32129), {'mode': 'cult', 'feedurl': prevPage, 'page_action': 'prev'}, properties={'SpecialSort': 'top'}, arts=self.__getBackwardArt())
        self.__analizza_elenco(els, True)
        kodiutils.endScript(update_listing=update_listing)

    def elenco_magazine(self, newsFeedUrl, page_action=""):
        arts = self.__getDirectoryArt()
        els, nextPage, prevPage = self.med.OttieniMagazine(newsFeedUrl, self.iperpage)
        update_listing = (page_action=='next' or page_action=='prev')
        if nextPage:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'magazine', 'newsFeedUrl': nextPage, 'page_action': 'next'}, properties={'SpecialSort': 'top'}, arts=self.__getForwardArt())
        if prevPage:
            kodiutils.addListItem(kodiutils.LANGUAGE(32129), {'mode': 'magazine', 'newsFeedUrl': prevPage, 'page_action': 'prev'}, properties={'SpecialSort': 'top'}, arts=self.__getBackwardArt())
        for sec in els:
            if 'metainfo' in sec and 'ddg_url' in sec['metainfo']:
                kodiutils.addListItem(sec["title"], {'mode': 'magazine', 'ddg_url': sec['metainfo']['ddg_url']}, arts=arts)
        kodiutils.log(('update_listing: {}').format(str(update_listing)), 4)
        kodiutils.endScript(update_listing=update_listing)

    def elenco_news(self, ddg_url):
        els = self.med.OttieniNews(ddg_url)
        self.__analizza_elenco(els, True)
        kodiutils.endScript()

    def elenco_sezione(self, id, page=0, sort='mediasetprogram$seasonTitle', order='asc', size=20):
        kodiutils.log("[main] elenco_sezione: id={},page={},sort={},order={}".format(str(id),str(page),str(sort),str(order)))
        els, hasmore = self.med.OttieniProgrammiGenere(id, size, page, sort, order)
        kodiutils.log('elenco_sezione size={},hasmore={}: {}'.format(str(size), str(hasmore), str(els)), 4)
        update_listing = int(page) > 0 if page else False
        page = int(page) if page else 1
        if els:
            if hasmore:
                kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': 'sezione', 'id': id, 'page': page + 1}, properties={'SpecialSort': 'top'}, arts=self.__getForwardArt())
            if page>1:
                kodiutils.addListItem(kodiutils.LANGUAGE(32129), {'mode': 'sezione', 'id': id, 'page': page - 1}, properties={'SpecialSort': 'top'}, arts=self.__getBackwardArt())
            self.__analizza_elenco(els, True)
            # else:
            #     kodiutils.addListItem('Ordina {}'.format('DESC' if sort and order == 'asc' else 'ASC'), {
            #         'mode': 'sezione', 'id': id, 
            #         'sort': sort if sort else 'title',
            #         'order': 'desc' if sort and order == 'asc' else 'asc'})
        kodiutils.endScript(update_listing=update_listing)

    def elenco_stagioni_list(self, series_id, title, sort=None, order='asc'):
        title = kodiutils.py2_encode(title)
        kodiutils.log("[main] elenco_stagioni_list: series_id={},title={},sort={},order={}".format(series_id,title,sort,order))
        els, _ = self.med.OttieniStagioni(series_id, sort, order)
        if len(els) == 1:
            self.elenco_sezioni_list(els[0]['mediasettvseason$brandId'])
        else:
            # workaround per controllare se è già una stagione e non una serie
            brandId = -1
            for el in els:
                kodiutils.log(('el: {}').format(str(el)), 4)
                if kodiutils.py2_encode(el['title']) == title:
                    brandId = el['mediasettvseason$brandId']
                    break
            kodiutils.log(('brandId: {}').format(str(brandId)), 4)
            if brandId == -1:
                self.__analizza_elenco(els)
                kodiutils.endScript()
            else:
                if sort:
                    kodiutils.addListItem('Tutte le Stagioni', {'mode': 'programma', 'series_id': series_id, 'title': '*', 'sort': sort, 'order': order}, properties={'SpecialSort': 'top'}, arts=self.__getDirectoryArt())
                else:
                    kodiutils.addListItem('Tutte le Stagioni', {'mode': 'programma', 'series_id': series_id, 'title': '*'}, properties={'SpecialSort': 'top'}, arts=self.__getDirectoryArt())
                self.elenco_sezioni_list(brandId)

    def elenco_sezioni_list(self, brandId, sort='mediasetprogram$order|asc'):
        kodiutils.log("[main] elenco_sezioni_list: brandId={},sort={}".format(str(brandId),str(sort)))
        els, _ = self.med.OttieniSezioniProgramma(brandId, sort=sort)
        if len(els) == 2:
            self.elenco_video_list(els[1]['mediasetprogram$subBrandId'])
        else:
            els.pop(0)
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def elenco_video_list(self, sub_brand_id, mode='programma', sort='', page=0, size=0):
        kodiutils.log("[main] elenco_video_list: sub_brand_id={},mode={},sort={},page={},size={}".format(str(sub_brand_id),str(mode),str(sort),str(page),str(size)))
        # sort = 'mediasetprogram$publishInfo_lastPublished|{}'.format(order)
        page = int(page)
        size = int(size)
        update_listing = (page > 0)
        page = page if page else 1
        if not size:
            size = self.iperpage
        els, hasMore = self.med.OttieniVideoSezione(sub_brand_id, sort=sort, page=page, size=size)
        if hasMore:
            kodiutils.addListItem(kodiutils.LANGUAGE(32130), {'mode': mode, 'sub_brand_id': sub_brand_id, 'sort': sort, 'page': page+1, 'size': size}, properties={'SpecialSort': 'top'}, arts=self.__getForwardArt())
        if page>1:
            kodiutils.addListItem(kodiutils.LANGUAGE(32129), {'mode': mode, 'sub_brand_id': sub_brand_id, 'sort': sort, 'page': page-1, 'size': size}, properties={'SpecialSort': 'top'}, arts=self.__getBackwardArt())
        self.__analizza_elenco(els, True)
        kodiutils.endScript(update_listing=update_listing)

    def personal_root(self):
        if self.isAnonimous:
            kodiutils.showOkDialog('ATTENTION', 'Configurare Username e Password del proprio account Mediaset per accedere alla sezione personale di MediasetPlay')
            kodiutils.openSettings()
        if self.isAnonimous:
            self.root()
        else:
            kodiutils.addListItem('Continua a Guardare', {'mode': 'continuewatch'}, arts=self.__getContinueArt())
            kodiutils.addListItem('Preferiti', {'mode': 'favorites'}, arts=self.__getFavouriteArt())
            kodiutils.addListItem('Guarda Dopo', {'mode': 'watchlist'}, arts=self.__getWatchlaterArt())
        kodiutils.endScript()

    def continuewatch(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if user and password and self.med.login(user, password):
            els, _ = self.med.OttieniContinuaGardare()
            self.__analizza_elenco(els) 
        kodiutils.endScript()

    def favorites(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if user and password and self.med.login(user, password):
            els, _ = self.med.OttieniFavoriti()
            self.__analizza_elenco(els, isDeletable=True, delete_list='favorites', context_ui='refresh')
        kodiutils.endScript()

    def watchlist(self):
        user = kodiutils.getSetting('email')
        password = kodiutils.getSetting('password')
        if user and password and self.med.login(user, password):
            els, _ = self.med.OttieniWatchlist()
            self.__analizza_elenco(els, isDeletable=True, delete_list='watchlist', context_ui='refresh')
        kodiutils.endScript()

    def contextMenu(self, context_menu, context_action, context_id, context_ui=''):
        deleted = False
        added = False
        with kodiutils.busy_dialog():
            if context_menu and context_action and context_id:
                if context_menu and context_action and context_id:
                    user = kodiutils.getSetting('email')
                    password = kodiutils.getSetting('password')
                    if user and password and self.med.login(user, password):
                        if context_action=='add':
                            added = self.med.AggiungiLista(context_menu, context_id)
                        elif context_action=='del':
                            deleted = self.med.EliminaLista(context_menu, context_id)
        if added:
            kodiutils.notify('Aggiunto a {}'.format(self.contextMenuMap[context_menu]), icon=kodiutils.getMedia('notify.png'))
        elif deleted:
            kodiutils.notify('Rimosso da {}'.format(self.contextMenuMap[context_menu]), icon=kodiutils.getMedia('notify.png'))
        update_dir = context_ui=='refresh' and (added or deleted)
        kodiutils.endScript(closedir=False, update_dir=update_dir)

    def tv_root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem(kodiutils.LANGUAGE(32111), {'mode': 'canali_live'}, arts=arts)
        kodiutils.addListItem(kodiutils.LANGUAGE(32113), {'mode': 'guida_tv'}, arts=arts)
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
        kodiutils.setContent('videos')
        if 'listings' in res:
            for el in res['listings']:
                program = el['program'] if 'program' in el else {}
                if (kodiutils.getSettingAsBool('fullguide') or
                        ('mediasetprogram$hasVod' in program and program['mediasetprogram$hasVod'])):
                    infos = _gather_info(el)
                    arts = _gather_art(el)
                    s_time = staticutils.get_date_from_timestamp(
                        el['startTime']).strftime("%H:%M")
                    e_time = staticutils.get_date_from_timestamp(
                        el['endTime']).strftime("%H:%M")
                    s = "{s}-{e} - {t}".format(s=s_time, e=e_time,
                                               t=el['mediasetlisting$epgTitle'].encode('utf8'))
                    kodiutils.addListItem(s,
                                          {'mode': 'video', 'guid': program['guid']},
                                          videoInfo=infos, arts=arts, properties={'ResumeTime': '0.0', 'TotalTime': '0.0', 'StartOffset': '0.0'}, isFolder=False)
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
                                              videoInfo=chn['infos'], arts=chn['arts'], properties={'ResumeTime': '0.0'},
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
                                  arts=arts, properties={'ResumeTime': '0.0'}, isFolder=False)
        if ('currentListing' in res[0] and
                res[0]['currentListing']['mediasetlisting$restartAllowed']):
            url = res[0]['currentListing']['restartUrl']
            vid = url.rpartition('/')[-1]
            kodiutils.addListItem(kodiutils.LANGUAGE(32138) + title, {'mode': 'video', 'pid': vid},
                                  videoInfo=infos, arts=arts, properties={'ResumeTime': '0.0'}, isFolder=False)
        kodiutils.endScript()

    def riproduci_guid(self, guid='', offset=None):
        kodiutils.log('riproduci_guid: guid={}, offset={}'.format(guid,offset))
        res = self.med.OttieniInfoDaGuid(guid)
        if not res or 'media' not in res:
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32136))
            kodiutils.setResolvedUrl(solved=False)
            return
        self.riproduci_video(guid=guid, pid=res['media'][0]['pid'], offset=offset)

    def riproduci_video(self, guid=None, pid=None, live=False, offset=None):
        from inputstreamhelper import Helper  # pylint: disable=import-error
        # kodiutils.log("Trying to get the video from pid %s" % pid)
        kodiutils.log('riproduci_video: guid={}, pid={}, live={}, offset={}'.format(guid,pid,live,offset))
        data = self.med.OttieniDatiVideo(pid, live)
        kodiutils.log('riproduci_video: data={}'.format(str(data)))
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
        properties = {'ResumeTime': '0.0'}
        isAutenticated = False
        scrobbling = kodiutils.getSettingAsNum('scrobbling')
        if scrobbling and not self.isAnonimous:
            properties['guid'] = guid
            if scrobbling == self.ADDON_SCROBBLING_CUSTOM:
                if offset:
                    properties['offset'] = str(offset)
                else:
                    user = kodiutils.getSetting('email')
                    password = kodiutils.getSetting('password')
                    isAutenticated = self.med.login(user, password)
                    if isAutenticated:
                        offset = self.med.getProgress(guid)
                        if offset:
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
        kodiutils.log("[main] params: {}".format(str(params)))
        if 'mode' in params:
            page = None
            if 'page' in params:
                try:
                    page = int(params['page'])
                except ValueError:
                    pass
            self.iperpage = min(kodiutils.getSettingAsNum('itemsperpage'), 10)
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
                    self.elenco_cult(**self.sliceParams(params, ('feedurl','page_action')))
                else:
                    self.elenco_cult_root()
            if params['mode'] == "magazine":
                if 'newsFeedUrl' in params:
                    self.elenco_magazine(**self.sliceParams(params, ('newsFeedUrl','page_action')))
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
            elif params['mode'] == "contextmenu":
                self.contextMenu(**self.sliceParams(params, ('context_menu','context_action','context_id','context_ui')))
            elif params['mode'] == "canali_live":
                self.canali_live_root()
            elif params['mode'] == "guida_tv":
                if 'id' in params:
                    if 'week' in params:
                        self.guida_tv_canale_settimana(params['id'], int(params['week']))
                    elif 'day' in params:
                        self.guida_tv_canale_giorno(params['id'], int(params['day']))
                self.guida_tv_root()
        else:
            self.root()
