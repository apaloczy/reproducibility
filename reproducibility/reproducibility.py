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


def repohash(repo_path=None, search_parent_directories=False):
    """Convenience function that returns the current hash of a repo."""
    if repo_path is None:                # If repo path is not provided, assume
        search_parent_directories = True # working dir is a subdir of the repo.
    else:
        pass
    repo = Repo(path=repo_path, search_parent_directories=search_parent_directories)

    return repo.head.commit.hexsha


def stamp(repo_path=None, search_parent_directories=False):
    """Return name of script, current time and git repo hash."""
    sname = __file__
    user = os.environ['USER']
    now = datetime.now().strftime("%b %d %Y %H:%M:%S")
    rhash = repohash(repo_path=repo_path, search_parent_directories=search_parent_directories)

    return dict(script_path=sname, time_created=now, user=user, git_repo_hash=rhash)


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
