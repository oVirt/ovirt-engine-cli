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


from cli.settings import Settings, enum, boolean


class OvirtCliSettings(Settings):

    settings = Settings.settings + [
        ('ovirt-shell:url', str, ''),
        ('ovirt-shell:username', str, ''),
        ('ovirt-shell:password', str, ''),        
        ('ovirt-shell:key_file', str, None),
        ('ovirt-shell:cert_file', str, None),
        ('ovirt-shell:port', int, None),
        ('ovirt-shell:timeout', int, None),
        ('ovirt-shell:input_format', enum('xml'), 'xml'),
        ('ovirt-shell:output_format', enum('xml', 'text'), 'text'),
        ('ovirt-shell:wide', boolean, False),
        ('ovirt-shell:header', boolean, True),
        ('ovirt-shell:fields', str, None),
        ('ovirt-shell:fields.*', str, None),
        ('ovirt-shell:ps1.connected', str, '(oVirt %(version)s) > '),
        ('ovirt-shell:ps1.disconnected', str, '(disconnected) > ')
    ]
