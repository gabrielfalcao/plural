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

import os
import json
import pygit2
from fnmatch import fnmatch

from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import GIT_RESET_HARD
from pygit2 import init_repository
from pygit2 import IndexEntry
from pygit2 import Signature
from gitgraph.meta import subject_has_index
from gitgraph.models import Subject
from gitgraph.models import resolve_subject_name
from gitgraph.util import generate_uuid
from gitgraph.util import serialize_commit


class GitGraphStore(object):
    """Data store that manipulates a single git repository

    :param path: ``bytes`` - the path to the git repository ``string``
    :param bare: ``bool`` - manipulate git objects only
    :param author_name: ``unicode`` - the name of the default git author, when not provided defaults to ``"hexastore"``
    :param author_email: ``unicode`` - the email of the default git author, when not provided defaults to ``"hexastore@git"``
    """
    def __init__(self, path=None, bare=False,
                 author_name='hexastore',
                 author_email='hexastore@git',
                 default_branch='refs/heads/master',
                 repository=None):
        path = path or self.__class__.__name__.lower()
        self.path = path
        self.bare = bare
        self.repository = repository or init_repository(path, bare=bare)
        self.author = Signature(author_name, author_email)
        self.commiter = Signature(author_name, author_email)
        self.queries = []
        self.default_branch = default_branch

    def add_remote(self, name, url):
        """adds a remote repository

        :param name: ``bytes``
        :param url: ``bytes``
        """
        self.repository.remotes.create(name, url)

    def serialize(self, obj):
        """serializes an object, meant for internal use only.

        :param obj: a hashable object
        :return: ``string``
        """
        return "\n".join([line.rstrip() for line in json.dumps(obj, sort_keys=True, indent=2).split('\n')])

    def deserialize(self, string):
        """deserialize a string into an object, meant for internal use only.

        :param string: a hashable object
        :return: ``a hashable object``
        """
        return json.loads(string)

    def iter_versions(self, branch='master'):
        """iterates over all the commits of the repo
        :param branch: the branch name
        :return: an iterator of dictionaries with commit metadata
        """
        for commit in self.repository.walk(self.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
            yield serialize_commit(commit)

    def get_versions(self, branch='master'):
        """same :py:meth:`as iter_versions` but returns a list
        :return: a list
        """
        results = list(self.iter_versions(branch))
        return results

    def add_spo(self, subject, predicate, data):
        """creates a staged entry of subject, predicate and object

        :param subject:
        :param predicate:
        :param data:
        :return: ``bytes`` - the blob id
        """
        subject = resolve_subject_name(subject)
        blob_id = self.repository.create_blob(data)
        entry = IndexEntry(os.path.join(subject, predicate), blob_id, GIT_FILEMODE_BLOB)
        self.repository.index.add(entry)
        return blob_id

    def create(self, subject, **obj):
        """creates a staged subject entry including its indexed fields.

        :param subject: a string or a :py:class:`Subject` subclass reference
        :param ``**kw``: the field values
        :return: an instance of the given subject

        """
        predicate_ids = []

        subject = resolve_subject_name(subject)
        subject_uuid = obj.pop('uuid', generate_uuid())
        obj['uuid'] = subject_uuid

        subject_data = self.serialize(obj)
        object_hash = bytes(pygit2.hash(subject_data))
        object_path = os.path.join(subject, 'objects')

        id_path = os.path.join(subject, '_ids')
        uuid_path = os.path.join(subject, '_uuids')

        indexes = {}
        for key in obj.keys():
            value = obj.get(key, None)
            if subject_has_index(subject, key):
                indexes[key] = value

            predicate_path = os.path.join(subject, 'indexes', key)
            predicate_ids.append(self.add_spo(predicate_path, object_hash, value))

        self.add_spo(object_path, object_hash, subject_data)
        self.add_spo(id_path, subject_uuid, object_hash)
        self.add_spo(uuid_path, object_hash, subject_uuid)

        self.queries.append(
            ' '.join(map(bytes, ['CREATE', subject, subject_uuid]))
        )
        return Subject.from_data(subject, **obj)

    def save_nodes(self, *nodes):
        """creates staged entries for all the given subject nodes, regardless of type

        :param ``*nodes``: a list of subject instances
        """

        result = []
        for node in nodes:
            n = self.create(node.__class__.__name__, **node.to_dict())
            result.append(n)

        return result

    def merge(self, *nodes):
        """saves and commits all given nodes

        :param ``*nodes``: a list of subject instances
        """
        result = self.save_nodes(*nodes)
        self.commit()
        return result

    def trace_path(self, entries):
        return map(lambda entry: (entry.path, bytes(entry.oid)), entries)

    def glob(self, pattern, treeish=None):
        treeish = treeish or self.repository.index
        return filter(lambda entry: fnmatch(entry.path, pattern), treeish)

    def scan_all(self, subject_name=None, treeish=None):
        subject_name = resolve_subject_name(subject_name)
        treeish = treeish or self.repository.index
        pattern = os.path.join(subject_name, 'objects', '*')
        for entry in self.glob(pattern):
            blob = self.repository[entry.oid]
            data = self.deserialize(blob.data)
            yield Subject.from_data(subject_name, **data)

    def delete(self, *nodes):
        for node in nodes:
            for path, oid in self.trace_path(self.glob('*{}*'.format(node.uuid))):
                map(self.repository.index.remove, node.get_related_blob_paths(self.repository))
                self.queries.append(
                    ' '.join(map(bytes, ['DELETE', node]))
                )

    def get_subject_by_uuid(self, subject_name, uuid):
        """retrieves a subject by id

        :param subject_name: the subject name or type
        :param uuid: the uuid value
        """
        subject_name = resolve_subject_name(subject_name)
        pattern = os.sep.join([subject_name, '_ids', uuid])
        for entry in self.glob(pattern):
            subject_blob_id = self.repository[entry.oid].data
            blob = self.repository[subject_blob_id]
            return Subject.from_data(subject_name, **self.deserialize(blob.data))

    def match_subjects_by_index(self, subject_name, field_name, match_callback):
        """retrieves multiple subjects by indexed field

        :param subject_name: the subject name or type
        :param uuid: the uuid value
        """
        subject_name = resolve_subject_name(subject_name)
        pattern = os.sep.join([subject_name or '*', 'indexes', '*'])
        # for index, oid in filter(lambda (index, oid): field_name in index, self.glob(pattern)):
        for index, oid in self.trace_path(self.glob(pattern)):
            path, blob_id = os.path.split(index)
            subject_name = path.split(os.sep)[0]
            value = self.repository[oid].data
            if match_callback(value):
                blob = self.repository[blob_id]
                data = self.deserialize(blob.data)
                Definition = Subject.definition(subject_name)
                yield Definition(**data)

    def commit(self, query=None):
        """creates a commit with the staged objects"""
        author = None

        if not query:
            query = '\n'.join(sorted(set(self.queries)))

        # commit
        tree_id = self.repository.index.write_tree()
        parent_commits = []
        if self.repository.references.objects:
            parent_commits = [self.repository.head.target]

        commit_id = self.repository.create_commit(
            self.default_branch,
            author or self.author,
            self.commiter,
            query,
            tree_id,
            parent_commits,
        )
        self.queries = []
        self.repository.head.set_target(commit_id)
        if not self.bare:
            self.repository.reset(commit_id, GIT_RESET_HARD)
        return commit_id
