#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import io
import os
import subprocess
import sys
import unittest
from setuptools import find_packages, setup, Command

# conditionally import to allow setup.py install introduce requirements
try:
    from sphinx.setup_command import BuildDoc
except ImportError:
    BuildDoc = None


# Fixed Package meta-data.
NAME = 'pyodv'
DESCRIPTION = 'Python package for reading ODV (Ocean Data Variables) files'
URL = 'https://vliz-be-opsci.github.io/pyodv'
EMAIL = 'rory.meyer@vliz.be'
AUTHOR = 'Rory Meyer'
LICENSE = 'MIT'
CONSOLE_SCRIPTS = ['pyodv = pyodv.__main__:main']
TROVE_CLASSES = [
    # Trove classifiers
    # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.8',
]
TEST_FOLDER = 'tests'
TEST_PATTERN = 'test_*.py'

# Dynamic Packge meta-data  - read from different local files
here = os.path.abspath(os.path.dirname(__file__))
# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


def required(sfx=''):
    """ Load the requirements from the requirements.txt file"""
    reqs = []
    try:
        with open(f"requirements{sfx}.txt") as f:
            reqs = [ln.strip() for ln in f.readlines() if not ln.startswith('-') and not ln.startswith('#') and ln.strip() != '']
    finally:
        return reqs


requirements = required()
requirements_dev = required('-dev')

# Load the package's __version__.py module as a dictionary.
about = {}
with io.open(os.path.join(here, NAME, '__version__.py')) as f:
    exec(f.read(), about)


# define specific setup commands
class CommandBase(Command):
    """"AbstractBase for our own commands"""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))


class TestCommand(CommandBase):
    """"Support setup.py test"""
    description = 'Perform the tests'

    def run(self):
        self.status('Discovering tests with pattern %s in folder %s' % (TEST_PATTERN, TEST_FOLDER))
        suite = unittest.TestLoader().discover(TEST_FOLDER, pattern=TEST_PATTERN)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        exit(0 if result.wasSuccessful() else 1)


class ReleaseCommand(CommandBase):
    """Support setup.py release."""
    description = 'Tag the package.'

    def run(self):
        self.version_tag = 'v' + about['__version__']
        self.status('Commiting this build...')
        os.system('git commit -am "Setup.py commit for version {0}" '.format(self.version_tag))

        self.status('Tagging this build with {0}'.format(self.version_tag))
        try:
            subprocess.run(['git', 'tag', self.version_tag], check=True)
            self.status('Git push')
            os.system('git push --tags')
        except subprocess.CalledProcessError:
            self.status('Rolling back last commit...')
            os.system('git reset --soft HEAD~1')
            # Delete old tag. This is not safe, needs to be done when pushing a new version only...
            # os.system('git tag -d {0}'.format(self.version_tag))
        sys.exit()


commands = {'release': ReleaseCommand, 'test': TestCommand}


# Conditionally add the BuildDoc command (if sphinx is available)
cmd_opts = dict()
if BuildDoc is not None:
    commands['build_sphinx'] = BuildDoc
    cmd_opts['build_sphinx'] = {
        'project': ('setup.py', NAME),
        'version': ('setup.py', about['__version__']),
        'release': ('setup.py', about['__version__']),
        'source_dir': ('setup.py', 'docs'),
    }


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    test_suite=TEST_FOLDER,
    packages=find_packages(exclude=('tests',)),
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],
    entry_points={
         'console_scripts': CONSOLE_SCRIPTS,
    },
    install_requires=requirements,
    extras_require={'dev': requirements_dev},
    include_package_data=True,
    license=LICENSE,
    classifiers=TROVE_CLASSES,
    cmdclass=commands,
    command_options=cmd_opts,
)
