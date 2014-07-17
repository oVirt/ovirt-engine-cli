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

import termios
import struct
import curses

from cli.terminal import Terminal

#TODO: check it the same import
#import fcntl
from mailbox import fcntl


class PosixTerminal(Terminal):
    """A terminal for Posix style systems."""

    def __init__(self, *args):
        super(PosixTerminal, self).__init__(*args)
        try:
            self._tty = os.open('/dev/tty', os.O_RDWR)
            curses.setupterm()
        except OSError:
            self._tty = None

    def _get_width(self):
        if self._tty:
            packed = fcntl.ioctl(self._tty, termios.TIOCGWINSZ, 'xxxx')
            width = struct.unpack('@HH', packed)[1]
        else:
            width = 80
        return width

    width = property(_get_width)

    def _get_height(self):
        if self._tty:
            packed = fcntl.ioctl(self._tty, termios.TIOCGWINSZ, 'xxxx')
            height = struct.unpack('@HH', packed)[0]
        else:
            height = 25
        return height

    def clear(self):
        if self._tty:
            os.system("clear")

    def set_echo(self, echo):
        if self._tty:
            attrs = termios.tcgetattr(self._tty)
            if echo:
                attrs[3] |= termios.ECHO
            else:
                attrs[3] &= ~termios.ECHO
            termios.tcsetattr(self._tty, termios.TCSANOW, attrs)

    def close(self):
        if self._tty:
            os.close(self._tty)

    def readline(self, prompt):
        line = raw_input(prompt)
        line += '\n'
        return line
