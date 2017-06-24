# Description: Tools for reproducibility.
# Author:      André Palóczy
# E-mail:      paloczy@gmail.com

import numpy as np
from matplotlib.pyplot import savefig as savefig_mpl
from git.repo import Repo

__all__ = ['gethash',
           'savefig',
           'addhash_fig']

def get_current_repohash(search_parent_directories=False):
    if repo_path is None:
        search_parent_directories = True
    else:
        pass
    watedRepo = Repo(path=repo_path, search_parent_directories=search_parent_directories)
    return Repo.head.object.sha

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
