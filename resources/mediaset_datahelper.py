from datetime import datetime, date
from kodi_six import utils  # pyright: ignore[reportMissingImports]
from functools import reduce
import json
# from phate89lib import kodiutils  # pyright: ignore[reportMissingImports]
# from pprint import pformat


def __reduceTags(x, y):
    if "scheme" in y and y["scheme"]:
        if y["scheme"] in x:
            x[y["scheme"]].append(y["title"])
        else:
            x[y["scheme"]] = [y["title"]]
    return x


def __normalize(value):
    if isinstance(value, dict):
        return dict(map(lambda x: (x[0], __normalize(x[1])), value.items()))
    elif isinstance(value, list):
        return list(map(lambda x: utils.py2_encode(x), value))
    else:
        return utils.py2_encode(value)


def _gather_media_type(prog):
    programType = None
    if "programType" in prog:
        programType = prog["programType"]
    elif "programtype" in prog:
        programType = prog["programtype"]
    if programType:
        if programType == "movie":
            return "movie"
        if programType == "TVSeason":
            return "tvshow"
        if programType == "episode":
            return "episode"
        if programType == "extra":
            return "episode"
    if (
        "mediasetprogram$brandVerticalSiteCMS" in prog
        and prog["mediasetprogram$brandVerticalSiteCMS"] == "fiction"
    ):
        return "tvshow"
    if (
        "tvSeasonNumber" in prog
        and "tvSeasonEpisodeNumber" in prog
        and prog["tvSeasonNumber"]
        and prog["tvSeasonEpisodeNumber"]
    ):
        return "episode"
    if "seriesId" in prog and "mediasetprogram$subBrandId" not in prog:
        return "tvshow"
    if "mediasetprogram$subBrandDescription" in prog and (
        prog["mediasetprogram$subBrandDescription"].lower() == "film"
        or prog["mediasetprogram$subBrandDescription"].lower() == "documentario"
    ):
        return "movie"
    if "_blockId" in prog:
        return ""
    return "video"


