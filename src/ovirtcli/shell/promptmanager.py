#
# Copyright (c) 2013 Red Hat, Inc.
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
from ovirtcli.utils.colorhelper import ColorHelper
from cli.executionmode import ExecutionMode
from ovirtcli.shell.promptmode import PromptMode
from urlparse import urlparse


class PromptManager(object):
    """
    manages shell prompt
    """
    def __init__(self, engineshell):
        self.__engineshell = engineshell
        self.__org_prompt = ''
        self.__engineshell.prompt = self.set_prompt(
                                    PromptMode.Disconnected
        )

    # PromptMode.Default
    def set_prompt(self, mode):
        self.__engineshell.onPromptChange.fire()
        if mode == PromptMode.Multiline:
            if not self.__org_prompt:
                self.__org_prompt = self.__engineshell.prompt
            self.__engineshell.prompt = '> '
        elif mode == PromptMode.Original:
            if self.__org_prompt:
                self.__engineshell.prompt = self.__org_prompt
                self.__org_prompt = ''
        elif mode == PromptMode.Disconnected or mode == PromptMode.Default:
            if not self.__org_prompt and self.__engineshell.prompt != "(Cmd) ":
                self.__org_prompt = self.__engineshell.prompt
            self.__engineshell.prompt = self.__get_disconnected_prompt()
        elif mode == PromptMode.Connected:
            self.__engineshell.prompt = self.__get_connected_prompt()
        elif mode == PromptMode.Unauthorized:
            self.__engineshell.prompt = self.__get_unauthorized_prompt()

    def __get_unauthorized_prompt(self):
        dprompt = self.__engineshell.context.settings.get('ovirt-shell:ps1.unauthorized')
        if self.__engineshell.context.mode != ExecutionMode.SCRIPT \
           and self.__engineshell.context.interactive:
            dprompt = dprompt.replace(
                          "unauthorized",
                          ColorHelper.colorize(
                                "unauthorized",
                                color=ColorHelper.RED,
                                is_prompt=True
                          )
            )
        return dprompt

    def __get_disconnected_prompt(self):
        dprompt = self.__engineshell.context.settings.get('ovirt-shell:ps1.disconnected')
        if self.__engineshell.context.mode != ExecutionMode.SCRIPT \
           and self.__engineshell.context.interactive:
            dprompt = dprompt.replace(
                          "disconnected",
                          ColorHelper.colorize(
                                "disconnected",
                                color=ColorHelper.RED,
                                is_prompt=True
                          )
            )
        return dprompt

    def __get_connected_prompt(self):
        if self.__engineshell.context.settings.get('ovirt-shell:extended_prompt'):
            url = self.__engineshell.context.settings.get('ovirt-shell:url')
            url_obj = urlparse(url)
            if url_obj and hasattr(url_obj, 'hostname'):
                cprompt = self.__engineshell.context.settings.get(
                               'ovirt-shell:ps3.connected'
                          ) % {
                               'host':url_obj.hostname
                }
                if self.__engineshell.context.mode != ExecutionMode.SCRIPT \
                   and self.__engineshell.context.interactive:
                    cprompt = cprompt.replace(
                              "connected@" + url_obj.hostname,
                              ColorHelper.colorize(
                                    'connected@' + url_obj.hostname,
                                    color=ColorHelper.GREEN,
                                    is_prompt=True
                              )
                )
                return cprompt

        cprompt = self.__engineshell.context.settings.get('ovirt-shell:ps2.connected')
        if self.__engineshell.context.mode != ExecutionMode.SCRIPT \
           and self.__engineshell.context.interactive:
            cprompt = cprompt.replace(
                              "connected",
                              ColorHelper.colorize(
                                 "connected",
                                 color=ColorHelper.GREEN,
                                 is_prompt=True
                               )
        )
        return cprompt
