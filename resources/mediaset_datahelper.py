from datetime import datetime, date
from kodi_six import utils
try:
    from functools import reduce
except:
    pass

def __reduceTags(x, y):
    if y['scheme'] in x:
        x[y['scheme']].append(y['title'])
    else:
        x[y['scheme']] = [y['title']]
    return x

def __normalize(value):
    if isinstance(value, dict):
        return dict(map(lambda x: (x[0], __normalize(x[1])), value.items()))
    elif isinstance(value, list):
        return map(lambda x: utils.py2_encode(x), value)
    else:
        return utils.py2_encode(value)

def _gather_media_type(prog):
    if 'programType' in prog:
        if prog['programType'] == 'movie':
            return 'movie'
        if prog['programType'] == 'episode':
            return 'episode'
    if ('mediasetprogram$brandVerticalSiteCMS' in prog and
            prog['mediasetprogram$brandVerticalSiteCMS'] == 'fiction'):
        return 'tvshow'
    if 'tvSeasonNumber' in prog or 'tvSeasonEpisodeNumber' in prog:
        return 'episode'
    if 'seriesId' in prog and 'mediasetprogram$subBrandId' not in prog:
        return 'tvshow'
    if ('mediasetprogram$subBrandDescription' in prog and
            (prog['mediasetprogram$subBrandDescription'].lower() == 'film' or
             prog['mediasetprogram$subBrandDescription'].lower() == 'documentario')):
        return 'movie'
    return 'video'

def _gather_info(prog, titlewd=False, mediatype=None, infos=None, lookup_fullplot=True):
    if infos is None:
        infos = {}

    tags = reduce(__reduceTags , prog['tags'],  {}) if 'tags' in prog else {}
    if 'genre' not in infos:
        infos['genre'] = []
    if 'mediasetprogram$genres' in prog:
        infos['genre'].extend(prog['mediasetprogram$genres'])
    if 'mediasettvseason$genres' in prog:
        infos['genre'].extend(prog['mediasettvseason$genres'])
    if 'genre' in tags and tags['genre']:
        infos['genre'].extend(tags['genre'])

    channelCategory = ''
    if 'mediasetprogram$channelCategory' in prog and prog['mediasetprogram$channelCategory']:
        channelCategory = prog['mediasetprogram$channelCategory'][0]
    elif 'mediasettvseason$channelCategory' in prog and prog['mediasettvseason$channelCategory']:
        channelCategory = prog['mediasettvseason$channelCategory'][0]
    elif 'channelCategory' in tags and tags['channelCategory']:
        channelCategory = tags['channelCategory'][0]

    if 'mediatype' not in infos:
        if mediatype:
            infos['mediatype'] = mediatype
        else:
            infos['mediatype'] = _gather_media_type(prog)

    if 'title' not in infos:
        if 'title' in prog:
            infos['title'] = prog["title"]
        elif 'mediasetprogram$brandTitle' in prog:
            infos['title'] = prog["mediasetprogram$brandTitle"]
        if (titlewd and 'mediasetprogram$brandTitle' in prog and prog['mediasetprogram$brandTitle'] != ''):
            infos['title'] = '{} - {}'.format(prog['mediasetprogram$brandTitle'], infos['title'])

    if 'credits' in prog:
        if 'cast' not in infos:
            infos['cast'] = []
        if 'director' not in infos:
            infos['director'] = []
        for person in prog['credits']:
            if person['creditType'] == 'actor':
                infos['cast'].append(person['personName'])
            elif person['creditType'] == 'director':
                infos['director'].append(person['personName'])

    if not ('plot' in infos or 'plotoutline' in infos):
        plot = ""
        plotoutline = ""
        # try to find plotoutline
        if 'shortDescription' in prog and prog['shortDescription']:
            plotoutline = prog["shortDescription"]
        elif 'mediasettvseason$shortDescription' in prog and channelCategory != 'MediasetPlay_Programmi Tv':
            plotoutline = prog["mediasettvseason$shortDescription"]
        elif 'description' in prog and prog['description']:
            plotoutline = prog["description"]
        elif 'mediasettvseason$brandDescription' in prog:
            plotoutline = prog["mediasettvseason$brandDescription"]
        elif 'mediasetprogram$brandDescription' in prog:
            plotoutline = prog["mediasetprogram$brandDescription"]
        elif 'mediasetprogram$subBrandDescription' in prog:
            plotoutline = prog["mediasetprogram$subBrandDescription"]

        # try to find plot
        if lookup_fullplot:
            if 'longDescription' in prog and prog['longDescription'] and channelCategory != 'MediasetPlay_Programmi Tv': # longDescription sometimes has -
                plot = prog["longDescription"]
            elif 'description' in prog and prog['description']:
                plot = prog["description"]
            elif 'mediasettvseason$brandDescription' in prog:
                plot = prog["mediasettvseason$brandDescription"]
            elif 'mediasetprogram$brandDescription' in prog:
                plot = prog["mediasetprogram$brandDescription"]
            elif 'mediasetprogram$subBrandDescription' in prog:
                plot = prog["mediasetprogram$subBrandDescription"]

        # fill the other if one is empty
        if plot == "":
            plot = plotoutline
        if plotoutline == "":
            plotoutline = plot
        infos['plot'] = plot
        infos['plotoutline'] = plotoutline

    lastPublished = 0
    if 'mediasetprogram$publishInfo_lastPublished' in prog:
        try:
            lastPublished = int(prog['mediasetprogram$publishInfo_lastPublished'])/1000
        except:
            pass
    if 'aired' not in infos and lastPublished:
        try:
            infos['aired'] = str(date.fromtimestamp(lastPublished))
        except:
            pass
    if 'dateadded' not in infos and lastPublished:
        try:
            infos['dateadded'] = str(datetime.fromtimestamp(lastPublished))
        except:
            pass

    if 'duration' not in infos and 'mediasetprogram$duration' in prog:
        infos['duration'] = prog['mediasetprogram$duration']
    if 'year' not in infos and 'year' in prog:
        infos['year'] = prog['year']
    if 'season' not in infos and 'tvSeasonNumber' in prog and prog['tvSeasonNumber']:
        infos['season'] = prog['tvSeasonNumber']
    if 'episode' not in infos:
        if 'tvSeasonEpisodeNumber' in prog and prog['tvSeasonEpisodeNumber']:
            infos['episode'] = prog['tvSeasonEpisodeNumber']
        elif 'season' in infos:
            del infos['season']
    if ('season' in infos and 'episode' in infos):
        infos['tvshowtitle'] = prog['mediasetprogram$brandTitle']

    if 'program' in prog:
        return _gather_info(prog['program'], titlewd=titlewd, infos=infos)

    return __normalize(infos)


