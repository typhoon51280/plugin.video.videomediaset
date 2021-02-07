# -*- coding: utf-8 -*-

from resources.lib.monitor import MediasetService
from phate89lib import kodiutils  # pyright: reportMissingImports=false

scrobbling = kodiutils.getSettingAsNum("scrobbling")

if scrobbling:
    kodiutils.log('Addon {} starting {} scrobbling service (version {})'.format(kodiutils.ID, kodiutils.NAME, kodiutils.VERSION))
    try:
        MediasetService().run()
    except Exception as exc:
        kodiutils.log('[mediasetservice] Exception: {}'.format(str(exc)))

    kodiutils.log('Addon {} shutting down {} scrobbling service (version {})'.format(kodiutils.ID, kodiutils.NAME, kodiutils.VERSION))
