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


import textwrap
from optparse import OptionParser


class OvirtCliOptionParser(OptionParser):

    usage = '%prog [options]\n       %prog [options] command...'
    description = textwrap.dedent("""\
        This program is a command-line interface to Red Hat Enterprise
        Virtualization.
        """)

    def __init__(self):
        OptionParser.__init__(self, usage=self.usage,
                              description=self.description)
        self.add_option('-d', '--debug', action='store_true',
                        help='enable debugging')
        self.add_option('-v', '--verbose', action='store_const',
                        const=10, dest='verbosity', help='be more verbose')
        self.add_option('-H', '--help-commands', action='store_true',
                        help='show help on commands')
        self.add_option('-U', '--url',
                        help='specifies the API entry point URL')
        self.add_option('-u', '--username', help='connect as this user')
        self.add_option('-p', '--password', help='specify password')
        self.add_option('-r', '--read-input', action='store_true',
                        help='read pre-formatted input on stdin')
        self.add_option('-i', '--input-format', metavar='FORMAT',
                        help='input format for pre-formatted input')
        self.add_option('-o', '--output-format', metavar='FORMAT',
                         help='specfies the output format')
        self.add_option('-c', '--connect', action='store_true',
                        help='automatically connect')
        self.add_option('-f', '--filter', metavar='FILE',
                        help='read commands from FILE instead of stdin')
        self.add_option('-w', '--wide', action='store_true',
                        help='wide display')
        self.add_option('-n', '--no-header', action='store_false',
                        dest='header', help='suppress output header')
        self.add_option('-F', '--fields', help='fields to display')
        self.disable_interspersed_args()
