# Description: Tools for reproducible research.
# Author:      André Palóczy
# E-mail:      paloczy@gmail.com

import os
from os import system
from subprocess import check_output
from pkgutil import get_importer
from matplotlib.pyplot import savefig as savefig_mpl
from datetime import datetime
from git import InvalidGitRepositoryError
from git.repo import Repo

from . import __cfgfile__, __cfgstr__

__all__ = ['repohash',
           'stamp',
           'stamp_fig',
           'savefig',
           'read_fig_metadata']


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

    sname = get_importer(os.getcwd()).path
    user = os.environ['USER']
    uname = check_output(['uname', '-a']).decode('UTF-8')
    now = datetime.now().strftime("%b %d %Y %H:%M:%S %z").strip()
    d = dict(parent_script_dir=sname, time_file_was_created=now,
             file_was_created_by_user=user, git_repo_path=gitpath,
             git_repo_author=auth, time_git_repo_commit=authdt,
             git_repo_hash=rhash, uname_output=uname)

    return d


def stamp_fig(figpath, repo_path=None, search_parent_directories=False, wipe=True):
    """Adds a git hash to the metadata of a figure."""
    if wipe: # Remove all deletable tags before writing stamp.
        system("exiftool -all= %s"%figpath)

    s = stamp(repo_path=repo_path, search_parent_directories=search_parent_directories)
    # 1) Edit .cfg file.
    # 2) execute exiftool to write tags to image.
    # 3) Reset .cfg file.
    for tag, val in s.items():
        sedcmd1 = "sed -i \'/%s/c\\%s => { },\' %s"%(__cfgstr__, tag, __cfgfile__)
        exfcmd = "exiftool -config %s -xmp-dc:%s=\"%s\" %s"%(__cfgfile__, tag, val, figpath)
        sedcmd2 = "sed -i '/%s/c\%s' %s"%(tag, __cfgstr__, __cfgfile__)
        _batch_exec([sedcmd1, exfcmd, sedcmd2])


def savefig(figname, repo_path=None, search_parent_directories=False, fmt='png', **kw):
    """
    A Wrapper for matplotlib.pyplot.savefig() that adds a the current
    git hash (of the repo that created the figure) to the figure metadata, after
    saving it. Keyword arguments are passed to stamp_fig and matplotlib.pyplot.savefig.
    """
    savefig_mpl(figname, fmt=fmt, **kw) # Save figure first.
    # Append git hash and other metadata to figure file.
    stamp_fig(figname, repo_path=repo_path, \
              search_parent_directories=search_parent_directories)


def read_fig_metadata(figpath, wipe=True):
    """Extract the text in the metadata fields of an image file."""
    tab = check_output(['exiftool', figpath]).decode().splitlines()
    k = [l.split(':')[0].strip() for l in tab]
    v = [l.split(':')[1].strip() for l in tab]
    d = {}
    for kn, vn in zip(k, v):
        d.update({kn.casefold().replace(' ', '_'):vn})

    if wipe: # Retrieve only the metadata fields assigned by stamp().
        stamp_tags = stamp().keys()
        krms = list(set(d).symmetric_difference(set(stamp_tags)))
        for krm in krms:
            d.pop(krm)

    return d


def _guess_fmt(figpath):
    return check_output(['file', figpath]).decode('UTF-8')


def _batch_exec(cmds):
    _ = [system(cmd) for cmd in cmds]
