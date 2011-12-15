
from cli.settings import Settings, enum, boolean


class OvirtCliSettings(Settings):

    settings = Settings.settings + [
        ('osh:url', str, ''),
        ('osh:username', str, ''),
        ('osh:password', str, ''),
        ('osh:input_format', enum('xml'), 'xml'),
        ('osh:output_format', enum('xml', 'text'), 'text'),
        ('osh:wide', boolean, False),
        ('osh:header', boolean, True),
        ('osh:fields', str, None),
        ('osh:fields.*', str, None),
        ('osh:ps1.connected', str, '(oVirt %(version)s) > '),
        ('osh:ps1.disconnected', str, '(disconnected) > ')
    ]
