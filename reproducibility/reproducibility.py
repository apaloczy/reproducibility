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
           'stamp_fig',
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


def stamp_fig(figpath, repo_path=None, search_parent_directories=False, fmt='guess'):
    """Adds a git hash to the metadata of a figure."""
    metadata, fmt = _get_plugin(figpath, fmt=fmt) # Get the right plugin for each format.
    img = Image.open(figpath)
    stp = stamp(repo_path=repo_path, search_parent_directories=search_parent_directories)
    for i in stp.items():
        metadata.add_text(i[0], i[1])
    fmt = fmt.lower()
    if 'png' in fmt:
        img.save(figpath, 'png', pnginfo=metadata) # Overwrite figure with repo info.
    else:
        raise NotImplementedError("Only PNG figure implemented so far, sorry...")


def savefig(figname, parent_repo_path, **kw):
    """
    A Wrapper for matplotlib.pyplot.savefig() that adds a the current
    git hash (of the repo that created the figure) to the figure metadata, after
    saving it. All keyword arguments are passed to matplotlib.pyplot.savefig.
    """
    savefig_mpl(figname, **kw) # Save figure first.
    stamp_fig(figname)         # Append git hash and other metadata to figure.


def _get_plugin(figpath, fmt='guess'):
    if fmt is 'guess': # Attept to guess the figure format.
        fmt = _guess_fmt(figpath)
    fmt = fmt.lower()
    if 'png' in fmt:
        plugin = PngImagePlugin.PngInfo()
    elif 'jpg' in fmt or 'jpeg' in fmt:
        raise NotImplementedError("JPG figure not implemented yet, sorry...")
    elif 'pdf' in fmt:
        raise NotImplementedError("PDF figure not implemented yet, sorry...")
    elif 'eps' in fmt:
        raise NotImplementedError("EPS figure not implemented yet, sorry...")
    elif 'tiff' in fmt:
        raise NotImplementedError("TIFF figure not implemented yet, sorry...")
    else:
        raise TypeError('No plugin available for image format "%s".'%fmt)

    return plugin, fmt

def _guess_fmt(figpath):
    f = subprocess.Popen(['file', figpath], stdout=subprocess.PIPE)
    fmt = str(f.stdout.read()).split(':')[1].strip()

    return fmt
