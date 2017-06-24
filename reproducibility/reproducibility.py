# Description: Tools for reproducibility.
# Author:      André Palóczy
# E-mail:      paloczy@gmail.com

import numpy as np
from matplotlib.pyplot import savefig as savefig_mpl
from git.repo import Repo

__all__ = ['get_repohash',
           'savefig',
           'add_repohashfig']

def get_repohash(repo_path, search_parent_directories=False):
    if repo_path is None:
        search_parent_directories = True
    else:
        pass
    watedRepo = Repo(path=repo_path, search_parent_directories=search_parent_directories)
    return wantedRepo.head.object.sha

def savefig(figname, **kw):
    """
    A Wrapper for matplotlib.pyplot.savefig() that adds a the current
    git hash (of the repo that created the figure) to the figure metadata, after
    saving it. All keyword arguments are passed to matplotlib.pyplot.savefig.
    """
    savefig_mpl(figname, **kw)    # Save figure.
    Hash = get_repohash() # Read the current repo hash.

def add_repohashfig():
    return None
