# -*- coding: utf-8 -*-
#
# <GitGraph - Git-powered graph database library>
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
from datetime import datetime
from mock import patch
from gitgraph.util import generate_uuid
from gitgraph.util import serialize_commit


@patch('gitgraph.util.uuid4')
def test_generate_uuid(uuid4):
    ('generate_uuid() should a hex string')
    uuid4.return_value.hex = 'deadbeefdeadbeef'
    generate_uuid().should.equal('deadbeefdeadbeef')


class stub_commit:
    commit_time = '1502686111.704968'
    message = 'testing serialize commit'

    class author:
        name = 'Author Name'
        email = 'author@name'

    class committer:
        name = 'Committer Name'
        email = 'committer@name'


def test_serialize_commit():
    ('serialize_commit() should return a dictionary')

    data = serialize_commit(stub_commit())
    data.should.equal({
        'author': {
            'email': 'author@name',
            'name': 'Author Name'
        },
        'committer': {
            'email': 'committer@name',
            'name': 'Committer Name'
        },
        'date': datetime(2017, 8, 14, 4, 48, 31, 704968),
        'message': 'testing serialize commit'})
