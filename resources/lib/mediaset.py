import time
import uuid
import xml.etree.ElementTree as ET
from phate89lib import kodiutils, rutils, staticutils  # pyright: reportMissingImports=false
try:
    from urllib.parse import urlencode, quote
except ImportError:
    from urllib import urlencode, quote


class Mediaset(rutils.RUtils):

    USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    ACCEDO_ONE_KEY = "6023de431de1c4001877be3b"
    APP_NAME = "generic-androidtv/12/mediasetplay-ctv"

    def __init__(self, account={}):
        self.log = kodiutils.log
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
        if not self.isAuthenticated():
            if not(self.isAnonymous() and self.isValidBeToken()):
                self.anonymousLogin()

    @kodiutils.store('account', inject=False)
    def setAccount(self, key=None, value=None):
        if key:
            return {
                key: value
            }
        return {}

    @kodiutils.store('account', merge=False, write=False)
    def getAccount(self, attr=None, account={}):
        if attr:
            if attr in account:
                return account[attr]
            return None
        return account

    def getPersonas(self, idPersona=None, excludeCurrent=False):
        personas = self.getAccount('personas')
        if personas:
            if idPersona:
                personas = list(filter(lambda x: ('type' in x and x['id'] == idPersona), personas))
            elif excludeCurrent:
                currentPersona = self.getCurrentPersona()
                if currentPersona and 'id' in currentPersona:
                    personas = list(filter(lambda x: ('type' in x and x['id'] != currentPersona['id']), personas))
        return personas

    def getCurrentPersona(self):
        currentPersona = self.getAccount('currentPersona')
        if currentPersona:
            personas = self.getPersonas(currentPersona)
            if len(personas)==1:
                return personas[0]
        return None

    def getAuthHeaders(self, headers={}):
        token = self.getAccount('beToken')
        if token:
            headers['Authorization'] = 'Bearer {}'.format(token)
        return headers

    def isValidPin(self):
        account = self.getAccount()
        return account and 'action_pin' in account and account['action_pin'] and 'action_ttl' in account and staticutils.is_after_now(account['action_ttl'])

    def isValidCaToken(self):
        account = self.getAccount()
        return account and 'caToken' in account and account['caToken'] and 'caToken_ttl' in account and staticutils.is_after_now(account['caToken_ttl'])

    def isValidBeToken(self):
        account = self.getAccount()
        return account and 'beToken' in account and account['beToken'] and 'beToken_ttl' in account and staticutils.is_after_now(account['beToken_ttl'])

    def isSessionValid(self):
        account = self.getAccount()
        return 'sessionKey' in account and 'sessionKey_ttl' in account and staticutils.is_after_now(account['sessionKey_ttl'])

    def isAnonymous(self):
        accountType = self.getAccount('accountType')
        return accountType and accountType == 'anonymous'

    def isRegistered(self):
        accountType = self.getAccount('accountType')
        return accountType and accountType == 'account'

    def isAuthenticated(self):
        if self.isRegistered():
            if self.isValidBeToken():
                return True
            elif self.accountRefresh() and self.accountLogin():
                return self.isValidBeToken()
        return False

    def isPaired(self):
        if self.isValidCaToken():
            personas = self.getPersonas()
            return len(personas) > 0
        return False

    def registerDevice(self):
        if not self.isValidPin():
            self.accountSetup()
        return self.isValidPin()

    def pair(self):
        if not self.isPaired():
            if self.accountPair():
                personas = self.getPersonas()
                if personas and len(personas)==1:
                    self.personaLogin(personas[0]['id'])
        return self.isPaired()

    def unauthorized(self):
        self.setAccount('beToken_ttl', 0)
        kodiutils.notify('Timeout Sessione', icon=kodiutils.getMedia('notify.png'))

    @kodiutils.store(merge=False)
    def logout(self):
        return {}

    @kodiutils.store('account')
    def getSessionKey(self, account={}):
        res = self.getJson(self.__create_url("https://api.one.accedo.tv/session", args={"appKey": self.ACCEDO_ONE_KEY, "uuid": str(uuid.uuid4())}))
        if res and 'sessionKey' in res and 'expiration' in res:
            return {
                "sessionKey": res['sessionKey'],
                "sessionKey_ttl": staticutils.get_timestamp(staticutils.get_datetime_from_string(res['expiration'][0:17] + "Z", "%Y%m%dT%H:%M:%S%z"))
            }
        return None
    
    def getSessionHeaders(self, headers={}):
        if not self.isSessionValid():
            self.getSessionKey()
        if self.isSessionValid():
            headers['x-session'] = self.getAccount('sessionKey')
        return headers

    @kodiutils.store('account', inject=False)
    def anonymousLogin(self):
        clientId = str(uuid.uuid4())
        data = {
            "client_id": clientId,
            "appName": self.APP_NAME
        }
        url = "https://api-ott-prod-fe.mediaset.net/PROD/play/idm/anonymous/login/v2.0"
        jsn = self.getJson(url, json=data)
        if jsn and 'isOk' in jsn and jsn['isOk']:
            return {
                "beToken": jsn['response']['beToken'],
                "beToken_ttl": staticutils.get_timestamp(staticutils.get_datetime_from_string(jsn['time'], '%Y-%m-%dT%H:%M:%S.%f') + staticutils.get_duration(milliseconds=43420000)),
                "accountType": 'anonymous',
                "sid": jsn['response']['sid'],
                "clientId": clientId,
                "appName": self.APP_NAME
            }
        return None

    @kodiutils.store('account')
    def accountSetup(self, account={}):
        self.log('accountSetup: {}'.format(account))
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/action/create/v2.0'
        clientId = str(uuid.uuid4())
        action_url = "https://mediasetinfinity.mediaset.it/tv"
        action_url_full = action_url + "?pin={action_pin}"
        data = {
            "action_name": "LOGIN",
            "action_url": action_url_full,
            "action_data": {
                "appName": self.APP_NAME,
                "client_id": clientId,
                "include": "personas,accountInfo,adminBeToken"
            },
            "action_info": {
                "appName": self.APP_NAME
            }
        }
        jsn = self.getJson(url, json=data)
        if jsn and 'isOk' in jsn and jsn['isOk'] and 'response' in jsn:
            response = jsn['response']
            response['action_url'] = action_url
            response['action_url_full'] = action_url_full.format(action_pin=response['action_pin'])
            return {**self.mapDevice(response), **{"appName": self.APP_NAME, "clientId": clientId}}
        return False

    @kodiutils.store('account')
    def accountPair(self, account={}):
        self.log('accountPair: {}'.format(account))
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/action/pair/v2.0'
        data = {
            "action_id": account['action_id']
        }
        jsn = self.getJson(url, json=data)
        self.log('accountPair response: {}'.format(jsn))
        if jsn and 'isOk' in jsn and jsn['isOk'] and 'response' in jsn and 'action_complete' in jsn['response']:
            response = jsn['response']
            if response['action_complete'] and 'action_result' in response and 'login' in response['action_result']:
                login_data = response['action_result']['login']
                if 'account' in login_data:
                    login_data['caToken_ttl'] = staticutils.get_timestamp(staticutils.get_datetime_from_string(jsn['time'], '%Y-%m-%dT%H:%M:%S.%f') + staticutils.get_duration(milliseconds=login_data['duration']))
                    return {**self.mapDevice(), **self.mapLogin(login_data), **self.mapPersonas(login_data['account'])}
        return False
    
    @kodiutils.store('account')
    def accountRefresh(self, account={}):
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/gigya/renew/v2.0'
        data = {
            "client_id": account['clientId']
        }
        jsn = self.getJson(url, json=data, headers=self.getAuthHeaders())
        if jsn and 'isOk' in jsn and jsn['isOk'] and 'response' in jsn:
            response = jsn['response']
            return {
                "id_token": response['gt']
            }
        return False

    @kodiutils.store('account')
    def accountLogin(self, account={}):
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/account/login/v2.0'
        data = {
            "id": account['currentPersona'],
            "gt": account['id_token'],
            "appName": account['appName'],
            "client_id": account['clientId'],
            "include": "personas,accountInfo,adminBeToken"
        }
        jsn = self.getJson(url, json=data)
        if jsn and 'isOk' in jsn and jsn['isOk'] and 'response' in jsn:
            response = jsn['response']
            if 'account' in response:
                response['caToken_ttl'] = staticutils.get_timestamp(staticutils.get_datetime_from_string(jsn['time'], '%Y-%m-%dT%H:%M:%S.%f') + staticutils.get_duration(milliseconds=response['duration']))
                response['beToken_ttl'] = response['caToken_ttl']
                return {**self.mapLogin(response), **self.mapPersonas(response['account'])}
        return False

    def personaList(self):
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/persona/list/v2.0'
        jsn = self.getJson(url, headers=self.getAuthHeaders())
        if jsn and 'isOk' in jsn and jsn['isOk'] and 'response' in jsn:
            response = jsn['response']
            if 'account' in response:
                return self.mapPersonas(response['account'])
        return False

    @kodiutils.store('account')
    def personaLogin(self, idPersona=None, account={}):
        self.log('personaLogin: {}'.format(account))
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/idm/persona/login/v2.0'
        data = {
            "caToken": account['caToken'],
            "id": idPersona 
        }
        jsn = self.getJson(url, json=data)
        if 'isOk' in jsn and jsn['isOk'] and 'response' in jsn:
            response = jsn['response']
            return {
                'beToken': response['beToken'],
                'beToken_ttl': staticutils.get_timestamp(staticutils.get_datetime_from_string(jsn['time'], '%Y-%m-%dT%H:%M:%S.%f') + staticutils.get_duration(milliseconds=response['duration'])),
                'currentPersona': idPersona,
                'accountType': 'account',
            }
        return False

    def userInfo(self, caToken, idPersona):
        url = 'https://api-ott-prod-fe.mediaset.net/PROD/play/comm/syntheticuserinfo/v2.0'
        jsn = self.getJson(url, headers=self.getAuthHeaders())
        if jsn and 'isOk' in jsn and jsn['isOk'] and 'response' in jsn:
            return jsn['response']
        return False

    def mapDevice(self, action={}):
        return {
            "action_url": action['action_url'] if 'action_url' in action else None,
            "action_url_full": action['action_url_full'] if 'action_url_full' in action else None,
            "action_id": action['action_id'] if 'action_id' in action else None,
            "action_pin": action['action_pin'] if 'action_pin' in action else None,
            "action_ttl": action['action_ttl'] * 1000 if 'action_ttl' in action else None,
            "action_qrcode": action['action_qrcode'] if 'action_qrcode' in action else None
        }


    def mapLogin(self, login={}):
        return {
            "accountType": 'account' if 'beToken' in login else None,
            "sid": login['sid'] if 'sid' in login else None,
            "beToken": login['beToken'] if 'beToken' in login else None,
            "beToken_ttl": login['beToken_ttl'] if 'beToken_ttl' in login else None,
            "caToken": login['caToken'] if 'caToken' in login else None,
            "caToken_ttl": login['caToken_ttl'] if 'caToken_ttl' in login else None,

        }

    def mapPersonas(self, account={}):
        if 'id' in account:
            accountId = account['id']
        if 'accountSettings' in account and 'default' in account['accountSettings']:
            default_persona = account['accountSettings']['default']
        if 'personas' in account:
            personas = list(filter(lambda x: ('type' in x and x['type'] != "Family"), account['personas']))
        return {
            "accountId": accountId,
            "defaultPersona": default_persona,
            "personas": personas
        }

    def __getEntriesFromUrl(self, url, args=None, headers={}):
        hasMore = False
        data = self.getJson(self.__create_url(url, args), headers=headers)
        if data:
            if 'itemsPerPage' in data and 'entryCount' in data:
                hasMore = data['itemsPerPage'] == data['entryCount']
            elif 'pagination' in data:
                pagination = data['pagination']
                hasMore = pagination['total'] <= (pagination['offset']+1) * pagination['size']
            if 'entries' in data:
                return data['entries'], hasMore
        return data, hasMore

    def __getElsFromUrl(self, url, headers={}):
        result = None
        hasMore = False
        data = self.getJson(url, headers=headers)
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
                elif 'pagination' in response and 'hasNextPage' in response['pagination']:
                    hasMore = response['pagination']['hasNextPage']
                elif 'pagination' in metadata:
                    pagination = metadata['pagination']
                    hitsPerPage = int(pagination['hitsPerPage']) if 'hitsPerPage' in pagination else 0
                    totalHits = int(pagination['totalHits']) if 'totalHits' in pagination else 0
                    if totalHits and totalHits == hitsPerPage:
                        hasMore = totalHits
                if 'entries' in response:
                    result = response['entries']
                elif 'blocks' in response:
                    result = response['blocks'][0]['items']
                else:
                    result = response
            elif 'entries' in data:
                result = data['entries']
        return result, hasMore

    def __getsectionsFromEntryID(self, eid):
        jsn = self.getJson(self.__create_url("https://api.one.accedo.tv/content/entry/{eid}", args={"locale": "it"}, path={"eid": eid}), headers=self.getSessionHeaders())
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
                    eid = ",".join(entries)
                    self.log('eid: ' + str(eid), 4)
                    del entries[:]
                    jsn = self.getJson(self.__create_url("https://api.one.accedo.tv/content/entries", args={"id": eid, "locale": "it"}), headers=self.getSessionHeaders())
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

    def __create_url(self, url, args=None, path=None):
        self.log('args {}'.format(args), 4)
        if path:
            url = url.format(**path)
        if args is None:
            return url
        if url.endswith('?'):
            return url + urlencode(args,safe=",")
        return url + '?' + urlencode(args,safe=",")

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
        data, _ = self.__getEntriesFromUrl(url, args, headers=self.getSessionHeaders())
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
        if jsn and 'data' in jsn:
            data = jsn['data']
            if 'items' in data:
                els = data['items']
        if jsn and 'resultInfo' in jsn and 'paging' in jsn['resultInfo']:
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
        if jsn and 'entries' in jsn:
            els = jsn['entries']
            if els and 'itemsPerPage' in jsn and 'entryCount' in jsn and jsn['itemsPerPage'] == jsn['entryCount']:
                url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs-v2'
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
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/bookmarks/v2.0")
        return self.__getElsFromUrl(url, headers=self.getAuthHeaders())

    def OttieniFavoriti(self):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/favouritesSeries/v2.0")
        return self.__getElsFromUrl(url, headers=self.getAuthHeaders())

    def OttieniWatchlist(self):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/watchlist/v2.0")
        return self.__getElsFromUrl(url, headers=self.getAuthHeaders())

    def getProgress(self, guid=''):
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/userlist/continuewatch/progress/v2.0", args={"contentId": guid})
        res = self.getJson(url, headers=self.getAuthHeaders())
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
            return result and 'response' in result and 'isOk' in result['response'] and result['response']['isOk']
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
            return result and 'isOk' in result and result['isOk']

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
            return result and 'response' in result and 'isOk' in result['response'] and result['response']['isOk']
        return False

    def uxMapping(self, id):
        if id and id in self.uxReferenceMapping:
            return self.uxReferenceMapping[id]
        return id

    # @kodiutils.cacheable(hours=24)
    def OttieniProgrammiGenere(self, gid, pageels=20, page=None, params=None, sort=None, order='asc'):
        self.log('Trying to get the programs from section id ' + gid, 4)
        account = self.getAccount()
        args = {
            'uxReference': self.uxMapping(gid),
            'property': 'play',
            'tenant': 'play-prod-v2',
            'sessionId': account['sid']
        }
        if params:
            args['params'] = params
        url = self.__createMediasetUrl("https://api-ott-prod-fe.mediaset.net/PROD/play/reco/{}/v2.0".format(self.getAccount('accountType')), pageels, page = page, args=args)
        data, hasMore = self.__getElsFromUrl(url, headers=self.getAuthHeaders())
        if sort and data and not hasMore:
            return sorted(data, key=lambda k: k[sort] if sort in k else '', reverse=(not order == 'asc')), hasMore
        return data, hasMore

    def OttieniStagioni(self, seriesId, sort=None, order='asc'):
        self.log('Trying to get the seasons from series id {}'.format(seriesId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-tv-seasons-v2'
        args = {'bySeriesId': seriesId}
        if sort:
            args['sort'] = sort + '|' + order
        return self.__getEntriesFromUrl(url, args)

    def OttieniSezioniProgramma(self, brandId, sort=None):
        self.log('Trying to get the sections from brand id {}'.format(brandId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-brands'
        args = {'byCustomValue': '{{brandId}}{{{brandId}}}'.format(brandId=brandId)}
        if sort:
            args['sort'] = sort
        return self.__getEntriesFromUrl(url, args)

    def OttieniVideoSezione(self, subBrandId, sort=None, page=1, size=50):
        self.log('Trying to get the videos from section {}'.format(subBrandId), 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs-v2'
        startIndex = (page-1) * size + 1
        endIndex = page * size
        args = {'byCustomValue': '{{subBrandId}}{{{subBrandId}}}'.format(subBrandId=subBrandId), 'range': '{}-{}'.format(startIndex, endIndex)}
        if sort:
            args['sort'] = sort
        return self.__getEntriesFromUrl(url, args)

    def OttieniCanaliLive(self, sort=None):
        self.log('Trying to get the live channels list', 4)
        url = 'https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-stations-v2'
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
            "https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-listings",
            pageels=None, page=None, args=args, passkeys=False)
        return self.__getEntriesFromUrl(url)

    def OttieniLiveStream(self, guid):
        self.log('Trying to get live and rewind channel program of id {}'.format(guid), 4)
        url = 'https://static3.mediasetplay.mediaset.it/apigw/nownext/{}.json'.format(guid)
        return self.__getElsFromUrl(url)

    def OttieniInfoDaGuid(self, guid):
        self.log('Trying to get info from guid ' + guid, 4)
        url = ('https://feed.entertainment.tv.theplatform.eu/f/PR1GhC/mediaset-prod-all-programs-v2/'
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
        if self.isValidBeToken():
            self.cts = self.getAccount()['beToken']
        return (
            'https://widevine.entitlement.theplatform.eu/wv/web/ModularDrm/getRawWidevineLicense?'
            'releasePid={pid}&account=http://access.auth.theplatform.com/data/Account/'
            '2702976343&schema=1.0&token={cts}').format(pid=uid, cts=self.cts)
