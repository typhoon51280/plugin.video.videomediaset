import time
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
        self.expires_at = 0.0
        self.anonymousLogin()
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
        rutils.RUtils.__init__(self)
        # user = kodiutils.getSetting('email')
        # password = kodiutils.getSetting('password')
        # if user and password:
        #     self.login(user, password)
        # else:
        #     self.anonymousLogin()
        # self.log = kodiutils.log

    def __getAPISession(self):
        res = self.SESSION.get(
            "https://api.one.accedo.tv/session?appKey=59ad346f1de1c4000dfd09c5&uuid=sdd",
            verify=True)
        self.setHeader('x-session', res.json()['sessionKey'])

    def isSessionValid(self, now=time.time()):
        return self.expires_at>=0.0 and now > self.expires_at

    def login(self, user, password):
        self.log('Trying to login with user data', 4)
        data = {
            "loginID": user,
            "password": password,
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
        # s = res.text.strip().replace('gigya.callback(', '', 1)
        # if s[-1:] == ';':
        #     s = s[:-1]
        # if s[-1:] == ')':
        #     s = s[:-1]
        # jsn = json.loads(s)
        data = res.json()
        self.log('Trying to login with user data %s' % data , 4)
        jsn = data['userInfo'] if 'userInfo' in data else {}
        if jsn['errorCode'] != 0:
            self.log('Login with user data failed', 4)
            return False
        self.__UID = jsn['UID']
        self.__UIDSignature = jsn['UIDSignature']
        self.__signatureTimestamp = jsn['signatureTimestamp']
        if 'sessionInfo' in data and 'expires_in' in data['sessionInfo']:
            self.expires_at = time.time() + (float(data['sessionInfo']['expires_in']) / 1000.0)
        return self.__getAPIKeys(True)

    def anonymousLogin(self):
        return self.__getAPIKeys()

    def __getAPIKeys(self, login=False):
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
        if not jsn['isOk']:
            return False

        self.apigw = res.headers['t-apigw']
        self.cts = res.headers['t-cts']
        self.setHeader('t-apigw', self.apigw)
        self.setHeader('t-cts', self.cts)
        self.__tracecid = jsn['response']['traceCid']
        self.__cwid = jsn['response']['cwId']
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
        if data and 'isOk' in data and data['isOk']:
            if 'response' in data:
                response = data['response']
                if 'hasMore' in response:
                    hasMore = response['hasMore']
                elif 'metadata' in response and 'pagination' in response['metadata']:
                    pagination = response['metadata']['pagination']
                    hasMore = pagination['totalHits'] == pagination['hitsPerPage'] if 'hitsPerPage' in pagination else False
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

    # def OttieniTutto(self, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the full program list', 4)
    #     url = self.__createAZUrl(inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

    # def OttieniTuttoLettera(self, lettera, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the full program list with letter {}'.format(lettera), 4)
    #     if lettera == '#':
    #         query = '-(TitleFullSearch:{A TO *})'
    #     else:
    #         query = 'TitleFullSearch:' + lettera + '*'
    #     url = self.__createAZUrl(query=query, inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

    # def OttieniTuttiProgrammi(self, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the tv program list', 4)
    #     url = self.__createAZUrl(["Programmi Tv"], inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

    # def OttieniTutteFiction(self, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the fiction list', 4)
    #     url = self.__createAZUrl(["Fiction"], inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

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
                if 'page_section' in el and str(el['name'].lower()).startswith('[pro]'):
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

    def OttieniMagazine(self, newsFeedUrl):
        self.log('Trying to get the list of articles for magazine section: ' + newsFeedUrl, 4)
        jsn = self.getJson(newsFeedUrl)
        nextPage = False
        els = []
        if 'data' in jsn:
            data = jsn['data']
            if 'items' in data:
                els = data['items']
        if 'resultInfo' in jsn and 'paging' in jsn['resultInfo'] and 'next' in jsn['resultInfo']['paging']:
            nextPage = jsn['resultInfo']['paging']['next']
        return els, nextPage

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

    def OttieniCult(self, feedurl):
        self.log('Trying to get the list of articles for cult section: ' + feedurl, 4)
        jsn = self.getJson(feedurl)
        nextPage = False
        els = []
        if 'entries' in jsn:
            els = jsn['entries']
            if els and 'itemsPerPage' in jsn and 'entryCount' in jsn and jsn['itemsPerPage'] == jsn['entryCount']:
                url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs'
                startIndex = int(jsn['startIndex']) + int(jsn['itemsPerPage'])
                endIndex = int(jsn['startIndex']) + int(jsn['itemsPerPage']) + int(jsn['itemsPerPage']) - 1
                brandId = els[0]['mediasetprogram$brandId']
                subBrandId = els[0]['mediasetprogram$subBrandId']
                args = {'byCustomValue': '{{brandId}}{{{brandId}}},{{subBrandId}}{{{subBrandId}}}'.format(brandId=brandId,subBrandId=subBrandId), 'range': '{}-{}'.format(startIndex, endIndex)}
                nextPage = self.__create_url(url, args)
        return els, nextPage

    # def OttieniGeneri(self, section):
    #     self.log('Trying to get the sections list for ' + section, 4)
    #     url = "https://api.one.accedo.tv/content/entries"
    #     args = {'locale': 'it', 'offset': '0', 'size': '50', 'typeAlias': 'page-browse'}
    #     self.__getAPISession()
    #     data, _ = self.__getEntriesFromUrl(url, args)
    #     if data:
    #         self.log('data: {}'.format(data), 4)
    #         entries = list(filter(lambda el: 'page_section' in el and str(el['page_section'].lower()) == section.lower() and str(el['name'].lower()).startswith('[pro]'), data))
    #         if entries:
    #             entry = entries[0]
    #             return self.__getsectionsFromEntryID(entry['_meta']['id'])
    #     return None

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
                return response['position']
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
            # self.setHeader('Content-Type', 'application/json')
            # self.setHeader('Cache-Control', 'no-cache')
            result = self.SESSION.post(url, json=data, headers={'Content-Type': 'application/json', 'Cache-Control': 'no-cache'})
            self.log('setProgress result FULL: %s' % result, 4)
            self.log('setProgress result TEXT: %s' % result.text, 4)

    # def OttieniGeneriFiction(self):
    #     self.log('Trying to get the fiction sections list', 4)
    #     return self.__getsectionsFromEntryID("5acfcb3c23eec6000d64a6a4")

    # def OttieniFilm(self, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the movie list', 4)
    #     url = self.__createAZUrl(["Cinema"], inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

    # def OttieniGeneriFilm(self):
    #     self.log('Trying to get the movie sections list', 4)
    #     return self.__getsectionsFromEntryID("5acfcbc423eec6000d64a6bb")

    # def OttieniKids(self, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the kids list', 4)
    #     url = self.__createAZUrl(["Kids"], inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

    # def OttieniGeneriKids(self):
    #     self.log('Trying to get the kids sections list', 4)
    #     return self.__getsectionsFromEntryID("5acfcb8323eec6000d64a6b3")

    # def OttieniDocumentari(self, inonda=None, pageels=100, page=None):
    #     self.log('Trying to get the movie list', 4)
    #     url = self.__createAZUrl(["Documentari"], inonda=inonda, pageels=pageels, page=page)
    #     return self.__getElsFromUrl(url)

    # def OttieniGeneriDocumentari(self):
    #     self.log('Trying to get the movie sections list', 4)
    #     return self.__getsectionsFromEntryID("5bfd17c423eec6001aec49f9")

    def OttieniProgrammiGenere(self, gid, pageels=100, page=None, sort=None, order='asc'):
        self.log('Trying to get the programs from section id ' + gid, 4)
        url = self.__createMediasetUrl(
            "https://api-ott-prod-fe.mediaset.net/PROD/play/rec2/cataloguelisting/v1.0",
            pageels=pageels, page=page, args={'platform': 'pc', 'uxReference': self.uxReferenceMapping[gid]})
        data, hasMore = self.__getElsFromUrl(url)
        if sort and not hasMore:
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

    def OttieniVideoSezione(self, subBrandId, sort=None, page=0, size=50):
        self.log('Trying to get the videos from section {}'.format(subBrandId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs'
        offset = int(page) * int(size)
        startIndex = offset + 1
        endIndex = offset + int(size)
        args = {'byCustomValue': '{{subBrandId}}{{{subBrandId}}}'.format(subBrandId=subBrandId), 'range': '{}-{}'.format(startIndex, endIndex)}
        if sort:
            args['sort'] = sort
        return self.__getEntriesFromUrl(url, args)

    def OttieniCanaliLive(self, sort=None):
        self.log('Trying to get the live channels list', 4)
        url = ('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-stations?')
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
            "https://api-ott-prod-fe.mediaset.net/PROD/play/alive/allListingFeedEpg/v1.0?",
            pageels=None, page=None, args=args)
        res = self.__getElsFromUrl(url)
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
                    '&assetTypes=HD,browser,widevine:HD,browser:SD,browser,widevine:SD,browser:SD')
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
