# Description: Tools for reproducible research.
# Author:      André Palóczy
# E-mail:      paloczy@gmail.com

import pickle
import os
from os import system
import sys
import inspect
from pkgutil import get_importer
from subprocess import check_output
from numpy import load as load_np
from numpy import savez as savez_np
from matplotlib.pyplot import gcf
from matplotlib.pyplot import savefig as savefig_mpl
from datetime import datetime
from git import InvalidGitRepositoryError
from git.repo import Repo

from . import __cfgfile__, __cfgstr__

__all__ = ['repohash',
           'stamp',
           'stamp_fig',
           'savefig',
           'read_fig_metadata',
           'savez']


def repohash(repo_path=None, search_parent_directories=False, return_gitobj=False):
    """Convenience function that returns the current hash of a repo."""
    if not repo_path:                    # If repo path is not provided, assume
        search_parent_directories = True # working dir is a subdir of the repo.
    try:
        repo = Repo(path=repo_path, search_parent_directories=search_parent_directories)
    except InvalidGitRepositoryError:
        print("Warning: Git repository not found. No git info added to this stamp.")
        return None

    if return_gitobj:
        return repo
    else:
        return repo.head.commit.hexsha


def stamp(repo_path=None, search_parent_directories=False):
    """Return dictionary with current git repo hash and other metadata."""
    repo = repohash(repo_path=repo_path,
                    search_parent_directories=search_parent_directories,
                    return_gitobj=True)

    if not repo:
        rhash = None
        gitpath = None
        auth = None
        authdt = None
    else:
        rhash = repo.head.commit.hexsha
        gitpath = repo.git_dir
        auth = repo.commit().author.name
        authdt = repo.commit().authored_datetime.strftime("%b %d %Y %H:%M:%S %z").strip()

    # Search the list of all scopes above the caller's frame.
    dirname = get_importer(os.getcwd()).path
    pnames = inspect.stack() # List with the paths of all the scopes loaded.
    script_path = None
    for pname in pnames:
        pnamef = pname.filename
        if dirname in pnamef:    # 'dirname' is the directory where the calling
            script_path = pnamef # script lives. So the path of the scope we are
                                 # looking for has to have 'dirname' in it.

    python_version = sys.version
    user = os.environ['USER']
    uname = check_output(['uname', '-a']).decode('UTF-8')
    now = datetime.now().strftime("%b %d %Y %H:%M:%S %z").strip()
    d = dict(created_by_script=script_path, time_file_was_created=now,
             file_was_created_by_user=user, git_repo_path=gitpath,
             git_repo_author=auth, time_git_repo_commit=authdt,
             git_repo_hash=rhash, uname_output=uname,
             python_version=python_version)

    return d


def stamp_fig(figpath, repo_path=None, search_parent_directories=False, wipe=True):
    """Adds a git hash to the metadata of a figure."""
    if wipe: # Remove all deletable tags before writing stamp.
        system("exiftool -all= %s -q"%figpath)

    s = stamp(repo_path=repo_path, search_parent_directories=search_parent_directories)
    # 1) Edit .cfg file.
    # 2) execute exiftool to write tags to image.
    # 3) Reset .cfg file.
    for tag, val in s.items():
        sedcmd1 = "sed -i \'/%s/c\\%s => { },\' %s"%(__cfgstr__, tag, __cfgfile__)
        exfcmd = "exiftool -config %s -q -xmp-dc:%s=\"%s\" %s"%(__cfgfile__, tag, val, figpath)
        sedcmd2 = "sed -i '/%s/c\%s' %s"%(tag, __cfgstr__, __cfgfile__)
        cleancmd = "rm -f %s_original"%figpath
        _batch_exec([sedcmd1, exfcmd, sedcmd2, cleancmd])


def savefig(figname, repo_path=None, search_parent_directories=False, \
            auto_commit=True, fmt='png', pickle_fig=False, **kw):
    """
    A wrapper for matplotlib.pyplot.savefig() that adds the current
    git hash (of the repo that created the figure) to the figure metadata, after
    saving it. Keyword arguments are passed to stamp_fig and
    matplotlib.pyplot.savefig.

    If kw 'pickle_fig' is set to True, also pickle the figure handle (for easier
    interactive viewing later).
    """
    savefig_mpl(figname, fmt=fmt, **kw) # Save figure first.
    # Append git hash and other metadata to figure file.
    stamp_fig(figname, repo_path=repo_path, \
              search_parent_directories=search_parent_directories)
    if pickle_fig:
        pklname = figname.replace(fmt, 'pkl')
        pickle.dump(gcf(), open(pklname, 'wb'))


def read_fig_metadata(figpath, stamp_tags_only=True):
    """Extract the text in the metadata fields of an image file."""
    tab = check_output(['exiftool', figpath]).decode().splitlines()
    k = [l.split(':')[0].strip() for l in tab]
    v = [l.split(':')[1].strip() for l in tab]
    d = {}
    for kn, vn in zip(k, v):
        d.update({kn.casefold().replace(' ', '_'):vn})

    if stamp_tags_only: # Retrieve only the metadata fields assigned by stamp().
        stamp_tags = stamp().keys()
        krms = list(set(d).symmetric_difference(set(stamp_tags)))
        for krm in krms:
            _ = d.pop(krm)

    return d


def savez(npzfname, stamp_name='__reproducibility_stamp__', \
          repo_path=None, search_parent_directories=False, **dvars):
    """
    A wrapper for numpy.savez() that adds the current git hash (of the repo
    that created the figure) to the .npz file, after saving it. Keyword
    arguments are passed to numpy.savez().
    """
    s = stamp(repo_path=repo_path, \
              search_parent_directories=search_parent_directories)
    dvars.update({stamp_name:s})
    savez_np(npzfname, **dvars)


def _guess_fmt(figpath):
    return check_output(['file', figpath]).decode('UTF-8')


def _batch_exec(cmds):
    _ = [system(cmd) for cmd in cmds]
