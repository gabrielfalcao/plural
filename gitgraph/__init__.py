# -*- coding: utf-8 -*-
#
# <GitGraph - Git-powered library>
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
import socket
import pygit2
from hashlib import sha256
from uuid import uuid4
from datetime import datetime
from fnmatch import fnmatch
from collections import OrderedDict

from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import GIT_RESET_HARD
from pygit2 import init_repository
from pygit2 import IndexEntry
from pygit2 import Signature


def resolve_subject_name(subj):
    if isinstance(subj, type) and issubclass(subj, Subject):
        return subj.__name__
    elif subj is None:
        return '*'
    elif isinstance(subj, basestring):
        return subj
    else:
        msg = (
            'resolve_subject_name() takes a Subject subclass, '
            'a string or None. Got {}'
        )
        raise TypeError(msg.format(repr(subj)))


def resolve_subject(subj):
    if isinstance(subj, type) and issubclass(subj, Subject):
        return subj.__name__
    elif isinstance(subj, basestring):
        return subj
    else:
        msg = (
            'resolve_subject() takes a Subject subclass or '
            'a string. Got {}'
        )
        raise TypeError(msg.format(repr(subj)))


def serialize_commit(commit):
    data = {
        'author': {
            'name': commit.author.name,
            'email': commit.author.email,
        },
        'committer': {
            'name': commit.committer.name,
            'email': commit.committer.email,
        },
        'message': commit.message,
        'date': datetime.utcfromtimestamp(commit.commit_time),
    }
    return data


class GitGraphStore(object):
    """Data store that manipulates a single git repository

    :param path: ``bytes`` - the path to the git repository ``string``
    :param bare: ``bool`` - manipulate git objects only
    :param author_name: ``unicode`` - the name of the default git author, when not provided defaults to ``"hexastore"``
    :param author_email: ``unicode`` - the email of the default git author, when not provided defaults to ``"hexastore@git"``
    """
    def __init__(self, path=None, bare=False, author_name='hexastore', author_email='hexastore@git'):
        path = path or self.__class__.__name__.lower()
        self.path = path
        self.bare = bare
        self.repository = init_repository(path, bare=bare)
        self.author = Signature(author_name, author_email)
        self.commiter = Signature(author_name, author_email)
        self.queries = []
        self.default_branch = 'refs/heads/master'

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
        subject = resolve_subject(subject)
        subject_uuid = obj.get('uuid', uuid4().hex)

        subject_data = self.serialize(obj)
        object_hash = bytes(pygit2.hash(subject_data))
        self.add_spo(os.path.join(subject, 'objects'), object_hash, subject_data)

        predicate_ids = []

        self.add_spo(os.path.join(subject, '_ids'), subject_uuid, object_hash)
        self.add_spo(os.path.join(subject, '_uuids'), object_hash, subject_uuid)

        indexes = {}
        for key in obj.keys():
            value = obj[key]
            if subject_has_index(subject, key):
                indexes[key] = value

            predicate_ids.append(self.add_spo(os.path.join(subject, 'indexes', key), object_hash, value))

        node = Subject.from_data(subject, **obj)

        self.queries.append(
            ' '.join(map(bytes, ['CREATE', node]))
        )
        return node

    def save_nodes(self, *nodes):
        """creates staged entries for all the given subject nodes, regardless of type

        :param ``*nodes``: a list of subject instances
        """

        for node in nodes:
            self.create(node.__class__.__name__, **node.to_dict())

    def merge(self, *nodes):
        """saves and commits all given nodes

        :param ``*nodes``: a list of subject instances
        """
        self.save_nodes(*nodes)
        self.commit()

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


SUBJECTS = OrderedDict()
SUBJECTS_BY_CLASS = OrderedDict()


class InvalidSubjectDefinition(Exception):
    pass


def subject_has_index(name, key):
    if name not in SUBJECTS:
        return False

    subject = SUBJECTS[name]
    return subject.indexes.intersection({key})


def get_attribute_from_meta_child(attribute, cls, members):
    return getattr(cls, attribute, members.get(attribute))


def validate_subject_definition(name, cls, members):
    indexes = get_attribute_from_meta_child('indexes', cls, members)
    if not indexes:
        raise InvalidSubjectDefinition('the {} definition should have at least one index'.format(cls))
    # if not isinstance(indexes, (set, list, tuple)):
    #     raise InvalidSubjectDefinition('')


class MetaSubject(type):
    def __init__(cls, name, bases, members):
        if name not in ('MetaSubject', 'Subject') and cls.__module__ != __name__:
            SUBJECTS[name] = cls
            SUBJECTS_BY_CLASS[cls] = name
            validate_subject_definition(name, cls, members)

        super(MetaSubject, cls).__init__(name, bases, members)


class Node(object):
    def __init__(self, uuid=None, **kw):
        self.uuid = kw.get('uuid', uuid)
        self.__data__ = kw
        self.__data__['uuid'] = uuid

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __getitem__(self, key):
        return self.__data__[key]

    def to_dict(self):
        return self.__data__.copy()

    def to_json(self, **kw):
        return json.dumps(self.to_dict(), **kw)


class SubjectDefinitionNotFound(Exception):
    pass


class Subject(Node):
    __metaclass__ = MetaSubject

    @classmethod
    def definition(cls, name):
        try:
            return SUBJECTS[name]
        except KeyError:
            raise SubjectDefinitionNotFound('there are no subject subclass defined with the name "{}"'.format(name))

    @classmethod
    def from_data(cls, ___name___, **kw):
        Definition = cls.definition(___name___)
        return Definition(**kw)

    def get_related_blob_paths(self, repository):
        subject_name = self.__class__.__name__
        uuid = self.uuid
        blob_id_path = '{subject_name}/_ids/{uuid}'.format(**locals())
        blob_id = repository[repository.index[blob_id_path].oid].data
        context = {
            'subject_name': subject_name,
            'blob_id': blob_id,
            'uuid': uuid,
        }
        paths = [
            '{subject_name}/_ids/{uuid}',
            '{subject_name}/_uuids/{blob_id}',
            '{subject_name}/indexes/uuid/{blob_id}',
            '{subject_name}/objects/{blob_id}',
        ]
        for predicate in self.indexes:
            context['predicate'] = predicate
            paths.append('{subject_name}/indexes/{predicate}/{blob_id}'.format(**context))

        return map(lambda path: path.format(**context), paths)

    def __hash__(self):
        return int(sha256(self.to_json()).hexdigest(), 16)

    def __str__(self):
        return ''.join([self.__class__.__name__, self.to_json()])

    def __repr__(self):
        return bytes(self)

    def __eq__(self, other):
        return isinstance(other, Node) and self.to_dict() == other.to_dict()


class GitGraph(GitGraphStore):
    pass
