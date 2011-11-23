
import os.path
import pwd


def get_home_dir():
    """Return the user's home directory."""
    home = os.environ.get('HOME')
    if home is not None:
        return home
    try:
        pw = pwd.getpwuid(os.getuid())
    except Exception:
        return None
    return pw.pw_dir

def local_settings_file(name):
    """"Return the local settings file for `name'."""
    home = get_home_dir()
    if home is None:
        return
    name = name.replace('-', '').replace('_', '')
    fname = os.path.join(home, '.%src' % name)
    return fname

def which(cmd):
    """Find a command `cmd' in the path."""
    if cmd.startswith('/') and os.access(cmd, os.X_OK):
        return cmd
    path = os.environ.get('PATH')
    path = path.split(os.pathsep)
    for dir in path:
        fname = os.path.join(dir, cmd)
        if os.access(fname, os.X_OK):
            return fname

def get_pager():
    """Return the platform specific pager."""
    pager = os.environ.get('PAGER')
    if pager is None and which('less'):
        pager = 'less -FSRX'
    if pager is None and which('more'):
        pager = 'more'
    return pager
