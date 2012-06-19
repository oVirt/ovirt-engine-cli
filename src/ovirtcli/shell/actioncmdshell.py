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


class ActionCmdShell(CmdShell):
    NAME = 'action'

    def __init__(self, context, parser):
        CmdShell.__init__(self, context, parser)

    def do_action(self, args):
        return self.context.execute_string(ActionCmdShell.NAME + ' ' + args + '\n')

    def __add_resource_specific_options(self, obj, specific_options, line, key=None):
        obj_type = TypeHelper.getDecoratorType(TypeHelper.to_singular(obj))
        if obj_type and hasattr(brokers, obj_type):

            args = TypeHelper.get_actionable_types(expendNestedTypes=True)
            specific_arguments = self.get_resource_specific_options(args,
                                                                    line,
                                                                    callback=self.__add_resource_specific_arguments)

            action = None
            memeber = key if key is not None else obj
            for arg in line.split():
                if specific_arguments.has_key(memeber) and arg in specific_arguments[memeber]:
                    action = arg
                    break

            if action:
                obj_typ_ref = getattr(brokers, obj_type)
                if obj_typ_ref and hasattr(obj_typ_ref, action):
                    method_args = MethodHelper.get_documented_arguments(method_ref=getattr(obj_typ_ref, action),
                                                                        as_params_collection=True,
                                                                        spilt_or=True)
                    if method_args:
                        specific_options[memeber] = method_args

    def __add_resource_specific_arguments(self, obj, specific_options, line, key=None):
        obj_type = TypeHelper.getDecoratorType(TypeHelper.to_singular(obj))
        if obj_type and hasattr(brokers, obj_type):
            method_args = MethodHelper.get_object_methods(getattr(brokers, obj_type),
                                                          exceptions=['delete', 'update'])
            if method_args:
                specific_options[obj if key == None else key] = method_args

    def complete_action(self, text, line, begidx, endidx):
        args = TypeHelper.get_actionable_types(expendNestedTypes=True)
        specific_arguments = {}

        specific_options = self.get_resource_specific_options(args,
                                                              line,
                                                              callback=self.__add_resource_specific_options)

        if not specific_options:
            specific_arguments = self.get_resource_specific_options(args,
                                                                    line,
                                                                    callback=self.__add_resource_specific_arguments)

        return AutoCompletionHelper.complete(line,
                                             text,
                                             args,
                                             specific_options=specific_options,
                                             specific_arguments=specific_arguments)
