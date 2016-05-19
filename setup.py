
import os
import sys

from distutils.command.build import build
from distutils.command.build_py import build_py
from setuptools import setup, Command


version_info = {
    'name': 'ovirt-shell',
    'version': '3.6.2.1',
    'description': 'A command-line interface to oVirt Virtualization',
    'author': 'Michael Pasternak',
    'author_email': 'mpastern@redhat.com',
    'url': 'http://www.ovirt.org/wiki/CLI',
    'license': 'ASL2',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4' ],
}

class custom_build_py(build_py):
    """
    This custom build implementation is needed in order to generate
    the parsing and lexing tables used by ply during buildtime, so
    that it won't attempt to generate them during runtime.
    """
    def run(self):
        build_py.run(self)
        if not self.dry_run:
            self.generate_parsing_tables()

    def generate_parsing_tables(self):
        """
        Generates the parsing tables used by ply.
        """
        print("generating parsing tables")
        old_path = sys.path
        try:
            sys.path = [self.build_lib] + sys.path
            import cli.parser
            parser = cli.parser.Parser()
            parser._write_tables()
        finally:
            sys.path = old_path

setup(
    package_dir={ '': 'src' },
    packages=[ 'ovirtcli', 'ovirtcli.command', 'ovirtcli.format',
                 'ovirtcli.platform', 'ovirtcli.platform.posix',
                 'ovirtcli.platform.windows', 'ovirtcli.shell', 'ovirtcli.utils', 'cli',
                 'cli.command', 'cli.platform', 'cli.platform.posix', 'ovirtcli.infrastructure',
                 'ovirtcli.annotations', 'ovirtcli.events', 'ovirtcli.listeners', 'ovirtcli.meta',
                 'ovirtcli.state'],
    install_requires=[ 'ovirt-engine-sdk-python >= 3.6.2.0', 'ply >= 3.3', 'kitchen >= 1' ],
    entry_points={ 'console_scripts': [ 'ovirt-shell = ovirtcli.main:main' ] },
    cmdclass={
        "build_py": custom_build_py,
    },
    **version_info
)