def _gather_art(prog):
    arts = {}
    if 'thumbnails' in prog:

        # Thumb
        if 'image_vertical-264x396' in prog['thumbnails']:
            arts['poster'] = prog['thumbnails']['image_vertical-264x396']['url']
            arts['thumb'] = arts['poster']
        elif 'channel_logo-100x100' in prog['thumbnails']:
            arts['poster'] = prog['thumbnails']['channel_logo-100x100']['url']
            arts['thumb'] = arts['poster']

        # Banner
        if 'brand_cover-1440x513' in prog['thumbnails']:
            arts['banner'] = prog['thumbnails']['brand_cover-1440x513']['url']
        elif 'image_header_poster-1440x630' in prog['thumbnails']:
            arts['banner'] = prog['thumbnails']['image_header_poster-1440x630']['url']
        elif 'image_header_poster-1440x433' in prog['thumbnails']:
            arts['banner'] = prog['thumbnails']['image_header_poster-1440x433']['url']

        # Landscape
        if 'image_header_poster-1440x630' in prog['thumbnails']:
            arts['landscape'] = prog['thumbnails']['image_header_poster-1440x630']['url']
        elif 'image_header_poster-1440x433' in prog['thumbnails']:
            arts['landscape'] = prog['thumbnails']['image_header_poster-1440x433']['url']

        # Icon
        if 'brand_logo-210x210' in prog['thumbnails']:
            arts['icon'] = prog['thumbnails']['brand_logo-210x210']['url']

        # Fanart
        if 'image_horizontal_cover-704x396' in prog['thumbnails']:
            arts['fanart'] = prog['thumbnails']['image_horizontal_cover-704x396']['url']
        elif 'image_header_poster-1440x630' in prog['thumbnails']:
            arts['fanart'] = prog['thumbnails']['image_header_poster-1440x630']['url']
        elif 'image_header_poster-768x384' in prog['thumbnails']:
            arts['fanart'] = prog['thumbnails']['image_header_poster-768x384']['url']

        # Cleart
        if 'image_keyframe_poster-1200x630' in prog['thumbnails']:
            arts['clearart'] = prog['thumbnails']['image_keyframe_poster-1200x630']['url']
        
        # if 'programType' in prog and (prog['programType'] == 'extra' or prog['programType'] == 'episode'):
        #     if 'image_keyframe_poster-652x367' in prog['thumbnails']:
        #         arts['poster'] = prog['thumbnails']['image_keyframe_poster-652x367']['url']
        #         arts['thumb'] = prog['thumbnails']['image_keyframe_poster-652x367']['url']

    elif 'program' in prog:
        return _gather_art(prog['program'])
    return __normalize(arts)
