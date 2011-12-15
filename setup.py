
import os
import sys

from distutils.command.build import build
from setuptools import setup, Command


version_info = {
    'name': 'ovirt-shell',
    'version': '1.0-SNAPSHOT',
    'description': 'A command-line interface to oVirt'
                   ' Virtualization',
    'author': 'Unknown',
    'author_email': 'engine-devel@ovirt.org',
    'url': 'www.ovirt.org',
    'license': 'ASL2',
    'classifiers': [
        'Development Status :: 1 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: ASL2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7' ],
}


setup(
    package_dir={ '': 'src' },
    packages=[ 'ovirtcli', 'ovirtcli.command', 'ovirtcli.format',
                 'ovirtcli.platform', 'ovirtcli.platform.posix',
                 'ovirtcli.platform.windows' ],
    install_requires=[ 'ovirt-engine-sdk >= 0.1', 'pexpect <= 2.3' ],
    entry_points={ 'console_scripts': [ 'ovirt-shell = ovirtcli.main:main' ] },
    **version_info
)
