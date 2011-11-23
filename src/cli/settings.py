
import os
import re

from fnmatch import fnmatch
from ConfigParser import ConfigParser
from cli import platform


class enum(object):
    """A setting that can have one of a predetermined set of values."""

    def __init__(self, *values):
        self.values = values

    def __call__(self, value):
        if value not in self.values:
            raise ValueError, 'illegal value: %s' % value
        return value


class regex(object):
    """A setting that is matched against a regular expression."""

    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __call__(self, value):
        if not self.regex.match(value):
            raise ValueError, 'illegal value: %s' % value
        return value


def boolean(value):
    """A boolean setting."""
    if isinstance(value, int) or isinstance(value, bool):
        return bool(value)
    elif isinstance(value, str):
        s = value.lower()
        if s in ('true', 'on', '1'):
            return True
        elif s in ('false', 'off', '0'):
            return False
    raise ValueError, 'illegal value: %s' % value


class Settings(dict):
    """Base class for settings."""

    settings = [
        ('cli:ps1', str, '$ '),
        ('cli:ps2', str, '> '),
        ('cli:debug', boolean, False),
        ('cli:verbosity', int, 0),
        ('cli:autopage', boolean, True),
        ('cli:pager', str, None)
    ]

    def __init__(self, name):
        """Constructor."""
        self.name = name
        self.callbacks = []
        self.update(self.get_defaults())

    def __setitem__(self, key, value):
        """Validate a variable. Also calls callbacks."""
        found = False
        for pattern, validator, default in self.settings:
            if not fnmatch(key, pattern):
                continue
            value = validator(value)
            found = True
        if not found:
            raise KeyError, 'unknown setting: %s' % key
        for pattern, callback in self.callbacks:
            if not fnmatch(key, pattern):
                continue
            callback(key, value)
        super(Settings, self).__setitem__(key, value)

    def get_defaults(self):
        """Return a dictionary with the default settings."""
        return dict(((p, d) for p, t, d in self.settings
                     if d is not None and '*' not in p))

    def load_config_file(self):
        """Load default values from a configuration file."""
        fname = platform.local_settings_file(self.name)
        if fname is None:
            return False
        cp = ConfigParser()
        if not cp.read(fname):
            return False
        for section in cp.sections():
            for key, value in cp.items(section):
                self['%s:%s' % (section, key)] = value
        return True

    def _write_config_file(self, settings, example=False):
        """Overwrite the configuration file with the current settings."""
        fname = platform.local_settings_file(self.name)
        if fname is None:
            return
        ftmp = '%s.%d-tmp' % (fname, os.getpid())
        fout = file(ftmp, 'w')
        sections = {}
        for key in settings:
            section, name = key.split(':')
            if section not in sections:
                sections[section] = {}
            sections[section][name] = settings[key]
        for section in sorted(sections):
            fout.write('[%s]\n' % section)
            for key in sorted(sections[section]):
                if example:
                    fout.write('#')
                fout.write('%s = %s\n' % (key, sections[section][key]))
        fout.close()
        os.rename(ftmp, fname)

    def write_config_file(self):
        """Overwrite the config file with the current settings."""
        self._write_config_file(self, False)

    def write_example_config_file(self):
        """Write an example config file."""
        self._write_config_file(self.get_defaults(), True)

    def add_callback(self, pattern, callback):
        """Register a callback function. The callback is called when the
        variable identified by `pattern' changes."""
        self.callbacks.append((pattern, callback))
