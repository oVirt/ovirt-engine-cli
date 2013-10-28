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


import sys
import textwrap
from optparse import OptionParser, BadOptionError, AmbiguousOptionError
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
                        help='specifies the API entry point URL (http[s]://server[:port]/api)')
        self.add_option('-u', '--username', help='connect as this user')
        self.add_option('-K', '--key-file', help='specify client PEM key-file')
        self.add_option('-C', '--cert-file', help='specify client PEM cert-file')
        self.add_option('-A', '--ca-file', help='specify server CA cert-file')
        self.add_option('-I', '--insecure', help='allow connecting to SSL sites without CA certificate',
                        action='store_true')
        self.add_option('-D', '--dont-validate-cert-chain', help='do not validate server CA certificate',
                        action='store_true')
        self.add_option('-F', '--filter', help='enables user permission based filtering',
                        action='store_true')
        self.add_option('-P', '--port', help='specify port')
        self.add_option('-T', '--timeout', help='specify request timeout')
        self.add_option('-S', '--session-timeout', help='specify authentication session timeout (positive number)')
        self.add_option('-c', '--connect', action='store_true',
                        help='automatically connect')
        self.add_option('-f', '--file', metavar='FILE',
                        help='read commands from FILE instead of stdin')
        self.add_option('-e', '--extended-prompt', action='store_true',
                        help='display extra information in the prompt')
        self.add_option('-E', '--execute-command',
                        help='execute command and print the output to STDIO')
        self.disable_interspersed_args()

        # list of hidden app. options (long format)
        self.app_options = ['--password', '-p']

    def exit(self, status=0, msg=None):
        self.values._exit = True
        if msg: print (msg + 'see help for more details.\n')
        sys.exit(status)

    def _match_long_opt(self, opt):
        """_match_long_opt(opt : string) -> string

        Determine which long option string 'opt' matches, ie. which one
        it is an unambiguous abbrevation for.  Raises BadOptionError if
        'opt' doesn't unambiguously match any long option string.
        """
        return self._match_abbrev(opt, self._long_opt)

    def _match_abbrev(self, s, wordmap):
        """_match_abbrev(s : string, wordmap : {string : Option}) -> string

        Return the string key in 'wordmap' for which 's' is an unambiguous
        abbreviation.  If 's' is found to be ambiguous or doesn't match any of
        'words', raise BadOptionError.
        """

        # Is there an exact match?
        if s in wordmap:
            return s
        else:
            # Isolate all words with s as a prefix.
            option_keys = wordmap.keys()
            for item in self.app_options:
                if item not in  option_keys:
                    option_keys.append(item)
            possibilities = [word for word in option_keys
                             if word.startswith(s)]
            # No exact match, so there had better be just one possibility.
            if len(possibilities) == 1:
                return possibilities[0]
            elif not possibilities:
                raise BadOptionError(s)
            else:
                # More than one possible completion: ambiguous prefix.
                possibilities.sort()
                raise AmbiguousOptionError(s, possibilities)

    def _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        if "=" in arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = True
        else:
            opt = arg
            had_explicit_value = False

        opt = self._match_long_opt(opt)
        if opt not in self._long_opt.keys() and opt in self.app_options:
            # This is app. option (long format)
            self.add_option('', opt, help='private app. option')
        option = self._long_opt[opt]
        if option.takes_value():
            nargs = option.nargs
            if len(rargs) < nargs:
                if nargs == 1:
                    self.error(_("%s option requires an argument") % opt)
                else:
                    self.error(_("%s option requires %d arguments")
                               % (opt, nargs))
            elif nargs == 1:
                value = rargs.pop(0)
            else:
                value = tuple(rargs[0:nargs])
                del rargs[0:nargs]

        elif had_explicit_value:
            self.error(_("%s option does not take a value") % opt)

        else:
            value = None

        option.process(opt, value, values, self)
