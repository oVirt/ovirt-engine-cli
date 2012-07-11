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
import types


class VersionHelper():
    @staticmethod
    def to_string(version, exceptions=['*final']):
        """Converts version to string format"""
        str_ver = ''
        for item in version:
            if item not in exceptions:
                if types.IntType == type(item) or item.isdigit():
                    str_ver += str(int(item))
                else:
                    str_ver += item
                str_ver += "."
        return str_ver[:len(str_ver) - 1]
