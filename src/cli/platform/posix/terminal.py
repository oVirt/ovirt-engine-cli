
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
#        self._tty = os.open('/dev/tty', os.O_RDWR)
        self._tty = os.open('/tmp/xxx', os.O_RDWR)
        curses.setupterm()

    def _get_width(self):
        packed = fcntl.ioctl(self._tty, termios.TIOCGWINSZ, 'xxxx')
        width = struct.unpack('@HH', packed)[1]
        return width

    width = property(_get_width)

    def _get_height(self):
        packed = fcntl.ioctl(self._tty, termios.TIOCGWINSZ, 'xxxx')
        height = struct.unpack('@HH', packed)[0]
        return height

    def clear(self):
        if not self.stdout.isatty():
            return
        chars = curses.tigetstr('clear')
        self.stdout.write(chars)

    def set_echo(self, echo):
        attrs = termios.tcgetattr(self._tty)
        if echo:
            attrs[3] |= termios.ECHO
        else:
            attrs[3] &= ~termios.ECHO
        termios.tcsetattr(self._tty, termios.TCSANOW, attrs)

    def close(self):
        os.close(self._tty)

    def readline(self, prompt):
        line = raw_input(prompt)
        line += '\n'
        return line
