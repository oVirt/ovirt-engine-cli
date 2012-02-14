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


from ovirtcli.shell.cmdshell import CmdShell
from ovirtcli.utils.typehelper import TypeHelper
from ovirtcli.utils.autocompletionhelper import AutoCompletionHelper
from ovirtsdk.infrastructure import brokers
from ovirtcli.utils.methodhelper import MethodHelper


class CreateCmdShell(CmdShell):
    NAME = 'create'

    def __init__(self, context, parser):
        CmdShell.__init__(self, context, parser)

    def do_create(self, args):
        return self.context.execute_string(CreateCmdShell.NAME + ' ' + args + '\n')

    def __add_resource_specific_options(self, obj, specific_options, key=None):
        obj_coll_type = TypeHelper.getDecoratorType(TypeHelper.to_plural(obj))
        if obj_coll_type:
            if hasattr(brokers, obj_coll_type):
                obj_coll = getattr(brokers, obj_coll_type)
                if obj_coll and hasattr(obj_coll, 'add'):
                    method_args = MethodHelper.get_documented_arguments(method_ref=getattr(obj_coll, 'add'),
                                                                        as_params_collection=True,
                                                                        spilt_or=True)
                    if method_args:
                        specific_options[obj if key == None else key] = method_args

    def complete_create(self, text, line, begidx, endidx):
        args = TypeHelper.get_types_by_method(False, 'add')
        self.__add_resource_specific_options__ = self.__add_resource_specific_options
        specific_options = self.get_resource_specific_options(args, line)

        return AutoCompletionHelper.complete(line, text, args, specific_options=specific_options)
