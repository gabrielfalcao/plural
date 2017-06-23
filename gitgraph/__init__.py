# -*- coding: utf-8 -*-
import os
import json
import socket
import pygit2
from hashlib import sha256
from uuid import uuid4

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


class GitGraphStore(object):
    def __init__(self, path=None, bare=False, author_name='hexastore', author_email='hexastore@git'):
        path = path or self.__class__.__name__.lower()
        self.path = path
        self.repository = init_repository(path, bare=bare)
        self.author = Signature(author_name, author_email)
        self.commiter = Signature(os.getlogin(), '@'.join([os.getlogin(), socket.gethostname()]))
        self.queries = []
        self.default_branch = 'refs/heads/master'

    def serialize(self, obj):
        return "\n".join([line.rstrip() for line in json.dumps(obj, sort_keys=True, indent=2).split('\n')])

    def deserialize(self, string):
        return json.loads(string)

    def add_spo(self, subject, predicate, data):
        blob_id = self.repository.create_blob(data)
        entry = IndexEntry(os.path.join(subject, predicate), blob_id, GIT_FILEMODE_BLOB)
        self.repository.index.add(entry)
        return blob_id

    def create(self, subject, **obj):
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
        for node in nodes:
            self.create(node.__class__.__name__, **node.to_dict())

    def merge(self, *nodes):
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
        subject_name = resolve_subject_name(subject_name)
        pattern = os.sep.join([subject_name, '_ids', uuid])
        for entry in self.glob(pattern):
            subject_blob_id = self.repository[entry.oid].data
            blob = self.repository[subject_blob_id]
            return Subject.from_data(subject_name, **self.deserialize(blob.data))


    def match_subjects_by_index(self, subject_name, field_name, match_callback):
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
        self.repository.reset(commit_id, GIT_RESET_HARD)
        return commit_id


SUBJECTS = OrderedDict()
SUBJECTS_BY_CLASS = OrderedDict()


def subject_has_index(name, key):
    if name not in SUBJECTS:
        return False

    subject = SUBJECTS[name]
    return subject.indexes.intersection({key})


class MetaSubject(type):
    def __init__(cls, name, bases, members):
        if name not in ('MetaSubject', 'Subject') and cls.__module__ != __name__:
            SUBJECTS[name] = cls
            SUBJECTS_BY_CLASS[cls] = name

        super(MetaSubject, cls).__init__(name, bases, members)


class Node(object):
    def __init__(self, uuid=None, **kw):
        self.uuid = kw.get('uuid', uuid)
        self.__data__ = kw
        self.__data__['uuid'] = uuid

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
    def from_data(cls, name, **kw):
        Definition = cls.definition(name)
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
        return isinstance(other, Subject) and self.to_dict() == other.to_dict()


class GitGraph(GitGraphStore):
    pass
