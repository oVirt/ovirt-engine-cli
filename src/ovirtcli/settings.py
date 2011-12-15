
from cli.settings import Settings, enum, boolean


class OvirtCliSettings(Settings):

    settings = Settings.settings + [
        ('ovirt-shell:url', str, ''),
        ('ovirt-shell:username', str, ''),
        ('ovirt-shell:password', str, ''),
        ('ovirt-shell:input_format', enum('xml'), 'xml'),
        ('ovirt-shell:output_format', enum('xml', 'text'), 'text'),
        ('ovirt-shell:wide', boolean, False),
        ('ovirt-shell:header', boolean, True),
        ('ovirt-shell:fields', str, None),
        ('ovirt-shell:fields.*', str, None),
        ('ovirt-shell:ps1.connected', str, '(oVirt %(version)s) > '),
        ('ovirt-shell:ps1.disconnected', str, '(disconnected) > ')
    ]
