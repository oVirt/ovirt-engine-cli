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

    PRODUCT = 'oVirt'

    INTRO = \
    """
        
 ++++++++++++++++++++++++++++++++++++++++++
 
           Welcome to %s shell
 
 ++++++++++++++++++++++++++++++++++++++++++
        
    """ % PRODUCT

    DISCONNECTED_TEMPLATE = \
"""
  =======================================
  >>> disconnected from %s manager <<<
  =======================================
 """ % PRODUCT

    CONNECTED_TEMPLATE = \
"\n ==========================================\n" + \
" >>> connected to " + PRODUCT + " manager %s <<<\n" + \
" ==========================================\n\n"

    settings = Settings.settings + [
        ('ovirt-shell:name', str, '%s-shell' % PRODUCT),
        ('ovirt-shell:url', str, ''),
        ('ovirt-shell:username', str, ''),
        ('ovirt-shell:password', str, ''),
        ('ovirt-shell:key_file', str, None),
        ('ovirt-shell:cert_file', str, None),
        ('ovirt-shell:ca_file', str, None),
        ('ovirt-shell:port', int, -1),
        ('ovirt-shell:timeout', int, -1),
        ('ovirt-shell:input_format', enum('xml'), 'xml'),
        ('ovirt-shell:output_format', enum('xml', 'text'), 'text'),
        ('ovirt-shell:wide', boolean, False),
        ('ovirt-shell:header', boolean, True),
        ('ovirt-shell:fields', str, None),
        ('ovirt-shell:fields.*', str, None),
        ('ovirt-shell:ps1.connected', str, '[' + PRODUCT + ' shell %(version)s (connected)]# '),
        ('ovirt-shell:ps2.connected', str, '[' + PRODUCT + ' shell (connected)]# '),
        ('ovirt-shell:ps1.disconnected', str, '[%s shell (disconnected)]# ' % PRODUCT),
        ('ovirt-shell:commands', str, '%s shell commands:' % PRODUCT),
        ('ovirt-shell:misc_commands', str, '%s shell commands:' % PRODUCT),
        ('ovirt-shell:version', str, ''),
        ('ovirt-shell:prompt', str, '')
    ]
