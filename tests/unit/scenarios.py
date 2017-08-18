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
import json
import hashlib
from mock import patch
from sure import scenario

from gitgraph.store import GitGraphStore


def with_graph_store(*args, **kw):

    @patch('gitgraph.store.Signature')
    @patch('gitgraph.store.init_repository')
    def setup(context, init_repository, Signature):
        context.store = GitGraphStore(*args, **kw)
        context.init_repository = init_repository
        context.Signature = Signature

    return scenario(setup)


class BlobStub(object):

    def __init__(self, data):
        self.data = data

    @property
    def oid(self):
        return hashlib.sha1(self.data).hexdigest()


class RepositoryStub(object):
    def __init__(self, list_of_dicts):
        self.list_of_dicts = list_of_dicts
        self.index = dict([(b.oid, b) for b in map(BlobStub, map(json.dumps, list_of_dicts))])