def _gather_info(prog, titlewd=False, mediatype=None, infos=None, lookup_fullplot=True):
    if infos is None:
        infos = {}

    tags = reduce(__reduceTags, prog["tags"], {}) if "tags" in prog else {}
    if "genre" not in infos:
        infos["genre"] = []
    if "mediasetprogram$genres" in prog:
        infos["genre"].extend(prog["mediasetprogram$genres"])
    if "mediasettvseason$genres" in prog:
        infos["genre"].extend(prog["mediasettvseason$genres"])
    if "genre" in tags and tags["genre"]:
        infos["genre"].extend(tags["genre"])

    channelCategory = ""
    if (
        "mediasetprogram$channelCategory" in prog
        and prog["mediasetprogram$channelCategory"]
    ):
        channelCategory = prog["mediasetprogram$channelCategory"][0]
    elif (
        "mediasettvseason$channelCategory" in prog
        and prog["mediasettvseason$channelCategory"]
    ):
        channelCategory = prog["mediasettvseason$channelCategory"][0]
    elif "channelCategory" in tags and tags["channelCategory"]:
        channelCategory = tags["channelCategory"][0]

    if "mediatype" not in infos:
        if mediatype:
            infos["mediatype"] = mediatype
        else:
            infos["mediatype"] = _gather_media_type(prog)

    if "title" not in infos:
        if (
            "mediasetprogram$subBrandId" in prog
            and "description" in prog
            and prog["description"]
            and "media" not in prog
        ):
            infos["title"] = prog["description"]
        elif "title" in prog:
            infos["title"] = prog["title"]
        elif "mediasetprogram$brandTitle" in prog:
            infos["title"] = prog["mediasetprogram$brandTitle"]
        if (
            titlewd
            and "mediasetprogram$brandTitle" in prog
            and prog["mediasetprogram$brandTitle"] != ""
        ):
            infos["title"] = "{} - {}".format(
                prog["mediasetprogram$brandTitle"], infos["title"]
            )

    if "credits" in prog:
        if "cast" not in infos:
            infos["cast"] = []
        if "director" not in infos:
            infos["director"] = []
        for person in prog["credits"]:
            if person["creditType"] == "actor":
                infos["cast"].append(person["personName"])
            elif person["creditType"] == "director":
                infos["director"].append(person["personName"])

    if not ("plot" in infos or "plotoutline" in infos):
        plot = ""
        plotoutline = ""
        # try to find plotoutline
        if "shortDescription" in prog and prog["shortDescription"]:
            plotoutline = prog["shortDescription"]
        elif (
            "mediasettvseason$shortDescription" in prog
            and channelCategory != "MediasetPlay_Programmi Tv"
        ):
            plotoutline = prog["mediasettvseason$shortDescription"]
        elif "description" in prog and prog["description"]:
            plotoutline = prog["description"]
        elif "mediasettvseason$brandDescription" in prog:
            plotoutline = prog["mediasettvseason$brandDescription"]
        elif "mediasetprogram$brandDescription" in prog:
            plotoutline = prog["mediasetprogram$brandDescription"]
        elif "mediasetprogram$subBrandDescription" in prog:
            plotoutline = prog["mediasetprogram$subBrandDescription"]
        elif "descriptionSeo" in prog:
            plotoutline = prog["descriptionSeo"]

        # try to find plot
        if lookup_fullplot:
            if (
                "longDescription" in prog
                and prog["longDescription"]
                and channelCategory != "MediasetPlay_Programmi Tv"
            ):  # longDescription sometimes has -
                plot = prog["longDescription"]
            elif "description" in prog and prog["description"]:
                plot = prog["description"]
            elif "mediasettvseason$brandDescription" in prog:
                plot = prog["mediasettvseason$brandDescription"]
            elif "mediasetprogram$brandDescription" in prog:
                plot = prog["mediasetprogram$brandDescription"]
            elif "mediasetprogram$subBrandDescription" in prog:
                plot = prog["mediasetprogram$subBrandDescription"]

        # fill the other if one is empty
        if plot == "":
            plot = plotoutline
        if plotoutline == "":
            plotoutline = plot
        infos["plot"] = plot
        infos["plotoutline"] = plotoutline

    lastPublished = 0
    if "mediasetprogram$publishInfo_lastPublished" in prog:
        try:
            lastPublished = (
                int(prog["mediasetprogram$publishInfo_lastPublished"]) / 1000
            )
        except Exception:
            pass
    if "aired" not in infos and lastPublished:
        try:
            infos["aired"] = str(date.fromtimestamp(lastPublished))
        except Exception:
            pass
    if "dateadded" not in infos and lastPublished:
        try:
            infos["dateadded"] = str(datetime.fromtimestamp(lastPublished))
        except Exception:
            pass

    if "duration" not in infos and "mediasetprogram$duration" in prog:
        infos["duration"] = prog["mediasetprogram$duration"]
    if "year" not in infos and "year" in prog:
        infos["year"] = prog["year"]
    if "season" not in infos and "tvSeasonNumber" in prog and prog["tvSeasonNumber"]:
        infos["season"] = prog["tvSeasonNumber"]
    if "episode" not in infos:
        if "tvSeasonEpisodeNumber" in prog and prog["tvSeasonEpisodeNumber"]:
            infos["episode"] = prog["tvSeasonEpisodeNumber"]
        elif "season" in infos:
            del infos["season"]
    if "season" in infos and "episode" in infos:
        infos["tvshowtitle"] = prog["mediasetprogram$brandTitle"]

    if "program" in prog:
        return _gather_info(prog["program"], titlewd=titlewd, infos=infos)

    return dict(__normalize(infos))


