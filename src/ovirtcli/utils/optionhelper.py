#
# Copyright (c) 2015 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re


# These are the regular expressions used to check if an option should be
# used to find a parent entity. The preferred way is using the "parent"
# prefix, as it avoid potential conflicts with other options, but we
# need to support the "identifier" suffix without the "parent" prefix
# for backwards compatibility.
PARENT_ID_OPTION_EXPRESSIONS = [
    re.compile(r"^--parent-(?P<type>.+)-(identifier|name)$"),
    re.compile(r"^--(?P<type>.+)-identifier$"),
]


class OptionHelper(object):

    @staticmethod
    def is_parent_id_option(option):
        """
        Checks if the given option name is a reference to a parent
        entity.
        """
        for parent_id_option_expression in PARENT_ID_OPTION_EXPRESSIONS:
            if parent_id_option_expression.match(option):
                return True
        return False

    @staticmethod
    def get_parent_id_type(option):
        """
        Extracts the name of the type from an option that is a reference to
        a parent entity. For example, if the option is "--parent-host-name"
        this method will return "host".
        """
        for parent_id_option_expression in PARENT_ID_OPTION_EXPRESSIONS:
            match = parent_id_option_expression.match(option)
            if match is not None:
                return match.group("type")
        return None
