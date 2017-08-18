# -*- coding: utf-8 -*-

# <Plural - Git-powered graph database library>
# Copyright (C) <2017>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ast
import os
import codecs

from setuptools import setup, find_packages

local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f)).read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('plural', 'version.py')))
    return finder.version


def local_file(*f):
    path = os.path.join(os.path.dirname(__file__), *f)
    return codecs.open(path, 'r', encoding='utf-8').read().encode('utf-8')


install_requires = list(filter(bool, map(bytes.strip, local_file('requirements.txt').splitlines())))


setup(
    name='plural',
    version=read_version(),
    entry_points={
        'console_scripts': [
        ],
    },
    description='',
    long_description=local_file('README.rst'),
    author=u'Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='https://github.com/gabrielfalcao/plural',
    packages=find_packages(exclude=['*tests*']),
    install_requires=install_requires,
    include_package_data=True,
    package_data={
        'plural': '*.txt *.png *.gif *.yml *.rst docs/source/*'.split(),
    },
    zip_safe=False,
)