def _gather_art(prog):
    arts = {}
    # kodiutils.log(("_gather_art prog: {}").format(pformat(prog)), 4)
    if "thumbnails" in prog:
        mediaType = _gather_media_type(prog)

        # Thumb
        if "image_vertical-264x396" in prog["thumbnails"]:
            arts["poster"] = prog["thumbnails"]["image_vertical-264x396"]["url"]
            arts["thumb"] = arts["poster"]
        elif "channel_logo-100x100" in prog["thumbnails"]:
            arts["poster"] = prog["thumbnails"]["channel_logo-100x100"]["url"]
            arts["thumb"] = arts["poster"]

        # Banner
        if "brand_cover-1440x513" in prog["thumbnails"]:
            arts["banner"] = prog["thumbnails"]["brand_cover-1440x513"]["url"]
        elif "image_header_poster-1440x630" in prog["thumbnails"]:
            arts["banner"] = prog["thumbnails"]["image_header_poster-1440x630"]["url"]
        elif "image_header_poster-1440x433" in prog["thumbnails"]:
            arts["banner"] = prog["thumbnails"]["image_header_poster-1440x433"]["url"]

        # Landscape
        if "image_header_poster-1440x630" in prog["thumbnails"]:
            arts["landscape"] = prog["thumbnails"]["image_header_poster-1440x630"][
                "url"
            ]
        elif "image_header_poster-1440x433" in prog["thumbnails"]:
            arts["landscape"] = prog["thumbnails"]["image_header_poster-1440x433"][
                "url"
            ]

        # Icon
        if "brand_logo-210x210" in prog["thumbnails"]:
            arts["icon"] = prog["thumbnails"]["brand_logo-210x210"]["url"]

        # Fanart
        if "image_horizontal_cover-704x396" in prog["thumbnails"]:
            arts["fanart"] = prog["thumbnails"]["image_horizontal_cover-704x396"]["url"]
        elif "image_header_poster-1440x630" in prog["thumbnails"]:
            arts["fanart"] = prog["thumbnails"]["image_header_poster-1440x630"]["url"]
        elif "image_header_poster-768x384" in prog["thumbnails"]:
            arts["fanart"] = prog["thumbnails"]["image_header_poster-768x384"]["url"]

        # Cleart
        if "image_keyframe_poster-1200x630" in prog["thumbnails"]:
            arts["clearart"] = prog["thumbnails"]["image_keyframe_poster-1200x630"][
                "url"
            ]

        if mediaType:
            icon = None
            if mediaType == "episode":
                icon = __findImg(
                    prog["thumbnails"],
                    [
                        "image_keyframe_poster-240x135",
                        "image_keyframe_poster-265x148",
                        "image_keyframe_poster-292x165",
                        "image_keyframe_poster-360x203",
                        "image_keyframe_poster-391x220",
                        "image_keyframe_poster-652x367",
                        "image_keyframe_poster-1200x630",
                        "image_keyframe_poster-1280x720",
                    ],
                )
            if icon:
                arts["thumb"] = icon
                arts["poster"] = icon

    elif "program" in prog:
        return _gather_art(prog["program"])

    elif (
        "type" in prog and prog["type"] == "Entry"
        # and "contentType" in prog
        # and prog["contentType"] in ["page", "article", "listMixedContent"]
    ):
        imageUrl = _safeGet(prog, "imageUrl")
        posterImageUrl = _safeGet(prog, "posterImageUrl")
        keyframeImageUrl = _safeGet(prog, "keyframeImageUrl")
        poster = (
            (
                __findImgMax(json.loads(prog["posterImage"]))
                if "posterImage" in prog and prog["posterImage"]
                else ""
            )
            or imageUrl
            or posterImageUrl
        )
        keyframe = (
            (
                __findImgMax(json.loads(prog["keyframeImage"]))
                if "keyframeImage" in prog and prog["keyframeImage"]
                else ""
            )
            or imageUrl
            or keyframeImageUrl
        )
        if poster:
            arts["thumb"] = poster
            arts["poster"] = poster
            arts["icon"] = poster
        if keyframe:
            arts["fanart"] = keyframe
            arts["clearart"] = keyframe
            arts["banner"] = keyframe

    return dict(__normalize(arts))


def __findImg(images, names):
    for name in names:
        if name in images and "url" in images[name]:
            return images[name]["url"]
    return None


def __findImgMax(el):
    data = el["data"] if "data" in el else {}
    if "i" in data and "p" in data:
        baseUrl = data["p"] or ""
        images = sorted((data["i"] or {}).items())
        if images and images[-1]:
            return "{}{}".format(baseUrl, images[-1][-1])
    return ""


