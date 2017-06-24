# Description: Tools for helping reproducibility.
# Author:      André Palóczy
# E-mail:      paloczy@gmail.com

import numpy as np
from matplotlib.pyplot import savefig as savefig_mpl

__all__ = ['gethash',
           'savefig',
           'addhash_fig']

def gethash():
    return None

def savefig(figname, **kw):
    """
    A Wrapper for matplotlib.pyplot.savefig
    that adds a git hash to the figure metadata
    after saving it. All keyword arguments are
    passed to matplotlib.pyplot.savefig.
    """
    savefig_mpl(figname, **kw) # Save figure
    Hash = gethash()           # Read the current hash from the .git folder.

def addhash_fig():
    return None
