__version__ = '0.1'

__cfgfile__ = __path__[0] + '/mknewtag.cfg'
__cfgstr__ = 'NEWTAG => { },'

__all__ = ['repohash',
           'stamp',
           'stamp_fig',
           'savefig']

from .base import (repohash,
                   stamp,
                   stamp_fig,
                   savefig)