def _findGuid(el, videos):
    if el and videos:
        # kodiutils.log("_findGuid el={}".format(pformat(el)))
        # kodiutils.log(
        #     "_findGuid fields.text.content={}".format(pformat(_safeGet(el, "fields.text.content")))
        # )
        return next(
            (
                _safeGet(_safeGet(videos, _safeGet(x, "data.target.sys.id")), "guid")
                for x in _safeGet(el, "fields.text.content")
                if _safeGet(x, "nodeType") == "embedded-entry-block"
                and _safeGet(x, "data.target.sys.type") == "Link"
                and _safeGet(x, "data.target.sys.linkType") == "Entry"
                and _safeGet(videos, _safeGet(x, "data.target.sys.id"))
            ),
            "",
        )
    return ""
    # if "text" in el and el["text"] and "content" in el["text"]["content"] and videos:
    #     for node in el["text"]["content"]:
    #         if (
    #             "nodeType" in node
    #             and node["nodeType"]
    #             and node["nodeType"] == "embedded-entry-block"
    #             and "data" in node
    #             and node["data"]
    #             and "target" in node["data"]
    #             and node["data"]["target"]
    #             and "sys" in node["data"]["target"]
    #             and node["data"]["target"]["sys"]
    #             and "id" in node["data"]["target"]["sys"]
    #             and node["data"]["target"]["sys"]["id"]
    #             and "type" in node["data"]["target"]["sys"]
    #             and node["data"]["target"]["sys"]["type"] == "Link"
    #             and "linkType" in node["data"]["target"]["sys"]
    #             and node["data"]["target"]["sys"]["linkType"] == "Entry"
    #         ):
    #             if (
    #                 node["data"]["target"]["sys"]["id"] in videos
    #                 and videos[node["data"]["target"]["sys"]]
    #             ):
    #                 return videos[node["data"]["target"]["sys"]]
    # return ""


def _normalizeUrl(uri):
    if uri:
        if uri.startswith("http"):
            return uri
        else:
            httpProtocol = "https:" if uri.startswith("//") else "https://"
            return "{}{}".format(httpProtocol, uri)
    return ""


def _findImage(el, assets):
    imageId = _safeGet(el, "fields.image.sys.id")
    # kodiutils.log("_findImage imageid={}".format(imageId))
    if imageId:
        image = _safeGet(assets, imageId)
        # kodiutils.log("_findImage image={}".format(str(image)))
        imageURI = _safeGet(image, "file.url")
        # kodiutils.log("_findImage imageURI={}".format(str(imageURI)))
        imageUrl = _normalizeUrl(imageURI)
        # kodiutils.log("_findImage imageUrl={}".format(str(imageUrl)))
        return imageUrl
    return ""


def _findEmbeddedVideos(el):
    if _safeGet(el, "includes.Entry"):
        return dict(
            map(
                _mapItemToEntry,
                [
                    x
                    for x in _safeGet(el, "includes.Entry")
                    if _safeGet(x, "sys.id")
                    and _safeGet(x, "sys.contentType.sys.id") == "videoembed"
                ],
            )
        )
    return {}


def _findEmbeddedAssets(el):
    if _safeGet(el, "includes.Asset"):
        return dict(
            map(
                _mapItemToEntry,
                [
                    x
                    for x in el["includes"]["Asset"]
                    if _safeGet(x, "sys.id") and _safeGet(x, "fields.file.url")
                ],
            )
        )
    return {}


def _mapItemToEntry(el):
    entry = _mapItem(el)
    return (entry["id"], entry)


def _safeGet(el, path, value=""):
    if el and path:
        for x in path.split("."):
            if el and x in el:
                el = el[x]
            else:
                return value
        return el or value
    return value


def _mapItem(el):
    return {
        **el["fields"],
        "id": _safeGet(el, "sys.id"),
        "type": _safeGet(el, "sys.type"),
        "contentType": _safeGet(el, "sys.contentType.sys.id"),
    }
