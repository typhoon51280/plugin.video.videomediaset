import time
import uuid
import xml.etree.ElementTree as ET
from phate89lib import kodiutils, rutils, staticutils  # pyright: reportMissingImports=false
try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote


class Mediaset(rutils.RUtils):

    USERAGENT = "VideoMediaset Kodi Addon"
    # USERAGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    #                '(KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36')

    def __init__(self):
        self.__UID = ''
        self.__UIDSignature = ''
        self.__signatureTimestamp = ''
        self.apigw = ''
        self.cts = ''
        self.__tracecid = ''
        self.__cwid = ''
        self.__deviceid = str(uuid.uuid4())
        self.expires_at = 0.0
        self.uxReferenceMapping = {
            'CWDOCUBIOSTORIE': 'documentariBioStoria',
            'CWDOCUINCHIESTE': 'documentariInchiesta',
            'CWDOCUMOSTRECENT': 'mostRecentDocumentariFep',
            'CWDOCUNATURANIMALI': 'documentariNatura',
            'CWDOCUSCIENZATECH': 'documentariScienza',
            'CWDOCUSPAZIO': 'documentariSpazio',
            'CWDOCUTOPVIEWED': 'stagioniDocumentari',
            'CWENABLERKIDS': 'stagioniKids',
            'CWFICTIONADVENTURE': 'stagioniFictionAvventura',
            'CWFICTIONBIOGRAPHICAL': 'stagioniFictionBiografico',
            'CWFICTIONCOMEDY': 'stagioniFictionCommedia',
            'CWFICTIONDRAMATIC': 'stagioniFictionDrammatico',
            'CWFICTIONPOLICE': 'stagioniFictionPoliziesco',
            'CWFICTIONSENTIMENTAL': 'stagioniFictionSentimentale',
            'CWFICTIONSITCOM': 'stagioniFictionSitCom',
            'CWFICTIONSOAP': 'mostRecentSoapOpera',
            'CWFILMACTION': 'filmAzioneThrillerAvventura',
            'CWFILMCLASSIC': 'filmClassici',
            'CWFILMCOMEDY': 'filmCommedia',
            'CWFILMDOCU': 'filmDocumentario',
            'CWFILMDRAMATIC': 'filmDrammatico',
            'CWFILMSENTIMENTAL': 'filmSentimentale',
            'CWFILMTOPVIEWED': 'filmPiuVisti24H',
            'CWHOMEBRANDS': 'personToContentHomepage',
            'CWHOMEFICTIONNOWELITE': 'stagioniFictionSerieTvSezione',
            'CWHOMEFICTIONNOWPOP': 'stagioniFictionSerieTvHomepage',
            'CWHOMEPROGTVNOW': 'stagioniProgrammiTv',
            'CWKIDSBOINGFORYOU': 'kidsBoing',
            'CWKIDSCARTOONITO': 'kidsCartoonito',
            'CWKIDSMEDIASETBRAND': 'kidsMediaset',
            'CWPROGTVDAY': 'stagioniDaytime',
            'CWPROGTVMAGAZINE': 'stagioniCucinaLifestyle',
            'CWPROGTVPRIME': 'stagioniPrimaSerata',
            'CWPROGTVSPORT': 'mostRecentSport',
            'CWPROGTVTALENT': 'stagioniReality',
            'CWPROGTVTALK': 'stagioniTalk',
            'CWPROGTVTG': 'mostRecentTg',
            'CWPROGTVTOPVIEWED': 'programmiTvClip24H',
            'CWPROGTVVARIETY': 'stagioniVarieta',
            'CWSEARCHBRAND': 'searchStagioni',
            'CWSEARCHCLIP': 'searchClip',
            'CWSEARCHEPISODE': 'searchEpisodi',
            'CWSEARCHMOVIE': 'searchMovie',
            'CWSIMILARDOCUMENTARI': 'similarDocumentari',
            'CWSIMILARFICTION': 'similarSerieTvFiction',
            'CWSIMILARFILM': 'similarCinema',
            'CWSIMILARINFORMAZIONE': 'similarInformazione',
            'CWSIMILARINTRATTENIMENTO': 'similarIntrattenimento',
            'CWSIMILARKIDS': 'similarCartoni',
            'CWSIMILARSERIETV': 'similarSerieTvFiction',
            'CWSIMILARSPORT': 'similarSport',
            'CWSIMILARTG': 'similarTg',
            'CWTOPSEARCHBRAND': 'defaultSearchStagioni',
            'CWTOPSEARCHCLIP': 'defaultSearchVideo',
            'CWTOPVIEWEDDAY': 'piuVisti24H',
            'documentariBioStoria': 'documentariBioStoria',
            'documentariInchiesta': 'documentariInchiesta',
            'documentariNatura': 'documentariNatura',
            'documentariScienza': 'documentariScienza',
            'documentariSpazio': 'documentariSpazio',
            'filmAzioneThrillerAvventura': 'filmAzioneThrillerAvventura',
            'filmClassici': 'filmClassici',
            'filmCommedia': 'filmCommedia',
            'filmDocumentario': 'filmDocumentario',
            'filmDrammatico': 'filmDrammatico',
            'filmPiuVisti24H': 'filmPiuVisti24H',
            'filmSentimentale': 'filmSentimentale',
            'kidsBoing': 'kidsBoing',
            'kidsCartoonito': 'kidsCartoonito',
            'kidsMediaset': 'kidsMediaset',
            'mostRecentDocumentariFep': 'mostRecentDocumentariFep',
            'mostRecentSoapOpera': 'mostRecentSoapOpera',
            'mostRecentSport': 'mostRecentSport',
            'mostRecentTg': 'mostRecentTg',
            'personToContentFilm': 'personToContentFilm',
            'personToContentHomepage': 'personToContentHomepage',
            'piuVisti24H': 'piuVisti24H',
            'programmiTvClip24H': 'programmiTvClip24H',
            'similarCartoni': 'similarCartoni',
            'similarCinema': 'similarCinema',
            'similarDocumentari': 'similarDocumentari',
            'similarInformazione': 'similarInformazione',
            'similarIntrattenimento': 'similarIntrattenimento',
            'similarSerieTvFiction': 'similarSerieTvFiction',
            'similarSport': 'similarSport',
            'similarTg': 'similarTg',
            'stagioniCucinaLifestyle': 'stagioniCucinaLifestyle',
            'stagioniDaytime': 'stagioniDaytime',
            'stagioniDocumentari': 'stagioniDocumentari',
            'stagioniFictionAvventura': 'stagioniFictionAvventura',
            'stagioniFictionBiografico': 'stagioniFictionBiografico',
            'stagioniFictionCommedia': 'stagioniFictionCommedia',
            'stagioniFictionDrammatico': 'stagioniFictionDrammatico',
            'stagioniFictionPoliziesco': 'stagioniFictionPoliziesco',
            'stagioniFictionSentimentale': 'stagioniFictionSentimentale',
            'stagioniFictionSerieTvHomepage': 'stagioniFictionSerieTvHomepage',
            'stagioniFictionSerieTvSezione': 'stagioniFictionSerieTvSezione',
            'stagioniFictionSitCom': 'stagioniFictionSitCom',
            'stagioniKids': 'stagioniKids',
            'stagioniPrimaSerata': 'stagioniPrimaSerata',
            'stagioniProgrammiTv': 'stagioniProgrammiTv',
            'stagioniReality': 'stagioniReality',
            'stagioniTalk': 'stagioniTalk',
            'stagioniVarieta': 'stagioniVarieta'
        }
        rutils.RUtils.__init__(self, enable_cache=kodiutils.getSettingAsBool('cache'), enable_mem_cache=kodiutils.getSettingAsBool('cachememory'))
        self.anonymousLogin()
        # user = kodiutils.getSetting('email')
        # password = kodiutils.getSetting('password')
        # if user and password:
        #     self.login(user, password)
        # else:
        #     self.anonymousLogin()
        # self.log = kodiutils.log

    @kodiutils.cacheable(hours=4)
    def getSessionKey(self):
        res = self.SESSION.get(
            "https://api.one.accedo.tv/session?appKey=59ad346f1de1c4000dfd09c5&uuid=sdd",
            verify=True)
        return res.json()['sessionKey']
    
    def __getAPISession(self):
        self.setHeader('x-session', self.getSessionKey())

    def isSessionValid(self, now=time.time()):
        return self.expires_at>=0.0 and now > self.expires_at

    @kodiutils.cacheable(hours=4)
    def getLoginData(self, usr='', pwd=''):
        data = {
            "loginID": usr,
            "password": pwd,
            "sessionExpiration": "31536000",
            "targetEnv": "jssdk",
            "include": "profile,data,emails,subscriptions,preferences,",
            "includeUserInfo": "true",
            "loginMode": "standard",
            "lang": "it",
            "APIKey": "3_NhZq9YZgkgeKfN08uFjs3NYGo2Txv4QQTULh0he2w337E-o0DPXzEp4aVnWIR4jg",
            "cid": "mediaset-web-mediaset.it programmi-mediaset Default",
            "source": "showScreenSet",
            "sdk": "js_latest",
            "authMode": "cookie",
            "pageURL": "https://www.mediasetplay.mediaset.it",
            "format": "json",
            "utf8": "&#x2713;"}
        res = self.createRequest(
            "https://login.mediaset.it/accounts.login", post=data)
        data = res.json()
        self.log('Trying to login with user data %s' % data , 4)
        if data:
            jsn = data['userInfo'] if 'userInfo' in data else {}
            sessionInfo = data['sessionInfo'] if 'sessionInfo' in data else {}
            if 'errorCode' in jsn and jsn['errorCode'] == 0:
                return {
                    "UID": jsn['UID'],
                    "UIDSignature": jsn['UIDSignature'],
                    "signatureTimestamp": jsn['signatureTimestamp'],
                    "expires_in": sessionInfo['expires_in']
                }
        return None

    def login(self, user, password):
        self.log('Trying to login with user data', 4)
        data = self.getLoginData(usr=user, pwd=password)
        if not data:
            self.log('Login with user data failed', 4)
            return False
        self.__UID = data['UID']
        self.__UIDSignature = data['UIDSignature']
        self.__signatureTimestamp = data['signatureTimestamp']
        if data['expires_in']:
            self.expires_at = time.time() + (float(data['expires_in']) / 1000.0)
        return self.__getAPIKeys(True)

    def anonymousLogin(self):
        return self.__getAPIKeys()

    @kodiutils.cacheable(hours=1)
    def getAPIData(self, login):
        if login:
            data = {"platform": "pc",
                    "UID": self.__UID,
                    "UIDSignature": self.__UIDSignature,
                    "signatureTimestamp": self.__signatureTimestamp,
                    "appName": "web/mediasetplay-web/bd16667"}
            url = "https://api-ott-prod-fe.mediaset.net/PROD/play/idm/account/login/v1.0"
        else:
            data = {"cid": "dc4e7d82-89a5-4a96-acac-d3c7f2ca6d67",
                    "platform": "pc",
                    "appName": "web/mediasetplay-web/576ea90"}
            url = "https://api-ott-prod-fe.mediaset.net/PROD/play/idm/anonymous/login/v1.0"
        res = self.SESSION.post(url, json=data, verify=True)
        jsn = res.json()
        if 'isOk' in jsn and jsn['isOk']:
            return {
                "apigw": res.headers['t-apigw'],
                "cts": res.headers['t-cts'],
                "tracecid": jsn['response']['traceCid'],
                "cwid": jsn['response']['cwId']
            }
        return None

    def __getAPIKeys(self, login=False):
        data = self.getAPIData(login)
        if not data:
            return False
        self.apigw = data['apigw']
        self.cts = data['cts']
        self.setHeader('t-apigw', self.apigw)
        self.setHeader('t-cts', self.cts)
        self.__tracecid = data['tracecid']
        self.__cwid = data['cwid']
        self.log('Retrieved keys successfully', 4)
        return True

    def __getEntriesFromUrl(self, url, args=None):
        hasMore = False
        data = self.getJson(self.__create_url(url, args))
        if data:
            if 'itemsPerPage' in data and 'entryCount' in data:
                hasMore = data['itemsPerPage'] == data['entryCount']
            elif 'pagination' in data:
                pagination = data['pagination']
                hasMore = pagination['total'] <= (pagination['offset']+1) * pagination['size']
            if 'entries' in data:
                return data['entries'], hasMore
        return data, hasMore

    def __getElsFromUrl(self, url):
        result = None
        hasMore = False
        data = self.getJson(url)
        kodiutils.log('__getElsFromUrl: {}'.format(str(data)), 4)
        if data and 'isOk' in data and data['isOk']:
            if 'response' in data:
                response = data['response']
                metadata = response['metadata'] if 'metadata' in response else {}
                if 'error' in metadata and metadata['error']:
                    kodiutils.log('Error: {}'.format(str(metadata['error'])), 1)
                    kodiutils.notify('Timeout caricamento dati', icon=kodiutils.getMedia('notify.png'))
                    return [], None
                if 'hasMore' in response:
                    hasMore = response['hasMore']
                elif 'pagination' in metadata:
                    pagination = metadata['pagination']
                    hitsPerPage = int(pagination['hitsPerPage']) if 'hitsPerPage' in pagination else 0
                    totalHits = int(pagination['totalHits']) if 'totalHits' in pagination else 0
                    if totalHits and totalHits == hitsPerPage:
                        hasMore = totalHits
                if 'entries' in response:
                    result = response['entries']
                else:
                    result = response
            elif 'entries' in data:
                result = data['entries']
        return result, hasMore

    def __getsectionsFromEntryID(self, eid):
        self.__getAPISession()
        jsn = self.getJson(
            "https://api.one.accedo.tv/content/entry/{eid}?locale=it".format(eid=eid))
        if jsn and "components" in jsn:
            entries = []
            result = []
            components = jsn["components"]
            total = len(components)
            idx = 0
            self.log('components: ' + str(total), 4)
            for idx in range(total):
                entries.append(components[idx])
                if (idx+1) % 20 == 0 or idx+1==total:
                    eid = quote(",".join(entries))
                    self.log('eid: ' + str(eid), 4)
                    del entries[:]
                    jsn = self.getJson("https://api.one.accedo.tv/content/entries?id={eid}&locale=it".format(eid=eid))
                    if jsn and 'entries' in jsn:
                        result.extend(jsn['entries'])
            # self.log('result: ' + str(len(result)), 4)
            return result
        return False

    def __createMediasetUrl(self, base, pageels=None, page=None, args=None, passkeys=True):
        if args is None:
            args = {}
        if pageels and 'hitsPerPage' not in args:
            args['hitsPerPage'] = pageels
        if page and 'page' not in args:
            args['page'] = str(page)
        if 'page' not in args and 'hitsPerPage' in args:
            args['page'] = '1'
        if passkeys and self.__tracecid:
            args['traceCid'] = self.__tracecid
        if passkeys and self.__cwid:
            args['cwId'] = self.__cwid
        return self.__create_url(base, args)

    def __create_url(self, url, args=None):
        if args is None:
            return url
        if url.endswith('?'):
            return url + urlencode(args)
        return url + '?' + urlencode(args)

    def __createAZUrl(self, categories=None, query=None, inonda=None, pageels=100, page=None):
        args = {"query": query if query else "*:*"}

        if categories is not None:
            args["categories"] = ",".join(categories)
        if inonda is not None:
            args["inOnda"] = str(inonda).lower()
        return self.__createMediasetUrl(
            "https://api-ott-prod-fe.mediaset.net/PROD/play/rec/azlisting/v1.0?",
            pageels, page, args)

    def OttieniOnDemand(self):
        self.log('Trying to get the sections list for ondemand', 4)
        url = "https://api.one.accedo.tv/content/entries"
        args = {'locale': 'it', 'offset': '0', 'size': '50', 'typeAlias': 'page-browse'}
        self.__getAPISession()
        data, _ = self.__getEntriesFromUrl(url, args)
        if data:
            self.log('data: {}'.format(data), 4)
            page_priority = {'programmitv': '0001', 'family': '0002',  'fiction': '0003', 'film': '0004',  'kids': '0005', 'documentari': '0006'}
            filtered = []
            for el in data:
                name = str(el['name'].lower()) if 'name' in el else ''
                if 'pageUri' in el and 'page_section' in el and (name.startswith('[pro]') or name.startswith('[mpi]')):
                    key_pr = str(el['page_section'])
                    if key_pr in page_priority:
                        el['priority'] = page_priority[key_pr]
                    if not 'priority' in el:
                         el['priority'] = '9999' + '_' + el['title']
                    filtered.append(el)
            return sorted(filtered, key=lambda k: k['priority'] if 'priority' in k else k['title'])
        return None

    def OttieniOnDemandGeneri(self, id, sort=None, order='asc'):
        self.log('Trying to get the sections list for ondemand section: ' + id, 4)
        data = self.__getsectionsFromEntryID(id)
        if data and sort:
            return sorted(data, key=lambda k: k[sort] if sort in k else None, reverse=(not order == 'asc'))
        return data

    def OttieniMagazine(self, newsFeedUrl, iperpage=None):
        self.log('Trying to get the list of articles for magazine section: ' + newsFeedUrl, 4)
        if iperpage:
            if '?' in newsFeedUrl:
                newsFeedUrl = '{}&size={}'.format(newsFeedUrl,iperpage)
            else:
                newsFeedUrl = '{}?size={}'.format(newsFeedUrl,iperpage)
        jsn = self.getJson(newsFeedUrl)
        nextPage = False
        prevPage = False
        els = []
        if 'data' in jsn:
            data = jsn['data']
            if 'items' in data:
                els = data['items']
        if 'resultInfo' in jsn and 'paging' in jsn['resultInfo']:
            resultInfo = jsn['resultInfo']
            paging = resultInfo['paging'] if 'paging' in resultInfo else {}
            nextPage = paging['next'] if 'next' in paging else None
            prevPage = paging['previus'] if 'previus' in paging else None
        return els, nextPage, prevPage

    def OttieniNews(self, ddg_url):
        self.log('Trying to get info from ddg_url ' + ddg_url, 4)
        jsn = self.getJson(ddg_url)
        els = []
        if jsn and 'data' in jsn and 'paragraphs' in jsn['data']:
            for p in jsn['data']['paragraphs']:
                self.log('paragraph: ' + str(p), 4)
                if 'guid' in p:
                    el = self.OttieniInfoDaGuid(p['guid'])
                    if el:
                        els.append(el)
        return els

    def OttieniCult(self, feedurl, iperpage=None):
        if iperpage and not 'range' in feedurl:
            if '?' in feedurl:
                feedurl = '{}&range={}-{}'.format(feedurl,1,iperpage)
            else:
                feedurl = '{}?range={}-{}'.format(feedurl,1,iperpage)
        self.log('Trying to get the list of articles for cult section: ' + feedurl, 4)
        jsn = self.getJson(feedurl)
        self.log('Trying to get the list of articles for cult section: %s' % jsn, 4)
        nextPage = False
        prevPage = False
        els = []
        if 'entries' in jsn:
            els = jsn['entries']
            if els and 'itemsPerPage' in jsn and 'entryCount' in jsn and jsn['itemsPerPage'] == jsn['entryCount']:
                url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs'
                brandId = els[0]['mediasetprogram$brandId'] if 'mediasetprogram$brandId' in els[0] else ''
                subBrandId = els[0]['mediasetprogram$subBrandId'] if 'mediasetprogram$subBrandId' in els[0] else ''
                if brandId and subBrandId:
                    byCustomValue = '{{brandId}}{{{brandId}}},{{subBrandId}}{{{subBrandId}}}'.format(brandId=brandId,subBrandId=subBrandId)
                    itemsPerPage = int(jsn['itemsPerPage'])
                    startIndex = int(jsn['startIndex'])
                    nextStartIndex = startIndex + itemsPerPage
                    nextEndIndex = nextStartIndex + itemsPerPage - 1
                    nextPage = self.__create_url(url, {'byCustomValue': byCustomValue, 'range': '{}-{}'.format(nextStartIndex, nextEndIndex)})
                    if startIndex>itemsPerPage:
                        prevStartIndex = startIndex - itemsPerPage
                        prevEndIndex = startIndex - 1
                        prevPage = self.__create_url(url, {'byCustomValue': byCustomValue, 'range': '{}-{}'.format(prevStartIndex, prevEndIndex)})
        return els, nextPage, prevPage

    def OttieniContinuaGardare(self):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/continuewatch/v1.0")
        return self.__getElsFromUrl(url)

    def OttieniFavoriti(self):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/favorites/v1.0")
        return self.__getElsFromUrl(url)

    def OttieniWatchlist(self):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/watchlist/v1.0")
        return self.__getElsFromUrl(url)

    def getProgress(self, guid=''):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/continuewatch/progress/v1.0", args={"contentId": guid})
        res = self.getJson(url)
        if res and 'response' in res:
            response = res['response']
            if 'position' in response and response['position']:
                return int(response['position'])
        return 0

    def setProgress(self, guid=None, position=0, duration=0):
        self.log('setProgress: guid={}, position={}, duration={}'.format(str(guid),str(position),str(duration)))
        if guid and position and duration:
            url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/continuewatch/progress/v1.0")
            data = {
                "contentId": str(guid),
                "position": int(position),
                "streamDuration": int(duration)
            }
            self.log('setProgress: url={}, data={}'.format(str(url),str(data)))
            result = self.SESSION.post(url, json=data, headers={'Content-Type': 'application/json', 'Cache-Control': 'no-cache'})
            # self.log('setProgress result: %s' % result.json(), 4)
            return 'response' in result and 'isOk' in result['response'] and result['response']['isOk']
        return False

    def AggiungiLista(self, lista='', item_id=''):
        if lista and item_id:
            url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/{}/v1.0".format(lista))
            data = {
                "contentId": str(item_id)
            }
            response = self.SESSION.post(url, json=data, headers={'Content-Type': 'application/json', 'Cache-Control': 'no-cache'})
            result = response.json()
            self.log('AggiungiLista result: %s' % result, 4)
            return 'isOk' in result and result['isOk']

    def EliminaLista(self, delete_list='', delete_id=''):
        if delete_list and delete_id:
            url = self.__createMediasetUrl("https://api.cloud.mediaset.net/api/ssr/userlist/{}/59ad346f1de1c4000dfd09c5".format(str(delete_list)))
            data = {
                "id": [str(delete_id)]
            }
            res = self.SESSION.delete(url, json=data, headers={'Content-Type': 'application/json', 'Cache-Control': 'no-cache'})
            jsn = res.json()
            self.log('EliminaLista result: %s' % jsn, 4)
            result = jsn[0] if jsn and len(jsn)>0 else {}
            return 'response' in result and 'isOk' in result['response'] and result['response']['isOk']
        return False

    @kodiutils.cacheable(hours=24)
    def OttieniProgrammiGenere(self, gid, pageels=20, page=None, sort=None, order='asc'):
        self.log('Trying to get the programs from section id ' + gid, 4)
        url = self.__createMediasetUrl(
            "https://api-ott-prod-fe.mediaset.net/PROD/play/rec2/cataloguelisting/v1.0",
            pageels, page=page, args={'platform': 'pc', 'uxReference': self.uxReferenceMapping[gid], 'deviceId': self.__deviceid})
        data, hasMore = self.__getElsFromUrl(url)
        self.log('OttieniProgrammiGenere: %s' % data, 4)
        if sort and data and not hasMore:
            return sorted(data, key=lambda k: k[sort] if sort in k else None, reverse=(not order == 'asc')), hasMore
        return data, hasMore

    def OttieniStagioni(self, seriesId, sort=None, order='asc'):
        self.log('Trying to get the seasons from series id {}'.format(seriesId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-tv-seasons/feed'
        args = {'bySeriesId': seriesId}
        if sort:
            args['sort'] = sort + '|' + order
        return self.__getEntriesFromUrl(url, args)

    def OttieniSezioniProgramma(self, brandId, sort=None):
        self.log('Trying to get the sections from brand id {}'.format(brandId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-brands?'
        args = {'byCustomValue': '{{brandId}}{{{brandId}}}'.format(brandId=brandId)}
        if sort:
            args['sort'] = sort
        return self.__getEntriesFromUrl(url, args)

    def OttieniVideoSezione(self, subBrandId, sort=None, page=1, size=50):
        self.log('Trying to get the videos from section {}'.format(subBrandId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs'
        startIndex = (page-1) * size + 1
        endIndex = page * size
        args = {'byCustomValue': '{{subBrandId}}{{{subBrandId}}}'.format(subBrandId=subBrandId), 'range': '{}-{}'.format(startIndex, endIndex)}
        if sort:
            args['sort'] = sort
        return self.__getEntriesFromUrl(url, args)

    def OttieniCanaliLive(self, sort=None):
        self.log('Trying to get the live channels list', 4)
        url = ('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-stations-v2?')
        if sort:
            return self.__getEntriesFromUrl(url, {'sort': sort})
        return self.__getEntriesFromUrl(url)

    def Cerca(self, query, section=None, pageels=100, page=None):
        args = {'query': query, 'platform': 'pc'}
        if section:
            args['uxReference'] = self.uxReferenceMapping[section]
        url = self.__createMediasetUrl('https://api-ott-prod-fe.mediaset.net/PROD/play/rec2/search/v1.0', pageels=pageels, page=page, args=args)
        return self.__getElsFromUrl(url)

    def OttieniGuidaTV(self, chid, start, finish):
        self.log(('Trying to get the tv guide from {} channel '
                  'starting {} finishing {}').format(chid, str(start), str(finish)), 4)
        args = {'byCallSign': chid, 'byListingTime': '{s}~{f}'.format(s=str(start), f=str(finish))}
        url = self.__createMediasetUrl(
            "https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-listings?",
            pageels=None, page=None, args=args, passkeys=False)
        res = self.__getEntriesFromUrl(url)
        if res is not None:
            if res and res[0]:
                return res[0][0]
            return {}
        return res

    def OttieniProgrammiLive(self, sort=None):
        self.log('Trying to get the live programs', 4)
        now = staticutils.get_timestamp()
        args = {'byListingTime': '{s}~{f}'.format(s=str(now - 1001), f=str(now))}
        if sort:
            args['sort'] = sort
        url = self.__createMediasetUrl(
            "https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-listings?",
            pageels=None, page=None, args=args, passkeys=False)
        return self.__getEntriesFromUrl(url)

    def OttieniLiveStream(self, guid):
        self.log('Trying to get live and rewind channel program of id {}'.format(guid), 4)
        url = 'https://static3.mediasetplay.mediaset.it/apigw/nownext/{}.json'.format(guid)
        return self.__getElsFromUrl(url)

    def OttieniInfoDaGuid(self, guid):
        self.log('Trying to get info from guid ' + guid, 4)
        url = ('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs/'
               'guid/-/{guid}').format(guid=guid)
        data = self.getJson(url)
        if data and 'isException' not in data:
            return data
        return False

    def OttieniDatiVideo(self, pid, live=False, properties=None):
        self.log('Trying to get video data from pid ' + pid, 4)
        u = 'https://link.theplatform.eu/s/PR1GhC/'
        if not live:
            u += 'media/'
        u += pid + ('?auto=true&balance=true&format=smil&formats=MPEG-DASH,MPEG4,M3U&tracking=true'
                    '&assetTypes=HD,browser,widevine,geoIT|geoNo:HD,browser,geoIT|geoNo:HD,geoIT|geoNo:SD,browser,widevine,geoIT|geoNo:SD,browser,geoIT|geoNo:SD,geoIT|geoNo')
        text = self.getText(u)
        res = {'url': '', 'pid': '', 'type': '', 'security': False}
        root = ET.fromstring(text)
        for vid in root.findall('.//{http://www.w3.org/2005/SMIL21/Language}switch'):
            ref = vid.find('./{http://www.w3.org/2005/SMIL21/Language}ref')
            res['url'] = ref.attrib['src']
            res['type'] = ref.attrib['type']
            if 'security' in ref.attrib and ref.attrib['security'] == 'commonEncryption':
                res['security'] = True
            par = ref.find(
                './{http://www.w3.org/2005/SMIL21/Language}param[@name="trackingData"]')
            if par is not None:
                for item in par.attrib['value'].split('|'):
                    [attr, value] = item.split('=', 1)
                    if attr == 'pid':
                        res['pid'] = value
                        break
            break
        if properties and 'url' in res:
             res['url'] = self.__create_url(res['url'],properties)
        return res

    def OttieniWidevineAuthUrl(self, uid):
        return (
            'https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense?'
            'releasePid={pid}&account=http://access.auth.theplatform.com/data/Account/'
            '2702976343&schema=1.0&token={cts}').format(pid=uid, cts=self.cts)
