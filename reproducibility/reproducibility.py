# Description: Tools for reproducibility.
# Author:      André Palóczy
# E-mail:      paloczy@gmail.com

from matplotlib.pyplot import savefig as savefig_mpl
from datetime import datetime
import os
import subprocess
from git.repo import Repo
from PIL import Image
from PIL import PngImagePlugin, JpegImagePlugin, EpsImagePlugin
from PIL import TiffImagePlugin, PdfImagePlugin

__all__ = ['repohash',
           'stamp',
           'add_repohashfig',
           'savefig']


def repohash(repo_path=None, search_parent_directories=False, return_gitobj=False):
    """Convenience function that returns the current hash of a repo."""
    if repo_path is None:                # If repo path is not provided, assume
        search_parent_directories = True # working dir is a subdir of the repo.
    repo = Repo(path=repo_path, search_parent_directories=search_parent_directories)

    if return_gitobj:
        return repo
    else:
        return repo.head.commit.hexsha


def stamp(repo_path=None, search_parent_directories=False):
    """Return dictionary with current git repo hash and other metadata."""
    repo = repohash(repo_path=repo_path,
                    search_parent_directories=search_parent_directories,
                    return_gitobj=True)
    rhash = repo.head.commit.hexsha
    gitpath = repo.git_dir
    auth = repo.commit().author.name
    authdt = repo.commit().authored_datetime.strftime("%b %d %Y %H:%M:%S %z").strip()
    sname = __file__
    user = os.environ['USER']
    f = subprocess.Popen(['uname', '-a'], stdout=subprocess.PIPE, shell=False)
    uname = str(f.stdout.read()).replace('\\n\'', '').replace('b\'', '')
    now = datetime.now().strftime("%b %d %Y %H:%M:%S %z").strip()
    d = dict(parent_script_path=sname, time_file_was_created=now,
             file_was_created_by_user=user, git_repo_path=gitpath,
             git_repo_author=auth, time_git_repo_commit=authdt,
             git_repo_hash=rhash, uname_output=uname)

    return d


def add_repohashfig(figpath, repohash, repo_path, fmt=None):
    """Adds a git hash to the metadata of a figure."""
    plugin = _get_figmetadata(figpath, fmt=fmt) # Get right plugin for the figure.
    img = Image.open(figpath)
    metadata = _get_figmetadata(figpath, fmt=fmt)
    metadata.add_text('Git repo path', repo_path)
    metadata.add_text('Git repo hash', repohash)
    img.save(img, 'png', pnginfo=metadata) # Overwrite figure with repo info.


def savefig(figname, parent_repo_path, **kw):
    """
    A Wrapper for matplotlib.pyplot.savefig() that adds a the current
    git hash (of the repo that created the figure) to the figure metadata, after
    saving it. All keyword arguments are passed to matplotlib.pyplot.savefig.
    """
    savefig_mpl(figname, **kw)                           # Save figure.
    repohash = repohash(repo_path=parent_repo_path)  # Read the current repo hash.
    add_repohashfig(figname, repohash, parent_repo_path) # Append repo name and hash to figure.


def _get_figmetadata(figpath, fmt=None):
    if fmt is None: # Attept to guess the figure format.
        f = subprocess.Popen(['file', figpath], stdout=subprocess.PIPE)
        fmt = str(f.stdout.read())
    if 'PNG image data' in fmt:
        metadata = PngImagePlugin.PngInfo()
    elif 'JPG image data' in ftm or 'JPEG image data' in fmt:
        raise NotImplementedError("JPG figure not implemented yet, sorry...")
    elif 'PDF document' in ftype:
        raise NotImplementedError("PDF figure not implemented yet, sorry...")
    elif 'type EPS' in ftype:
        raise NotImplementedError("EPS figure not implemented yet, sorry...")
    elif 'TIFF image data' in fmt:
        raise NotImplementedError("TIFF figure not implemented yet, sorry...")
    else:
        raise TypeError('No plugin available for image format "%s".'%ftype)

    return metadata
