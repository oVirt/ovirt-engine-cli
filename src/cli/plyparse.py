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


import os.path
import inspect
import logging

from ply import lex, yacc


class PLYParser(object):
    """Wrapper object for PLY lexer/parser."""

    def _table_name(self, suffix, relative=False):
        """Return the module name for PLY's parsetab file."""
        mname = inspect.getmodule(self.__class__).__name__ + '_' + suffix
        if relative:
            mname = mname.split('.')[-1]
        return mname

    def _write_tables(self):
        """Write parser table (for distribution purposes)."""
        path = inspect.getfile(self.__class__)
        parent = os.path.split(path)[0]
        # Need to change directories to get the file written at the right
        # location.
        tabname = self._table_name('lex', relative=True)
        lex.lex(object=self, lextab=tabname, optimize=True, debug=False,
                outputdir=parent)
        tabname = self._table_name('tab', relative=True)
        yacc.yacc(module=self, tabmodule=tabname, optimize=True, debug=False,
                  outputdir=parent)

    def parse(self, input, fname=None, debug=False):
        optimize = not debug
        tabname = self._table_name('lex')
        lexer = lex.lex(object=self, lextab=tabname,
                        optimize=optimize, debug=debug)
        if hasattr(input, 'read'):
            input = input.read()
        lexer.input(input)
        tabname = self._table_name('tab')
        parser = yacc.yacc(module=self, tabmodule=tabname,
                           optimize=optimize, debug=debug,
                           write_tables=0)
        if debug:
            logger = logging.getLogger()
        else:
            logger = yacc.NullLogger()
        parsed = parser.parse(lexer=lexer, tracking=True, debug=logger)
        return parsed
