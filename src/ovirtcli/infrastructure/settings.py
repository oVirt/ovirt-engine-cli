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
    """Welcome to %s shell""" % PRODUCT

    DISCONNECTED_TEMPLATE = \
""">>> disconnected from %s manager <<<""" % PRODUCT

    CONNECTED_TEMPLATE = \
">>> connected to " + PRODUCT + " manager %s <<<"

    settings = Settings.settings + [
        ('ovirt-shell:name', str, '%s-shell' % PRODUCT),
        ('ovirt-shell:url', str, ''),
        ('ovirt-shell:username', str, ''),
        ('ovirt-shell:password', str, ''),
        ('ovirt-shell:key_file', str, None),
        ('ovirt-shell:cert_file', str, None),
        ('ovirt-shell:ca_file', str, None),
        ('ovirt-shell:insecure', boolean, False),
        ('ovirt-shell:dont_validate_cert_chain', boolean, False),
        ('ovirt-shell:filter', boolean, False),
        ('ovirt-shell:port', int, None),
        ('ovirt-shell:timeout', int, None),
        ('ovirt-shell:session_timeout', int, None),
        ('ovirt-shell:input_format', enum('xml'), 'xml'),
        ('ovirt-shell:output_format', enum('xml', 'text'), 'text'),
        ('ovirt-shell:wide', boolean, False),
        ('ovirt-shell:header', boolean, True),
        ('ovirt-shell:fields', str, None),
        ('ovirt-shell:fields.*', str, None),
        ('ovirt-shell:ps1.connected', str, '[' + PRODUCT + ' shell %(version)s (connected)]# '),
        ('ovirt-shell:ps2.connected', str, '[' + PRODUCT + ' shell (connected)]# '),
        ('ovirt-shell:ps3.connected', str, '[' + PRODUCT + ' shell (connected@%(host)s)]# '),
        ('ovirt-shell:ps1.disconnected', str, '[%s shell (disconnected)]# ' % PRODUCT),
        ('ovirt-shell:ps1.unauthorized', str, '[%s shell (unauthorized)]# ' % PRODUCT),
        ('ovirt-shell:commands', str, '%s shell commands:' % PRODUCT),
        ('ovirt-shell:misc_commands', str, '%s shell commands:' % PRODUCT),
        ('ovirt-shell:version', str, ''),
        ('ovirt-shell:prompt', str, ''),
        ('ovirt-shell:extended_prompt', boolean, False),
        ('ovirt-shell:execute_command', str, None),
        ('ovirt-shell:file', str, None),
        ('ovirt-shell:renew_session', boolean, False),
        ('ovirt-shell:kerberos', boolean, False),
    ]

    # config file white list
    config_items = [
        'cli:autopage',
        'cli:autoconnect',
        'ovirt-shell:url',
        'ovirt-shell:username',
        'ovirt-shell:password',
        'ovirt-shell:key_file',
        'ovirt-shell:cert_file',
        'ovirt-shell:ca_file',
        'ovirt-shell:insecure',
        'ovirt-shell:dont_validate_cert_chain',
        'ovirt-shell:filter',
        'ovirt-shell:timeout',
        'ovirt-shell:session_timeout',
        'ovirt-shell:extended_prompt',
        'ovirt-shell:renew_session',
        'ovirt-shell:kerberos',
    ]
