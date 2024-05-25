# -*- coding: utf-8 -*-
from datetime import timedelta
from resources.lib.mediaset import Mediaset
from resources.lib.authentication import Authentication
from resources.mediaset_datahelper import (
    _gather_info,
    _gather_art,
    _gather_media_type,
    _safeGet,
)
from phate89lib import kodiutils, staticutils  # pyright: ignore[reportMissingImports]
from pprint import pformat
import json


class KodiMediaset(object):
    contextMenuMap = {
        "favorites": "Favoriti",
        "watchlist": "Guarda Dopo",
        "continuewatch": "Continua Guardare",
    }
    ADDON_SCROBBLING_CUSTOM = 1
    ADDON_SCROBBLING_NONE = 0

    def __init__(self):
        self.med = Mediaset()
        self.iperpage = kodiutils.getSetting("itemsperpage")
        self.detect_media_type = kodiutils.getSettingAsBool("detectmediatype")
        self.lookup_fullplot = kodiutils.getSettingAsBool("lookupfullplot")

    def __imposta_tipo_media(self, prog):
        if self.detect_media_type:
            mediaType = _gather_media_type(prog)
            kodiutils.log("__analizza_elenco mediatype: {}".format(mediaType), 4)
            if mediaType:
                kodiutils.setContent(mediaType + "s")

    def __geItemtArt(
        self, icon="Icona_APP.png", poster="", fanart="mediasetinfinity-keyframe.jpg"
    ):
        if not poster:
            poster = icon
        art = {}
        art["thumb"] = kodiutils.getMedia(icon)
        art["icon"] = kodiutils.getMedia(icon)
        art["poster"] = kodiutils.getMedia(poster)
        art["banner"] = kodiutils.getMedia(poster)
        art["landscape"] = (
            fanart if fanart.startswith("http") else kodiutils.getMedia(fanart)
        )
        art["fanart"] = (
            fanart if fanart.startswith("http") else kodiutils.getMedia(fanart)
        )
        art["clearart"] = (
            fanart if fanart.startswith("http") else kodiutils.getMedia(fanart)
        )
        art["clearlogo"] = kodiutils.getMedia(poster)
        return art

    def __getDirectoryArt(self, fanart="mediasetinfinity-keyframe.jpg"):
        return self.__geItemtArt("Icona_APP.png", fanart=fanart)

    def __getForwardArt(self, fanart="mediasetinfinity-keyframe.jpg"):
        return self.__geItemtArt("forward-darkorchid.png", fanart=fanart)

    def __getForwardText(self, color="darkorchid"):
        return self._getArrowText(True, kodiutils.LANGUAGE(32130), color=color)

    def __getBackwardArt(self, fanart="mediasetinfinity-keyframe.jpg"):
        return self.__geItemtArt("backward-darkorchid.png", fanart=fanart)

    def __getBackwardText(self, color="darkorchid"):
        return self._getArrowText(False, kodiutils.LANGUAGE(32129), color=color)

    def _getArrowText(self, isForward=True, text="", color=""):
        return "[COLOR {}][B]{} {}[/B][/COLOR]".format(
            color, ">>" if isForward else "<<", text
        )

    def __getUpArt(self, fanart="mediasetinfinity-keyframe.jpg"):
        return self.__geItemtArt("up-orange.png", fanart=fanart)

    def __getUpText(self, color="orange"):
        return self.__getOrderText("ASC", color=color)

    def __getDownArt(self, fanart="mediasetinfinity-keyframe.jpg"):
        return self.__geItemtArt("down-orange.png", fanart=fanart)

    def __getDownText(self, color="orange"):
        return self.__getOrderText("DESC", color=color)

    def __getOrderText(self, order="ASC", color=""):
        return "[COLOR {}][B]{} {}[/B][/COLOR]".format(
            color, "++" if order == "ASC" else "--", "Ordinamento"
        )

    def __getFavouriteArt(self):
        return self.__geItemtArt("favourite.png")

    def __getWatchlaterArt(self):
        return self.__geItemtArt("watchlater.png")

    def __getContinueArt(self):
        return self.__geItemtArt("continue.png")

    def __getAccountArt(self):
        return self.__geItemtArt("account.png")

    def __getLogoutArt(self):
        return self.__geItemtArt("logout.png")

    def __analizza_elenco(
        self,
        progs,
        setcontent=False,
        titlewd=False,
        isDeletable=False,
        delete_list="",
        context_ui="",
        blockMode="sezione",
        blockParams={},
        arts={},
    ):
        if not progs:
            return
        if setcontent:
            self.__imposta_tipo_media(progs[0])
        defaultArt = self.__getDirectoryArt()
        for prog in progs:
            infos = _gather_info(
                prog, titlewd=titlewd, lookup_fullplot=self.lookup_fullplot
            )
            arts = {**defaultArt, **arts, **_gather_art(prog)}
            # kodiutils.log("__analizza_elenco prog: {}".format(pformat(prog)))
            # kodiutils.log("__analizza_elenco infos: {}".format(pformat(infos)))
            # kodiutils.log("__analizza_elenco arts: {}".format(pformat(arts)))
            item_id = ""
            guid = ""
            args = {}
            properties = {}
            if "media" in prog:
                # kodiutils.log("__analizza_elenco media: {}".format(pformat(prog)), 4)
                args["mode"] = "video"
                # salta se non ha un media ma ha il tag perchè non riproducibile
                if prog["media"]:
                    media = prog["media"][0]
                    if "position" in prog:
                        args["offset"] = prog["position"]
                    if "pid" in media:
                        args["pid"] = media["pid"]
                    elif "publicUrl" in media:
                        args["pid"] = media["publicUrl"].split("/")[-1]
                    if "guid" in media:
                        args["guid"] = media["guid"]
                        guid = media["guid"]
                    if "mediasetprogram$duration" in prog:
                        properties["TotalTime"] = str(prog["mediasetprogram$duration"])
                    if "mediasetprogram$brandId" in prog:
                        item_id = prog["mediasetprogram$brandId"]
                    properties["ResumeTime"] = "0.0"
                    menuItems = self.menuItems(
                        isDeletable=isDeletable,
                        delete_list=delete_list,
                        item_id=item_id,
                        guid=guid,
                        context_ui=context_ui,
                    )
                    kodiutils.addListItem(
                        infos["title"],
                        args,
                        videoInfo=infos,
                        arts=arts,
                        isFolder=False,
                        properties=properties,
                        menuItems=menuItems,
                    )
            elif "tuningInstruction" in prog:
                # kodiutils.log("__analizza_elenco tuningInstruction: {}".format(pformat(prog)), 4)
                args["mode"] = "live"
                if prog["tuningInstruction"] and not prog["mediasetstation$eventBased"]:
                    vdata = prog["tuningInstruction"]["urn:theplatform:tv:location:any"]
                    for v in vdata:
                        if v["format"] == "application/x-mpegURL":
                            args["id"] = v["releasePids"][0]
                        else:
                            args["mid"] = v["releasePids"][0]
                    kodiutils.addListItem(
                        prog["title"], args, videoInfo=infos, arts=arts, isFolder=False
                    )
            elif "guid" in prog and prog["guid"] and prog["guid"].startswith("F"):
                args["mode"] = "video"
                args["guid"] = prog["guid"]
                properties["ResumeTime"] = "0.0"
                kodiutils.addListItem(
                    infos["title"],
                    args,
                    videoInfo=infos,
                    arts=arts,
                    isFolder=False,
                    properties=properties,
                )
            elif "mediasetprogram$subBrandId" in prog:
                # kodiutils.log("__analizza_elenco subBrandId: {}".format(pformat(prog)))
                item_id = (
                    prog["mediasetprogram$brandId"]
                    if prog["mediasetprogram$brandId"]
                    else ""
                )
                args["mode"] = "programma"
                args["sub_brand_id"] = prog["mediasetprogram$subBrandId"]
                menuItems = self.menuItems(
                    isDeletable=isDeletable,
                    delete_list=delete_list,
                    item_id=item_id,
                    guid=guid,
                    context_ui=context_ui,
                )
                kodiutils.addListItem(
                    infos["title"],
                    args,
                    videoInfo=infos,
                    arts=arts,
                    menuItems=menuItems,
                )
            # elif "mediasettvseason$brandId" in prog and "_aresId" not in prog:
            elif "mediasettvseason$brandId" in prog:
                # kodiutils.log("__analizza_elenco brandId: {}".format(pformat(prog)), 4)
                # title = prog['title']
                # if 'mediasettvseason$displaySeason' in prog and  'mediasetprogram$seasonTitle' in prog:
                item_id = (
                    prog["mediasettvseason$brandId"]
                    if prog["mediasettvseason$brandId"]
                    else ""
                )
                args["mode"] = "programma"
                args["brand_id"] = prog["mediasettvseason$brandId"]
                # args['sort'] = 'tvSeasonEpisodeNumber|asc'
                # args['order'] = 'asc'
                menuItems = self.menuItems(
                    isDeletable=isDeletable,
                    delete_list=delete_list,
                    item_id=item_id,
                    guid=guid,
                    context_ui=context_ui,
                )
                kodiutils.addListItem(
                    prog["title"], args, videoInfo=infos, arts=arts, menuItems=menuItems
                )
            elif "seriesId" in prog or (
                "programType" in prog
                and prog["programType"] == "series"
                and "id" in prog
            ):
                # kodiutils.log("__analizza_elenco seriesId: {}".format(pformat(prog)), 4)
                title = prog["title"]
                seriesTitle = prog["title"]
                sort = "tvSeasonNumber"
                order = "asc"
                item_id = (
                    prog["mediasetprogram$brandId"]
                    if "mediasetprogram$brandId" in prog
                    and prog["mediasetprogram$brandId"]
                    else ""
                )
                if (
                    "mediasetprogram$pageUrl" in prog
                    and "programmi-tv"
                    in str(prog["mediasetprogram$pageUrl"].encode("utf-8")).lower()
                ):
                    if (
                        "mediasetprogram$seasonTitle" in prog
                        and "mediasetprogram$displaySeason" in prog
                    ):
                        seasonTitle = str(
                            prog["mediasetprogram$seasonTitle"].encode("utf-8")
                        )
                        # displaySeason = str(prog['mediasetprogram$displaySeason'].encode('utf-8'))
                        seriesTitle = seasonTitle
                        title = seriesTitle
                args["mode"] = "programma"
                args["series_id"] = (
                    prog["seriesId"] if "seriesId" in prog else prog["id"]
                )
                args["sort"] = sort
                args["order"] = order
                args["title"] = seriesTitle
                menuItems = self.menuItems(
                    isDeletable=isDeletable,
                    delete_list=delete_list,
                    item_id=item_id,
                    guid=guid,
                    context_ui=context_ui,
                )
                kodiutils.addListItem(
                    title, args, videoInfo=infos, arts=arts, menuItems=menuItems
                )
            elif (
                "programType" in prog
                and prog["programType"] == "movie"
                and "id_brand" in prog
            ):
                # kodiutils.log("__analizza_elenco movie: {}".format(pformat(prog)), 4)
                item_id = prog["id_brand"] if prog["id_brand"] else ""
                args["mode"] = "programma"
                args["brand_id"] = prog["id_brand"]
                menuItems = self.menuItems(
                    isDeletable=isDeletable,
                    delete_list=delete_list,
                    item_id=item_id,
                    guid=guid,
                    context_ui=context_ui,
                )
                kodiutils.addListItem(
                    infos["title"],
                    args,
                    videoInfo=infos,
                    arts=arts,
                    menuItems=menuItems,
                )

            elif "_blockId" in prog:
                item_id = ""
                argsOverride = {"mode": blockMode}
                if "_viewAll" in prog:
                    argsOverride["shortId"] = prog["_viewAll"]
                args = {**blockParams, **argsOverride}
                # kodiutils.log("__analizza_elenco args: {}".format(pformat(args)), 4)
                kodiutils.addListItem(
                    infos["title"],
                    args,
                    videoInfo=infos,
                    arts=arts,
                )

            else:
                # kodiutils.log("__analizza_elenco other: {}".format(pformat(prog)), 4)
                item_id = (
                    prog["mediasetprogram$brandId"]
                    if "mediasetprogram$brandId" in prog
                    and prog["mediasetprogram$brandId"]
                    else ""
                )
                args["mode"] = "programma"
                args["brand_id"] = (
                    prog["mediasetprogram$brandId"]
                    if "mediasetprogram$brandId" in prog
                    and prog["mediasetprogram$brandId"]
                    else ""
                )
                menuItems = self.menuItems(
                    isDeletable=isDeletable,
                    delete_list=delete_list,
                    item_id=item_id,
                    guid=guid,
                    context_ui=context_ui,
                )
                kodiutils.addListItem(
                    prog["title"], args, videoInfo=infos, arts=arts, menuItems=menuItems
                )

    def menuItems(
        self, isDeletable=False, delete_list="", item_id="", guid="", context_ui=""
    ):
        # kodiutils.log(
        #     "menuItems: isDeletable={},delete_list={},item_id={},guid={},context_ui={}".format(
        #         isDeletable, delete_list, item_id, guid, context_ui
        #     )
        # )
        menuItems = []
        if self.med.isAnonymous():
            return menuItems
        if isDeletable:
            if delete_list == "favorites" and item_id:
                menuItems.append(
                    (
                        "Rimuovi (MediasetPlay)",
                        "RunPlugin(plugin://{}/?mode=contextmenu&context_menu={}&context_action=del&context_id={}&context_ui={})".format(
                            kodiutils.ID, delete_list, item_id, context_ui
                        ),
                    )
                )
            elif delete_list == "watchlist" and guid:
                menuItems.append(
                    (
                        "Rimuovi (MediasetPlay)",
                        "RunPlugin(plugin://{}/?mode=contextmenu&context_menu={}&context_action=del&context_id={}&context_ui={})".format(
                            kodiutils.ID, delete_list, guid, context_ui
                        ),
                    )
                )
        else:
            if guid:
                menuItems.append(
                    (
                        "Guarda Dopo (MediasetPlay)",
                        "RunPlugin(plugin://{}/?mode=contextmenu&context_menu=watchlist&context_action=add&context_id={}&context_ui={})".format(
                            kodiutils.ID, guid, context_ui
                        ),
                    )
                )
            elif item_id:
                menuItems.append(
                    (
                        "Preferiti (MediasetPlay)",
                        "RunPlugin(plugin://{}/?mode=contextmenu&context_menu=favorites&context_action=add&context_id={}&context_ui={})".format(
                            kodiutils.ID, item_id, context_ui
                        ),
                    )
                )
        return menuItems

    def root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem("On Demand", {"mode": "ondemand"}, arts=arts)
        kodiutils.addListItem("TV", {"mode": "tv"}, arts=arts)
        kodiutils.addListItem("Play Cult", {"mode": "cult"}, arts=arts)
        kodiutils.addListItem(kodiutils.LANGUAGE(32107), {"mode": "cerca"}, arts=arts)
        # kodiutils.addListItem('Le tue liste', {'mode': 'personal'}, arts=arts)
        if self.med.isAuthenticated():
            persona = self.med.getCurrentPersona()
            if persona and "name" in persona:
                kodiutils.addListItem(
                    "Account ([COLOR purple]{}[/COLOR])".format(persona["name"]),
                    {"mode": "account", "idPersona": persona["id"]},
                    arts=self.avatar(persona),
                )
        else:
            kodiutils.addListItem("Login", {"mode": "auth"}, arts=arts)
        kodiutils.endScript()

    def avatar(self, persona):
        avatar = self.__getDirectoryArt()
        if persona and "avatar" in persona and persona["avatar"]:
            avatar["thumb"] = persona["avatar"]
            avatar["icon"] = persona["avatar"]
        return avatar

    def auth(self):
        authentication = Authentication()
        if authentication.auth():
            kodiutils.log("auth success", 4)
            if self.med.isAuthenticated():
                kodiutils.log("auth isAuthenticated", 4)
                self.root()
            else:
                kodiutils.log("auth profile", 4)
                self.profile()
        else:
            kodiutils.log("auth failed", 4)
            kodiutils.endScript(closedir=False)

    def account(self):
        if self.med.isAuthenticated():
            personas = self.med.getPersonas()
            kodiutils.addListItem(
                "Continua a Guardare",
                {"mode": "continuewatch"},
                arts=self.__getContinueArt(),
            )
            kodiutils.addListItem(
                "Preferiti", {"mode": "favorites"}, arts=self.__getFavouriteArt()
            )
            kodiutils.addListItem(
                "Guarda Dopo", {"mode": "watchlist"}, arts=self.__getWatchlaterArt()
            )
            if personas and len(personas) > 1:
                kodiutils.addListItem(
                    "Cambia Profilo", {"mode": "profile"}, arts=self.__getAccountArt()
                )
            kodiutils.addListItem(
                "Logout", {"mode": "logout"}, arts=self.__getLogoutArt()
            )
            kodiutils.endScript()
        else:
            kodiutils.endScript(closedir=False)

    def profile(self, idPersona=None):
        if idPersona:
            currentPersona = self.med.getCurrentPersona()
            if not (
                currentPersona
                and "id" in currentPersona
                and currentPersona["id"] == idPersona
            ):
                if self.med.personaLogin(idPersona):
                    return self.root()
                else:
                    kodiutils.endScript(closedir=False)
        else:
            personas = self.med.getPersonas(excludeCurrent=True)
            if personas:
                for p in personas:
                    if "name" in p and "id" in p:
                        kodiutils.addListItem(
                            kodiutils.py2_decode(p["name"]),
                            {"mode": "profile", "idPersona": p["id"]},
                            arts=self.avatar(p),
                        )
                kodiutils.endScript()
            else:
                kodiutils.endScript(closedir=False)

    def logout(self):
        self.med.logout()
        self.root()

    def elenco_cerca_root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32121), {"mode": "cerca", "section": "all"}, arts=arts
        )
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32115), {"mode": "cerca", "section": "brand"}, arts=arts
        )
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32103), {"mode": "cerca", "section": "movie"}, arts=arts
        )
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32116), {"mode": "cerca", "section": "video"}, arts=arts
        )
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32117),
            {"mode": "cerca", "section": "subscription"},
            arts=arts,
        )
        kodiutils.addListItem(
            "Ricerche frequenti",
            {"mode": "cerca", "section": "all", "search": " "},
            arts=arts,
        )
        kodiutils.endScript()

    def apri_ricerca(self, section):
        text = kodiutils.getKeyboardText(kodiutils.LANGUAGE(32131))
        if text:
            self.elenco_cerca_sezione(
                section=section, search=text, checkSingleBlock=False
            )
        else:
            self.elenco_cerca_root()

    def elenco_cerca_sezione(
        self, section="all", search="", shortId="", page=1, checkSingleBlock=True
    ):
        if search:
            els, hasMore = self.med.Cerca(
                search,
                section=section,
                shortId=shortId,
                pageels=self.iperpage,
                page=page,
                checkSingleBlock=checkSingleBlock,
            )
            # kodiutils.log(("elenco_cerca_sezione: els={}").format(pformat(els)), 4)
            if els:
                for item in els:
                    if not ("title" in item and item["title"]):
                        item["title"] = (
                            "Programmi e serie | Film"
                            if section in ["all", "subscription"]
                            else "Risultati"
                        )
                    currentTotalHits = (
                        "({})".format(len(item["items"])) if "items" in item else ""
                    )
                    item["title"] = "{} {}".format(item["title"], currentTotalHits)
                if hasMore:
                    kodiutils.addListItem(
                        self.__getForwardText(),
                        {
                            "mode": "cerca",
                            "search": search,
                            "section": section,
                            "shortId": shortId,
                            "page": page + 1,
                        },
                        properties={"SpecialSort": "top"},
                        arts=self.__getForwardArt(),
                    )
                if page > 1:
                    kodiutils.addListItem(
                        self.__getBackwardText(),
                        {
                            "mode": "cerca",
                            "search": search,
                            "section": section,
                            "shortId": shortId,
                            "page": page - 1,
                        },
                        properties={"SpecialSort": "top"},
                        arts=self.__getBackwardArt(),
                    )
                # exttitle = {
                #     "programmi": False,
                #     "clip": True,
                #     "episodi": True,
                #     "film": False,
                # }
                if not (
                    els[0] and "title" in els[0] and els[0]["title"] == "no-results"
                ):
                    self.__analizza_elenco(
                        els,
                        blockMode="cerca",
                        blockParams={
                            "section": section,
                            "search": search,
                            "shortId": shortId,
                        },
                    )  # , titlewd=exttitle.get(section, False))
        kodiutils.endScript()

    def elenco_ondemand_root(self):
        defaultArt = self.__getDirectoryArt()
        for item in self.med.OttieniOnDemand():
            # kodiutils.log(("elenco_ondemand_root: item={}").format(pformat(item)), 4)
            arts = {**defaultArt, **_gather_art(item)}
            kodiutils.addListItem(
                item["title"],
                {"mode": "ondemand", "id": item["id"], "include": "1"},
                arts=arts,
            )
        kodiutils.endScript()

    def elenco_ondemand(
        self,
        id="",
        include="1",
        forceItems="0",
        contentType="",
        fields="",
        feedParams="",
        template=None,
        sort="",
        order="asc",
        page=1,
        size=0,
    ):
        kodiutils.log(
            (
                "elenco_ondemand: id={},include={},forceItems={},fields={},feedParams={},template={},sort={},order={},page={},size={}"
            ).format(
                str(id),
                str(include),
                str(forceItems),
                str(fields),
                str(feedParams),
                str(template),
                str(sort),
                str(order),
                str(page),
                str(size),
            ),
            4,
        )

        defaultArt = self.__getDirectoryArt()

        size = int(size) if size else int(self.iperpage)
        page = int(page) if page else 1
        update_listing = page > 1

        query = {
            "sys.id": id,
            "include": include,
            "content_type": contentType,
            "limit": "100",
        }

        if include == "0" or forceItems == "1":
            if size:
                query["limit"] = str(size)
            if page and size:
                query["skip"] = str(page * size)

        if fields:
            for fieldsInner in fields.split("|"):
                for fieldsVars in fieldsInner.split("@"):
                    if fieldsVars and len(fieldsVars) == 2:
                        query[fieldsVars[0]] = fieldsVars[1]

        if feedParams:
            for feedInner in feedParams.split("|"):
                feedVars = feedInner.split("@")
                if feedVars and len(feedVars) == 2:
                    query[feedVars[0]] = feedVars[1]

        data, hasMore = self.med.OttieniOnDemandQuery(
            query, forceItems=forceItems, sort=sort, order=order
        )

        if include == "0" or forceItems == "1":
            if hasMore:
                kodiutils.addListItem(
                    self.__getForwardText(),
                    {
                        "mode": "ondemand",
                        "id": id if id else "",
                        "include": include if include else "",
                        "forceItems": forceItems if forceItems else "",
                        "contentType": contentType if contentType else "",
                        "fields": fields if fields else "",
                        "feedParams": feedParams if feedParams else "",
                        "template": template if template else "",
                        "sort": sort if sort else "",
                        "order": order if order else "",
                        "page": page + 1,
                        "size": size,
                    },
                    properties={"SpecialSort": "top"},
                    arts=self.__getForwardArt(),
                )
            if page > 0:
                kodiutils.addListItem(
                    self.__getBackwardText(),
                    {
                        "mode": "ondemand",
                        "id": id if id else "",
                        "include": include if include else "",
                        "forceItems": forceItems if forceItems else "",
                        "contentType": contentType if contentType else "",
                        "fields": fields if fields else "",
                        "feedParams": feedParams if feedParams else "",
                        "template": template if template else "",
                        "sort": sort if sort else "",
                        "order": order if order else "",
                        "page": page - 1,
                        "size": size,
                    },
                    properties={"SpecialSort": "top"},
                    arts=self.__getBackwardArt(),
                )

        for sec in data:
            # kodiutils.log("elenco_ondemand sec={}".format(pformat(sec)), 4)
            if template and (
                ("template" in sec and str(sec["template"]) not in template.split("|"))
                or "template" not in sec
            ):
                continue
            if "platform" in sec and "web" not in sec["platform"]:
                continue
            if "title" not in sec:
                if _safeGet(sec, "uxReferenceV2") == "filmClustering":
                    sec["title"] = "Da non perdere"
                else:
                    sec["title"] = "Altro"
            if _safeGet(sec, "showFor4k") and _safeGet(sec, "title"):
                sec["title"] = "{} ({})".format(sec["title"], sec["showFor4k"])

            infos = _gather_info(sec)
            arts = {**defaultArt, **_gather_art(sec)}
            # kodiutils.log(("elenco_ondemand infos: {}").format(str(infos)), 4)
            # kodiutils.log(("elenco_ondemand arts: {}").format(str(arts)), 4)

            if "uxReferenceV2" in sec:
                # kodiutils.log(("elenco_ondemand uxReferenceV2: {}").format(str(sec)), 4)
                additionalParams = (
                    sec["uxReferenceV2Params"] if "uxReferenceV2Params" in sec else None
                )
                kodiutils.addListItem(
                    sec["title"],
                    {
                        "mode": "sezione",
                        "id": sec["uxReferenceV2"],
                        "params": additionalParams,
                        "posterImage": _safeGet(arts, "poster"),
                        "keyframeImage": _safeGet(arts, "banner"),
                    },
                    arts=arts,
                    videoInfo=infos,
                )
            elif "uxReference" in sec:
                # kodiutils.log(("elenco_ondemand uxReference: {}").format(str(sec)), 4)
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "sezione", "id": sec["uxReference"]},
                    arts=arts,
                    videoInfo=infos,
                )
            elif "newsFeedUrl" in sec:
                # kodiutils.log(("elenco_ondemand newsFeedUrl: {}").format(str(sec)), 4)
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "magazine", "newsFeedUrl": sec["newsFeedUrl"]},
                    arts=arts,
                    videoInfo=infos,
                )
            elif "feedurlV2" in sec:
                # kodiutils.log(("elenco_ondemand feedurl: {}").format(str(sec)), 4)
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "cult", "feedurl": sec["feedurlV2"]},
                    arts=arts,
                    videoInfo=infos,
                )
            elif "feedurl" in sec:
                # kodiutils.log(("elenco_ondemand feedurl: {}").format(str(sec)), 4)
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "cult", "feedurl": sec["feedurl"]},
                    arts=arts,
                    videoInfo=infos,
                )
            elif "feedParams" in sec:
                # kodiutils.log(("elenco_ondemand feedParams: {}").format(str(sec)), 4)
                feedParamsJson = json.loads(sec["feedParams"])
                if (
                    feedParamsJson
                    and "feedParams" in feedParamsJson
                    and feedParamsJson["feedParams"]
                ):
                    feedParams = "|".join(
                        [k + "@" + v for k, v in feedParamsJson["feedParams"].items()]
                    )
                    kodiutils.addListItem(
                        sec["title"],
                        {
                            "mode": "ondemand",
                            "feedParams": feedParams,
                            "include": "1",
                            "forceItems": "1",
                        },
                        arts=arts,
                        videoInfo=infos,
                    )
            elif _safeGet(sec, "contentType") in ["videoembed", "article"] and _safeGet(
                sec, "guid"
            ):
                kodiutils.addListItem(
                    "Video",
                    {"mode": "video", "guid": _safeGet(sec, "guid")},
                    arts=arts,
                    videoInfo=infos,
                    isFolder=False,
                )
            elif _safeGet(sec, "contentType") in ["article"] and _safeGet(
                sec, "seriesId"
            ):
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "programma", "series_guid": _safeGet(sec, "seriesId")},
                    arts=arts,
                    videoInfo=infos,
                )
            elif _safeGet(sec, "contentType") in ["article"] and _safeGet(sec, "id"):
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "ondemand", "id": _safeGet(sec, "id"), "include": "1"},
                    arts=arts,
                    videoInfo=infos,
                )
            # else:
            #     kodiutils.log(("elenco_ondemand other: {}").format(pformat(sec)), 4)

        kodiutils.endScript(closedir=True, update_listing=update_listing)

    def elenco_cult_root(self):
        defaultArt = self.__getDirectoryArt()
        query = {
            "include": "0",
            "content_type": "pageTemplate",
            "fields.seriesId": "SE000000000641",
        }
        items, _ = self.med.OttieniOnDemandQuery(query, "pageUrl", "asc")
        for item in items:
            # kodiutils.log(("elenco_cult_root: item={}").format(pformat(item)), 4)
            if "title" in item and "id" in item:
                arts = {**defaultArt, **_gather_art(item)}
                kodiutils.addListItem(
                    item["title"],
                    {
                        "mode": "ondemand",
                        "id": item["id"],
                        "include": "1",
                        "sort": "title",
                        "order": "asc",
                    },
                    arts=arts,
                )
        # kodiutils.addListItem(
        #     "Home",
        #     {
        #         "mode": "ondemand",
        #         "id": "5dada71d23eec6001ba1a83b",
        #         "template": "keyframe|playlist",
        #         "sort": "title",
        #     },
        #     arts=arts,
        # )
        # kodiutils.addListItem(
        #     "Tutti i Video",
        #     {
        #         "mode": "ondemand",
        #         "id": "5c0ff291a0e845001bb455bf",
        #         "template": "keyframe|playlist",
        #         "sort": "title",
        #     },
        #     arts=arts,
        # )
        kodiutils.endScript()

    def elenco_cult(self, feedurl, page_action=""):
        els, nextPage, prevPage = self.med.OttieniCult(feedurl, self.iperpage)
        update_listing = page_action == "next" or page_action == "prev"
        kodiutils.log(("elenco_cult: {}").format(str(update_listing)), 4)
        if nextPage:
            kodiutils.addListItem(
                self.__getForwardText(),
                {"mode": "cult", "feedurl": nextPage, "page_action": "next"},
                properties={"SpecialSort": "top"},
                arts=self.__getForwardArt(),
            )
        if prevPage:
            kodiutils.addListItem(
                self.__getBackwardText(),
                {"mode": "cult", "feedurl": prevPage, "page_action": "prev"},
                properties={"SpecialSort": "top"},
                arts=self.__getBackwardArt(),
            )
        self.__analizza_elenco(els, True)
        kodiutils.endScript(update_listing=update_listing)

    def elenco_magazine(self, newsFeedUrl, page_action=""):
        arts = self.__getDirectoryArt()
        els, nextPage, prevPage = self.med.OttieniMagazine(newsFeedUrl, self.iperpage)
        update_listing = page_action == "next" or page_action == "prev"
        if nextPage:
            kodiutils.addListItem(
                self.__getForwardText(),
                {"mode": "magazine", "newsFeedUrl": nextPage, "page_action": "next"},
                properties={"SpecialSort": "top"},
                arts=self.__getForwardArt(),
            )
        if prevPage:
            kodiutils.addListItem(
                self.__getBackwardText(),
                {"mode": "magazine", "newsFeedUrl": prevPage, "page_action": "prev"},
                properties={"SpecialSort": "top"},
                arts=self.__getBackwardArt(),
            )
        for sec in els:
            if "metainfo" in sec and "ddg_url" in sec["metainfo"]:
                kodiutils.addListItem(
                    sec["title"],
                    {"mode": "magazine", "ddg_url": sec["metainfo"]["ddg_url"]},
                    arts=arts,
                )
        kodiutils.log(("update_listing: {}").format(str(update_listing)), 4)
        kodiutils.endScript(update_listing=update_listing)

    def elenco_news(self, ddg_url):
        els = self.med.OttieniNews(ddg_url)
        self.__analizza_elenco(els, True)
        kodiutils.endScript()

    def elenco_sezione(
        self,
        id="",
        shortId="",
        page=1,
        params="",
        posterImage="",
        keyframeImage="",
        sort="",
        order="",
        size=0,
    ):
        kodiutils.log(
            "[main] elenco_sezione: id={},shortId={},params={},page={},sort={},order={}".format(
                str(id), str(shortId), str(params), str(page), str(sort), str(order)
            )
        )

        arts = {}
        if posterImage:
            arts["poster"] = posterImage
            arts["thumb"] = posterImage
            arts["icon"] = posterImage
        if keyframeImage:
            arts["banner"] = keyframeImage
            arts["fanart"] = keyframeImage
            arts["clearart"] = keyframeImage

        size = int(size) if size else int(self.iperpage)
        page = int(page) if page else 1
        update_listing = page > 1

        els, hasmore = self.med.OttieniProgrammiGenere(
            id, {"shortId": shortId}, size, page, params, sort, order
        )
        # kodiutils.log(
        #     "elenco_sezione size={},hasmore={}: {}".format(
        #         str(size), str(hasmore), pformat(els)
        #     ),
        #     4,
        # )
        if els:
            fanart = str(_safeGet(arts, "fanart"))
            if hasmore:
                kodiutils.addListItem(
                    self.__getForwardText(),
                    {
                        "mode": "sezione",
                        "id": id,
                        "shortId": shortId,
                        "params": params,
                        "page": page + 1,
                        "posterImage": posterImage,
                        "keyframeImage": keyframeImage,
                    },
                    properties={"SpecialSort": "top"},
                    arts=self.__getForwardArt(fanart=fanart),
                )
            if page > 1:
                kodiutils.addListItem(
                    self.__getBackwardText(),
                    {
                        "mode": "sezione",
                        "id": id,
                        "shortId": shortId,
                        "params": params,
                        "page": page - 1,
                        "posterImage": posterImage,
                        "keyframeImage": keyframeImage,
                    },
                    properties={"SpecialSort": "top"},
                    arts=self.__getBackwardArt(fanart=fanart),
                )
            self.__analizza_elenco(
                els,
                setcontent=True,
                arts=arts,
                blockParams={
                    "posterImage": posterImage,
                    "keyframeImage": keyframeImage,
                },
            )
            # else:
            #     kodiutils.addListItem('Ordina {}'.format('DESC' if sort and order == 'asc' else 'ASC'), {
            #         'mode': 'sezione', 'id': id,
            #         'sort': sort if sort else 'title',
            #         'order': 'desc' if sort and order == 'asc' else 'asc'})
        kodiutils.endScript(update_listing=update_listing)

    def elenco_stagioni_list(
        self, series_id="", series_guid="", title="", sort="", order="asc"
    ):
        title = kodiutils.py2_encode(title)
        kodiutils.log(
            "[main] elenco_stagioni_list: series_id={},series_guid={},title={},sort={},order={}".format(
                series_id, series_guid, title, sort, order
            )
        )
        els, _ = self.med.OttieniStagioni(
            seriesId=series_id, seriesGuid=series_guid, sort=sort, order=order
        )
        if els:
            if len(els) == 1:
                self.elenco_sezioni_list(els[0]["mediasettvseason$brandId"])
            else:
                self.__analizza_elenco(els)
                kodiutils.endScript()
        else:
            kodiutils.endScript()
            # workaround per controllare se è già una stagione e non una serie
            # brandId = -1
            # for el in els:
            #     kodiutils.log(("el: {}").format(str(el)), 4)
            #     if kodiutils.py2_encode(el["title"]) == title:
            #         brandId = el["mediasettvseason$brandId"]
            #         break
            # kodiutils.log(("brandId: {}").format(str(brandId)), 4)
            # if brandId == -1:
            #     self.__analizza_elenco(els)
            #     kodiutils.endScript()
            # else:
            #     kodiutils.addListItem(
            #         "Tutte le Stagioni",
            #         {
            #             "mode": "programma",
            #             "series_id": series_id,
            #             "title": "*",
            #             "sort": sort,
            #             "order": order,
            #         },
            #         properties={"SpecialSort": "top"},
            #         arts=self.__getDirectoryArt(),
            #     )
            #     self.elenco_sezioni_list(brandId)

    def elenco_sezioni_list(
        self, brandId, sort="mediasetprogram$order|asc,tvSeasonEpisodeNumber|asc"
    ):
        kodiutils.log(
            "[main] elenco_sezioni_list: brandId={},sort={}".format(
                str(brandId), str(sort)
            )
        )
        els, _ = self.med.OttieniSezioniProgramma(brandId, sort=sort)
        # if not els:
        # els = []
        # if len(els) == 2:
        #     self.elenco_video_list(els[1]["mediasetprogram$subBrandId"], sort=sort)
        if els:
            self.__imposta_tipo_media(els[0])
            defaultArts = self.__getDirectoryArt()
            arts = {**defaultArts, **_gather_art(els[0])}
            # kodiutils.log("elenco_sezioni_list art: {}".format(pformat(arts)))
            if "seriesId" in els[0] and els[0]["seriesId"]:
                tvseasons, _ = self.med.OttieniStagioni(
                    seriesId=str(els[0]["seriesId"])
                )
                if tvseasons and len(tvseasons) > 1:
                    kodiutils.addListItem(
                        "Tutte le Stagioni",
                        {
                            "mode": "programma",
                            "series_id": els[0]["seriesId"],
                            "title": "*",
                            "sort": "tvSeasonNumber",
                            "order": "asc",
                        },
                        properties={"SpecialSort": "top"},
                        arts=arts,
                    )
                els.pop(0)
                self.__analizza_elenco(els, arts=arts)
            elif (
                len(els) == 2
                and "mediasetprogram$subBrandId" in els[1]
                and els[1]["mediasetprogram$subBrandId"]
            ):
                self.elenco_video_list(els[1]["mediasetprogram$subBrandId"], sort=sort)
            else:
                els.pop(0)
                self.__analizza_elenco(els, arts=arts)
        kodiutils.endScript()

    def elenco_video_list(
        self,
        sub_brand_id,
        mode="programma",
        sort="",
        page=1,
        size=0,
    ):
        kodiutils.log(
            "[main] elenco_video_list: sub_brand_id={},mode={},sort={},page={},size={}".format(
                str(sub_brand_id), str(mode), str(sort), str(page), str(size)
            )
        )

        if not sort:
            update_listing = False
            sortSetting = kodiutils.getSettingAsNum("sort")
            if sortSetting:
                sort = ":publishInfo_lastPublished|desc,tvSeasonEpisodeNumber|desc"
            else:
                sort = ":publishInfo_lastPublished|asc,tvSeasonEpisodeNumber|asc"
        else:
            update_listing = True

        size = int(size) if size else int(self.iperpage)
        page = int(page) if page else 1

        els, hasMore = self.med.OttieniVideoSezione(
            sub_brand_id, sort=sort, page=page, size=size
        )
        defaultArt = _gather_art(els[0]) if els else self.__getDirectoryArt()
        fanart = str(
            _safeGet(defaultArt, "landscape") or _safeGet(defaultArt, "fanart")
        )

        if hasMore:
            kodiutils.addListItem(
                self.__getForwardText(),
                {
                    "mode": mode,
                    "sub_brand_id": sub_brand_id,
                    "sort": sort,
                    "page": page + 1,
                    "size": size,
                },
                properties={"SpecialSort": "top"},
                arts=self.__getForwardArt(fanart=fanart),
            )
        if page > 1:
            update_listing = True
            kodiutils.addListItem(
                self.__getBackwardText(),
                {
                    "mode": mode,
                    "sub_brand_id": sub_brand_id,
                    "sort": sort,
                    "page": page - 1,
                    "size": size,
                },
                properties={"SpecialSort": "top"},
                arts=self.__getBackwardArt(fanart=fanart),
            )
        if els and len(els) > 1:
            toggleSort = (
                sort.replace("asc", "▲")
                .replace("desc", "▼")
                .replace("▲", "desc")
                .replace("▼", "asc")
            )
            toggleSortLabel = (
                self.__getUpText() if "desc" in toggleSort else self.__getDownText()
            )
            toggleSortArt = (
                self.__getUpArt(fanart=fanart)
                if "desc" in toggleSort
                else self.__getDownArt(fanart=fanart)
            )
            kodiutils.addListItem(
                toggleSortLabel,
                {
                    "mode": mode,
                    "sub_brand_id": sub_brand_id,
                    "sort": toggleSort,
                    "page": 1,
                    "size": size,
                },
                properties={"SpecialSort": "top"},
                arts=toggleSortArt,
            )
        if els:
            self.__analizza_elenco(els, True)
        kodiutils.endScript(update_listing=update_listing)

    def continuewatch(self):
        if self.med.isAuthenticated():
            els, _ = self.med.OttieniContinuaGardare()
            self.__analizza_elenco(els)
        kodiutils.endScript()

    def favorites(self):
        if self.med.isAuthenticated():
            els, _ = self.med.OttieniFavoriti()
            self.__analizza_elenco(
                els, isDeletable=True, delete_list="favorites", context_ui="refresh"
            )
        kodiutils.endScript()

    def watchlist(self):
        if self.med.isAuthenticated():
            els, _ = self.med.OttieniWatchlist()
            self.__analizza_elenco(
                els, isDeletable=True, delete_list="watchlist", context_ui="refresh"
            )
        kodiutils.endScript()

    def contextMenu(self, context_menu, context_action, context_id, context_ui=""):
        deleted = False
        added = False
        with kodiutils.busy_dialog():
            if context_menu and context_action and context_id:
                if context_menu and context_action and context_id:
                    if self.med.isAuthenticated():
                        if context_action == "add":
                            added = self.med.AggiungiLista(context_menu, context_id)
                        elif context_action == "del":
                            deleted = self.med.EliminaLista(context_menu, context_id)
        if added:
            kodiutils.notify(
                "Aggiunto a {}".format(self.contextMenuMap[context_menu]),
                icon=kodiutils.getMedia("Icona_APP.png"),
            )
        elif deleted:
            kodiutils.notify(
                "Rimosso da {}".format(self.contextMenuMap[context_menu]),
                icon=kodiutils.getMedia("Icona_APP.png"),
            )
        update_dir = context_ui == "refresh" and (added or deleted)
        kodiutils.endScript(closedir=False, update_dir=update_dir)

    def tv_root(self):
        arts = self.__getDirectoryArt()
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32111), {"mode": "canali_live"}, arts=arts
        )
        kodiutils.addListItem(
            kodiutils.LANGUAGE(32113), {"mode": "guida_tv"}, arts=arts
        )
        kodiutils.endScript()

    def guida_tv_root(self):
        kodiutils.setContent("videos")
        els, _ = self.med.OttieniCanaliLive(sort="ShortTitle", channelTypes=["TV"])
        for prog in els:
            # kodiutils.log(("prog: {}").format(pformat(prog)), 4)
            infos = _gather_info(prog)
            arts = _gather_art(prog)
            if "tuningInstruction" in prog:
                if prog["tuningInstruction"] and not (
                    "mediasetstation$eventBased" in prog
                    and prog["mediasetstation$eventBased"]
                ):
                    kodiutils.addListItem(
                        prog["title"],
                        {
                            "mode": "guida_tv",
                            "id": prog["callSign"],
                            "week": staticutils.get_timestamp_midnight(),
                        },
                        videoInfo=infos,
                        arts=arts,
                    )
        kodiutils.endScript()

    def guida_tv_canale_settimana(self, cid, dt):
        dt = staticutils.get_date_from_timestamp(dt)
        for d in range(0, 16):
            currdate = dt - timedelta(days=d)
            kodiutils.addListItem(
                kodiutils.getFormattedDate(currdate),
                {
                    "mode": "guida_tv",
                    "id": cid,
                    "day": staticutils.get_timestamp_midnight(currdate),
                },
            )
        # kodiutils.addListItem(kodiutils.LANGUAGE(32136),
        #                       {'mode': 'guida_tv', 'id': cid,
        #                       'week': staticutils.get_timestamp_midnight(dt - timedelta(days=7))})
        kodiutils.endScript()

    def guida_tv_canale_giorno(self, cid, dt):
        res = self.med.OttieniEpgListing(
            cid, dt, dt + 86399999
        )  # 86399999 is one day minus 1 ms
        kodiutils.setContent("episodes")
        if res:
            for el in res:
                program = el["program"] if "program" in el else el
                if kodiutils.getSettingAsBool("fullguide") or (
                    "mediasetprogram$hasVod" in program
                    and program["mediasetprogram$hasVod"]
                ):
                    # kodiutils.log(('guida_tv_canale_giorno el={}').format(str(el)))
                    infos = _gather_info(program)
                    arts = _gather_art(program)
                    s_time = staticutils.get_date_from_timestamp(
                        el["startTime"]
                    ).strftime("%H:%M")
                    e_time = staticutils.get_date_from_timestamp(
                        el["endTime"]
                    ).strftime("%H:%M")
                    programType = _gather_media_type(program)
                    showTitle = str(el["mediasetlisting$epgTitle"])
                    episodeTitle = (
                        str(program["title"]) if programType != "movie" else ""
                    )
                    infos["title"] = (
                        "[COLOR blue][B]{s} - {e}[/B][/COLOR] [COLOR cyan]{t}[/COLOR] [I]{u}[/I]".format(
                            s=s_time, e=e_time, t=showTitle, u=episodeTitle
                        )
                    )
                    kodiutils.addListItem(
                        infos["title"],
                        {"mode": "video", "guid": program["guid"]},
                        videoInfo=infos,
                        arts=arts,
                        properties={
                            "ResumeTime": "0.0",
                            "TotalTime": "0.0",
                            "StartOffset": "0.0",
                        },
                        isFolder=False,
                    )
        kodiutils.endScript()

    def canali_live_root(self):
        kodiutils.setContent("videos")
        els, _ = self.med.OttieniCanaliLive(sort="ShortTitle")
        chans = self.med.OttieniEpg()
        for el in els:
            if el["callSign"] in chans:
                callSign = el["callSign"]
                liveChannel = chans[callSign]
                # kodiutils.log(
                #     ("canali_live_root liveChannel={}").format(pformat(liveChannel))
                # )
                prog = liveChannel["currentListing"]
                program = prog["program"]
                chan = liveChannel["station"]
                infos = _gather_info(program)
                arts = {**_gather_art(program), **_gather_art(chan)}
                programType = _gather_media_type(program)
                showTitle = str(prog["mediasetlisting$epgTitle"])
                episodeTitle = (
                    str(program["title"])
                    if programType != "movie"
                    and program["title"] != prog["mediasetlisting$epgTitle"]
                    else ""
                )
                infos["title"] = (
                    "[COLOR blue][B]{channel}[/B][/COLOR] [COLOR cyan]{showTitle}[/COLOR] [I]{episodeTitle}[/I]".format(
                        showTitle=showTitle,
                        channel=chan["title"],
                        episodeTitle=episodeTitle,
                    )
                )
                data = {"mode": "live", "guid": callSign}
                if (
                    "mediasetlisting$restartAllowed" in prog
                    and prog["mediasetlisting$restartAllowed"]
                    and kodiutils.getSettingAsBool("splitlive")
                ):
                    data["tuning"] = "split"
                else:
                    data["tuning"] = "live"
                    data["publicUrl"] = liveChannel["publicUrl"]
                kodiutils.addListItem(
                    infos["title"],
                    data,
                    videoInfo=infos,
                    arts=arts,
                    isFolder=(data["tuning"] == "split"),
                )
        kodiutils.endScript()

    # def __ottieni_vid_restart(self, guid):
    #     res = self.med.OttieniLiveStream(guid)
    #     if (
    #         "currentListing" in res[0]
    #         and res[0]["currentListing"]["mediasetlisting$restartAllowed"]
    #     ):
    #         url = res[0]["currentListing"]["restartUrl"]
    #         return url.rpartition("/")[-1]
    #     return None

    def canali_live_play(self, guid):
        kodiutils.setContent("episodes")
        chans = self.med.OttieniEpg(callSign=guid)
        if chans and guid in chans:
            liveChannel = chans[guid]
            # kodiutils.log(("canali_live_play liveChannel={}").format(pformat(liveChannel)))
            prog = liveChannel["currentListing"]
            chan = liveChannel["station"]
            infos = _gather_info(prog)
            arts = {**_gather_art(prog), **_gather_art(chan)}

            if "mediasetlisting$epgTitle" in prog:
                infos["title"] = prog["mediasetlisting$epgTitle"]
                if (
                    "mediasetlisting$shortDescription" in prog
                    and prog["mediasetlisting$shortDescription"]
                ):
                    infos["title"] += " - " + prog["mediasetlisting$shortDescription"]
            elif "title" in prog:
                infos["title"] = prog["title"]

            title = infos["title"]
            infos["title"] = "([COLOR green]{}[/COLOR]) {}".format(
                kodiutils.LANGUAGE(32137), title
            )
            kodiutils.addListItem(
                infos["title"],
                {"mode": "live", "guid": guid, "tuning": "live"},
                properties={"ResumeTime": "0.0"},
                videoInfo=infos,
                arts=arts,
                isFolder=False,
            )

            infos["title"] = "([COLOR yellow]{}[/COLOR]) {}".format(
                kodiutils.LANGUAGE(32138), title
            )
            kodiutils.addListItem(
                infos["title"],
                {"mode": "live", "guid": guid, "tuning": "restart"},
                properties={"ResumeTime": "0.0"},
                videoInfo=infos,
                arts=arts,
                isFolder=False,
            )

        kodiutils.endScript()

    def riproduci_guid(self, guid="", offset=None):
        kodiutils.log("riproduci_guid: guid={}, offset={}".format(guid, offset))
        res = self.med.OttieniInfoDaGuid(guid)
        if not res or "media" not in res:
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32136))
            kodiutils.setResolvedUrl(solved=False)
            return
        self.riproduci_video(guid=guid, pid=res["media"][0]["pid"], offset=offset)

    def riproduci_video(
        self, guid="", pid="", publicUrl="", live=False, offset=None, tuning=None
    ):
        from inputstreamhelper import Helper  # pyright: ignore[reportMissingImports]

        kodiutils.log(
            "riproduci_video: guid={}, pid={}, live={}, offset={}".format(
                guid, pid, live, offset
            )
        )

        data = self.med.OttieniDatiVideo(guid, publicUrl, live, tuning)
        kodiutils.log("riproduci_video: data={}".format(pformat(data)))

        if not (data and "url" in data):
            # kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32133))
            kodiutils.setResolvedUrl(solved=False)
            return

        if data["type"] == "video/mp4":
            kodiutils.setResolvedUrl(data["url"])
            return

        is_helper = Helper("mpd", "com.widevine.alpha" if data["security"] else None)
        if not is_helper.check_inputstream():
            kodiutils.showOkDialog(kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32133))
            kodiutils.setResolvedUrl(solved=False)
            return

        headers = {}
        ins_data = data["manifest"] if "manifest" in data else {}

        properties = {"ResumeTime": "0.0"}

        scrobbling = kodiutils.getSettingAsNum("scrobbling")
        if scrobbling and not self.med.isAnonymous():
            properties["guid"] = guid
            if scrobbling == self.ADDON_SCROBBLING_CUSTOM:
                if offset:
                    properties["offset"] = str(offset)
                else:
                    if self.med.isAuthenticated():
                        offset = self.med.getProgress(guid)
                        if offset:
                            properties["offset"] = str(offset)

        if data["security"]:
            if not self.med.isValidBeToken():
                kodiutils.showOkDialog(
                    kodiutils.LANGUAGE(32132), kodiutils.LANGUAGE(32135)
                )
                kodiutils.setResolvedUrl(solved=False)
                return
            ins_data["license_type"] = "com.widevine.alpha"
            ins_data["license_key"] = self.med.OttieniWidevineAuthUrl(data["pid"])

        kodiutils.log("riproduci_video url: %s" % data["url"])
        kodiutils.log("riproduci_video headers: %s" % headers)
        kodiutils.log("riproduci_video properties: %s" % properties)
        kodiutils.log("riproduci_video ins_data: %s" % ins_data)

        kodiutils.setResolvedUrl(
            data["url"],
            headers=headers,
            ins=is_helper.inputstream_addon,
            insdata=ins_data,
            properties=properties,
        )

    def sliceParams(self, params, keys):
        return {key: params[key] for key in set(keys) & set(params)}

    def main(self):
        # parameter values
        params = staticutils.getParams()
        kodiutils.log("[main] params: {}".format(str(params)))
        if "mode" in params:
            if "page" in params:
                try:
                    params["page"] = int(params["page"])
                except ValueError:
                    pass
            self.iperpage = min(kodiutils.getSettingAsNum("itemsperpage"), 10)
            if params["mode"] == "cerca":
                if "section" in params:
                    if "search" in params:
                        self.elenco_cerca_sezione(
                            **self.sliceParams(
                                params,
                                ("section", "search", "shortId", "page"),
                            )
                        )
                    else:
                        self.apri_ricerca(section=params["section"])
                else:
                    self.elenco_cerca_root()
            elif params["mode"] == "sezione":
                self.elenco_sezione(
                    **self.sliceParams(
                        params,
                        (
                            "id",
                            "shortId",
                            "params",
                            "posterImage",
                            "keyframeImage",
                            "page",
                            "sort",
                            "order",
                        ),
                    )
                )
            elif params["mode"] == "ondemand":
                if "id" in params or "feedParams" in params or "fields" in params:
                    self.elenco_ondemand(
                        **self.sliceParams(
                            params,
                            (
                                "id",
                                "include",
                                "forceItems",
                                "contentType",
                                "fields",
                                "feedParams",
                                "template",
                                "sort",
                                "order",
                                "page",
                                "size",
                            ),
                        )
                    )
                else:
                    self.elenco_ondemand_root()
            elif params["mode"] == "cult":
                if "feedurl" in params:
                    self.elenco_cult(
                        **self.sliceParams(params, ("feedurl", "page_action"))
                    )
                else:
                    self.elenco_cult_root()
            elif params["mode"] == "magazine":
                if "newsFeedUrl" in params:
                    self.elenco_magazine(
                        **self.sliceParams(params, ("newsFeedUrl", "page_action"))
                    )
                elif "ddg_url" in params:
                    self.elenco_news(params["ddg_url"])
            elif params["mode"] == "programma":
                if _safeGet(params, "series_id") or _safeGet(params, "series_guid"):
                    self.elenco_stagioni_list(
                        **self.sliceParams(
                            params,
                            ("series_id", "series_guid", "title", "sort", "order"),
                        )
                    )
                elif "sub_brand_id" in params:
                    self.elenco_video_list(
                        **self.sliceParams(
                            params, ("sub_brand_id", "mode", "sort", "page", "size")
                        )
                    )
                elif "brand_id" in params:
                    self.elenco_sezioni_list(params["brand_id"])
            if params["mode"] == "video":
                if "pid" in params:
                    self.riproduci_video(
                        **self.sliceParams(params, ("guid", "pid", "offset"))
                    )
                else:
                    self.riproduci_guid(**self.sliceParams(params, ("guid", "offset")))
            elif params["mode"] == "live":
                if "tuning" in params and params["tuning"] == "split":
                    self.canali_live_play(params["guid"])
                else:
                    self.riproduci_video(
                        live=True,
                        **self.sliceParams(
                            params, ("guid", "pid", "publicUrl", "tuning")
                        ),
                    )
            elif params["mode"] == "tv":
                self.tv_root()
            # elif params["mode"] == "personal":
            #     self.personal_root()
            elif params["mode"] == "continuewatch":
                self.continuewatch()
            elif params["mode"] == "auth":
                self.auth()
            elif params["mode"] == "account":
                self.account()
            elif params["mode"] == "profile":
                idPersona = params["idPersona"] if "idPersona" in params else None
                self.profile(idPersona)
            elif params["mode"] == "logout":
                self.logout()
            elif params["mode"] == "favorites":
                self.favorites()
            elif params["mode"] == "watchlist":
                self.watchlist()
            elif params["mode"] == "contextmenu":
                self.contextMenu(
                    **self.sliceParams(
                        params,
                        ("context_menu", "context_action", "context_id", "context_ui"),
                    )
                )
            elif params["mode"] == "canali_live":
                self.canali_live_root()
            elif params["mode"] == "guida_tv":
                if "id" in params:
                    if "week" in params:
                        self.guida_tv_canale_settimana(
                            params["id"], int(params["week"])
                        )
                    elif "day" in params:
                        self.guida_tv_canale_giorno(params["id"], int(params["day"]))
                self.guida_tv_root()
        else:
            self.root()
