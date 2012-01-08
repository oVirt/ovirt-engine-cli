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


def create(cls, *args, **kwargs):
    """Create ovirtcli objects."""
    from ovirtcli.format import Formatter, get_formatter
    if issubclass(cls, Formatter):
        format = args[0]
        cls = get_formatter(format)
        obj = cls(**kwargs)
    else:
        obj = cls(*args, **kwargs)
    return obj
