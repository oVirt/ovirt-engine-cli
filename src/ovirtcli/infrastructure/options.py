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
from ovirtcli.infrastructure import settings


class OvirtCliOptionParser(OptionParser):

    usage = '%prog [options]\n       %prog [options] command...'
    description = textwrap.dedent("""\
        This program is a command-line interface to %s Virtualization.
        """ % settings.OvirtCliSettings.PRODUCT)

    def __init__(self):

        OptionParser.__init__(self, usage=self.usage,
                              description=self.description)
        self.add_option('-d', '--debug', action='store_true',
                        help='enable debugging')
        self.add_option('-l', '--url',
                        help='specifies the API entry point URL (http[s]://server[:port]/ovirt-engine/api)')
        self.add_option('-u', '--username', help='connect as this user')
        self.add_option('-K', '--key-file', help='specify client PEM key-file')
        self.add_option('-C', '--cert-file', help='specify client PEM cert-file')
        self.add_option('-A', '--ca-file', help='specify server CA cert-file')
        self.add_option('-I', '--insecure', help='allow connecting to SSL sites without CA certificate',
                        action='store_true')
        self.add_option('-r', '--renew-session', help='automatically renew session upon expiration',
                        action='store_true')
        self.add_option('-D', '--dont-validate-cert-chain', help='do not validate server CA certificate',
                        action='store_true')
        self.add_option('-F', '--filter', help='enables user permission based filtering',
                        action='store_true')
        self.add_option('-P', '--port', help='specify port')
        self.add_option('-T', '--timeout', help='specify request timeout')
        self.add_option('-S', '--session-timeout', help='specify authentication session timeout in minutes (positive number)')
        self.add_option('-c', '--connect', action='store_true',
                        help='automatically connect')
        self.add_option('-f', '--file', metavar='FILE',
                        help='read commands from FILE instead of stdin')
        self.add_option('-e', '--extended-prompt', action='store_true',
                        help='display extra information in the prompt')
        self.add_option('-E', '--execute-command',
                        help='execute command and print the output to STDIO')
        self.add_option('--kerberos', action='store_true',
                        help='use Kerberos authentication')
        self.disable_interspersed_args()


