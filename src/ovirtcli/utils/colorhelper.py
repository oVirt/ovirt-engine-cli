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


class ColorHelper():
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    __PROMPT_PREFIX = "\001"
    __PREFIX = "\033[1;%dm"
    __SUFFIX = "\033[1;m"
    ___PROMPT_SUFFIX = "\002"
    __OFFSET = 30

    @staticmethod
    def colorize(text, color, is_prompt=False):
        """
        Colors text

        @param text: text to color
        @param color: color to use (ColorHelper.RED|ColorHelper.BLUE...)
        @param param: is_prompt indicates that should be performed prompt
                      unique treatment
        """
        if color:
            if is_prompt:
                return (
                       ColorHelper.__PROMPT_PREFIX + \
                       ColorHelper.__PREFIX + \
                       ColorHelper.___PROMPT_SUFFIX
                       ) % \
                       (ColorHelper.__OFFSET + color) + \
                       text + \
                       (
                       ColorHelper.__PROMPT_PREFIX + \
                       ColorHelper.__SUFFIX + \
                       ColorHelper.___PROMPT_SUFFIX
                       )
            return ColorHelper.__PREFIX % \
                   (ColorHelper.__OFFSET + color) + \
                   text + \
                   ColorHelper.__SUFFIX
        return text
