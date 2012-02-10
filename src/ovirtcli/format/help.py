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
from string import Template


class Help(object):

    ruler = '='

    @staticmethod
    def format(text, subst):
        """Format a command help text, and make '$' substitutions."""
        lines = text.splitlines()
        if not lines:
            return ''
        indent = Help.__indent_level(lines[0])
        for ix in range(len(lines)):
            line = lines[ix][indent:]
            if line.startswith('==') and line.endswith('=='):
                line = line[2:-2].strip().upper()
            else:
                line = '  ' + line
            if '$' in line:
                template = Template(line)
                line = template.safe_substitute(subst)
                if '\n' in line:
                    lindent = Help.__indent_level(line)
                    line = line.replace('\n', '\n' + ' ' * lindent)
            lines[ix] = line
        text = '\n' + '\n'.join(lines) + '\n'
        return text

    @staticmethod
    def __indent_level(s):
        """INTERNAL: return the indentation level of a string."""
        for i in range(len(s)):
            if not s[i].isspace():
                return i
        return len(s)

    @staticmethod
    def format_topics(header, cmds, cmdlen, maxcol):
        txt = ''
        if cmds:
            txt += "%s\n" % str(header)
            if Help.ruler:
                txt += "%s\n" % str(Help.ruler * len(header))
            Help.__columnize(cmds, txt, maxcol - 1)
            txt += "\n"
        return txt

    @staticmethod
    def __columnize(list, txt, displaywidth=80):
        """Display a list of strings as a compact set of columns.

        Each column is only as wide as necessary.
        Columns are separated by two spaces (one was not legible enough).
        """
        if not list:
            txt += "<empty>\n"
            return
        nonstrings = [i for i in range(len(list))
                        if not isinstance(list[i], str)]
        if nonstrings:
            raise TypeError, ("list[i] not a string for i in %s" %
                              ", ".join(map(str, nonstrings)))
        size = len(list)
        if size == 1:
            txt += '%s\n' % str(list[0])
            return
        # Try every row count from 1 upwards
        for nrows in range(1, len(list)):
            ncols = (size + nrows - 1) // nrows
            colwidths = []
            totwidth = -2
            for col in range(ncols):
                colwidth = 0
                for row in range(nrows):
                    i = row + nrows * col
                    if i >= size:
                        break
                    x = list[i]
                    colwidth = max(colwidth, len(x))
                colwidths.append(colwidth)
                totwidth += colwidth + 2
                if totwidth > displaywidth:
                    break
            if totwidth <= displaywidth:
                break
        else:
            nrows = len(list)
            ncols = 1
            colwidths = [0]
        for row in range(nrows):
            texts = []
            for col in range(ncols):
                i = row + nrows * col
                if i >= size:
                    x = ""
                else:
                    x = list[i]
                texts.append(x)
            while texts and not texts[-1]:
                del texts[-1]
            for col in range(len(texts)):
                texts[col] = texts[col].ljust(colwidths[col])
            txt += "%s\n" % str("  ".join(texts))
