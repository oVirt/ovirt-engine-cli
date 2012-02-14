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
import os
from ovirtcli.utils.typehelper import TypeHelper
from ovirtsdk.infrastructure import brokers


class CmdShell(object):
    def __init__(self, context, parser):
        self.__context = context
        self.__parser = parser
        self.__owner = self

    def get_owner(self):
        return self.__owner


    def get_parser(self):
        return self.__parser

    def get_context(self):
        return self.__context

    context = property(get_context, None, None, None)
    parser = property(get_parser, None, None, None)
    owner = property(get_owner, None, None, None)

    ############################ CONFIG #################################
    def copy_environment_vars(self, context):
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


    def copy_cmdline_options(self, options, context, parser):
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
    #####################################################################
    def __generate_resource_specific_options__(self, args, line):
        specific_options = {}
        is_inner_type = False

        if line:
            spl = line.rstrip().split(' ')
            if len(spl) > 2:
                obj = spl[1].strip()
                for arg in spl[1:]:
                    if arg.startswith('--') and arg.endswith('id'):
                        parent_candidate = arg[2:len(arg) - 2]
                        canidate = TypeHelper.getDecoratorType(parent_candidate + obj)
                        if canidate and hasattr(brokers, canidate):
                            self.__add_resource_specific_options__(canidate,
                                                                specific_options,
                                                                key=obj)
                            is_inner_type = True
                            break
                if not is_inner_type:
                    self.__add_resource_specific_options__(obj, specific_options)
            elif len(spl) == 2 and spl[1] != '' and spl[1].strip() in args.keys():
                self.__add_resource_specific_options__(spl[1].strip(), specific_options)

            return specific_options

    def __add_resource_specific_options__(self, obj, specific_options, key=None):
        pass

    def get_resource_specific_options(self, args, line):
        return self.__generate_resource_specific_options__(args, line)

