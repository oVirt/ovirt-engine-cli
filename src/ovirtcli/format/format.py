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


class Formatter(object):
    """Base class for formatter objects."""

    name = None

    def format(self, context, result, scope=None):
        raise NotImplementedError

    def format_terminal(self, text, border, termwidth, newline="\n\n", header=None, offsettext=True):
        """
        formats (pretty) screen width adapted messages with border
        
        @param text: text to prin
        @param border: border to use
        @param termwidth: terminal width
        @param newline: new line separator (default is '\n\n')
        @param header: upper border header (default is None)
        @param offsettext: align the text to middle of the screen (default True)
        """

        linlebreak = '\r\n'
        offset = "  "
        space = " "
        introoffset = (termwidth / 2 - (len(text) / 2))
        borderoffset = (termwidth - 4)

        # align multilined output
        if text.find(linlebreak) <> -1 :
            offsettext = False
            text = offset + text.replace(linlebreak, (linlebreak + offset))

        if (header):
            headeroffset = (borderoffset / 2 - ((len(header) / 2)))
            oddoffset = 0 if termwidth & 1 != 0 else 1
            return offset + headeroffset * border + space + header + space + \
                   (headeroffset - len(offset) - oddoffset) * border + newline + \
                   ((introoffset * space)  if offsettext else "") + text + newline + \
                   offset + borderoffset * border + newline
        return offset + borderoffset * border + newline + \
               ((introoffset * space) if offsettext else "") + text + newline + \
               offset + borderoffset * border + newline

