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


import os
import sys

from ovirtcli.options import OvirtCliOptionParser
from ovirtcli.context import OvirtCliExecutionContext
from ovirtcli.object import create

def copy_environment_vars(context):
    """Copy environment variables into configuration variables in the
    execution context."""
    for var in ('url', 'username', 'password'):
        envvar = 'oVirt_%s' % var.upper()
        confvar = 'ovirt-shell:%s' % var
        if envvar in os.environ:
            try:
                context.settings[confvar] = os.environ[envvar]
            except ValueError, e:
                sys.stderr.write('error: %s\n' % str(e))
                return False
    return True


def copy_cmdline_options(options, context, parser):
    """Copy command-line options into configuration variables in the
    execution context."""
    for opt in parser.option_list:
        if not opt.dest:
            continue
        value = getattr(options, opt.dest)
        if value is None:
            continue
        if opt.dest in ('debug', 'verbosity'):
            dest = 'cli:%s' % opt.dest
        else:
            dest = 'ovirt-shell:%s' % opt.dest
        try:
            context.settings[dest] = value
        except KeyError:
            pass
        except ValueError, e:
            sys.stderr.write('error: %s\n' % str(e))
            return False
    return True


def main():
    """Entry point for ovirt-shell."""
    parser = create(OvirtCliOptionParser)
    opts, args = parser.parse_args()

    context = create(OvirtCliExecutionContext)
    if not copy_environment_vars(context):
        sys.exit(1)
    if not copy_cmdline_options(opts, context, parser):
        sys.exit(1)

    if opts.help_commands:
        args = ['help']

    if opts.filter:
        try:
            sys.stdin = file(opts.filter)
        except IOError, e:
            sys.stderr.write('error: %s\n' % e.strerror)
            sys.exit(1)

    if opts.connect or len(args) > 0:
        context.execute_string('connect\n')

    if len(args) == 0:
        context.execute_loop()
    else:
        command = ' '.join(args)
        if opts.read_input:
            buf = sys.stdin.read()
            command += '<<EOM\n%s\nEOM' % buf
        command += '\n'
        context.execute_string(command)

    sys.exit(context.status)

if __name__ == "__main__":
    main()
