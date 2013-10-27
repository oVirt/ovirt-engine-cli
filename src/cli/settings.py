#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import re
import stat

from fnmatch import fnmatch
from ConfigParser import ConfigParser
from cli import platform
import types
import sys


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
        ('cli:autoconnect', boolean, True),
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
            value = self.__normalazie_value(value)
            if value:
                try:
                    value = validator(value)
                except ValueError:
                    # delegate type related errors handling to SDK
                    pass
            found = True
        if not found:
            raise KeyError, 'unknown setting: %s' % key
        for pattern, callback in self.callbacks:
            if not fnmatch(key, pattern):
                continue
            callback(key, value)
        super(Settings, self).__setitem__(key, value)

    def __normalazie_value(self, value):
        """Converts string value to python type """
        if value:
            if type(value) == types.StringType and value == 'None':
                return None
        return value

    def get_defaults(self):
        """Return a dictionary with the default settings."""
        return dict(((p, d) for p, t, d in self.settings
                     if '*' not in p))

    def load_config_file(self):
        """
        Load default values from a configuration file.

        @return: if-file-exist, is-config-file-in-old-format
        """
        old_format = False
        fname = platform.local_settings_file(self.name)
        from ovirtcli.infrastructure.settings import OvirtCliSettings
        if fname is None:
            return False, old_format
        cp = ConfigParser()
        if not cp.read(fname):
            return False, old_format
        for section in cp.sections():
            items = cp.items(section)
            if len(items) != len(OvirtCliSettings.config_items):
                old_format = True
            for key, value in items:
                conf_key = '%s:%s' % (section, key)
                if conf_key not in OvirtCliSettings.config_items:
                    old_format = True
                else:
                    self[conf_key] = value

        return True, old_format

    def _write_config_file(self, settings, example=False):
        """Overwrite the configuration file with the current settings."""
        fname = platform.local_settings_file(self.name)
        if fname is None:
            return
        ftmp = '%s.%d-tmp' % (fname, os.getpid())
        fout = file(ftmp, 'w')
        sections = {}
        from ovirtcli.infrastructure.settings import OvirtCliSettings
        for key in settings:
            if key in OvirtCliSettings.config_items:
                section, name = key.split(':')
                if section not in sections:
                    sections[section] = {}
                sections[section][name] = settings[key]
        for section in sorted(sections):
            fout.write('[%s]\n' % section)
            for key in sections[section]:
                if example:
                    fout.write('#')
                fout.write('%s = %s\n' % (key, sections[section][key]))
        fout.close()
        self.set_file_permissions(ftmp)
        os.rename(ftmp, fname)

    def set_file_permissions(self, f):
        # Set UID bit
        # Owner has read permission
        # Owner has write permission
        # Do not dump the file.
        os.chmod(f,
                 stat.S_ISGID |
                 stat.S_IRUSR |
                 stat.S_IWUSR |
                 stat.UF_NODUMP)

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
