# -*- coding: utf-8 -*-
#
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
import json
from hashlib import sha256
from plural.meta import MetaSubject
from plural.meta import Node
from plural.meta import SUBJECTS
from plural.util import generate_uuid

from plural.exceptions import SubjectDefinitionNotFound


def resolve_subject_name(subj):
    """
    :param subj: an :py:class:`Subject` instance or string
    :returns: a string
    """
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
    """
    :param subj: an :py:class:`Subject` instance or string
    :returns: a :py:class:`Subject` subclass
    """
    if isinstance(subj, type) and issubclass(subj, Subject):
        return subj
    elif isinstance(subj, basestring):
        return SUBJECTS[subj]
    else:
        msg = (
            'resolve_subject() takes a Subject subclass or '
            'a string. Got {}'
        )
        raise TypeError(msg.format(repr(subj)))


class Subject(Node):
    """represents a node type (or "model", if you will)."""
    __metaclass__ = MetaSubject
    def __init__(self, uuid=None, **kw):
        self.uuid = kw.get('uuid', uuid)
        self.__data__ = dict([(k, self.decode_field(k, v)) for k, v in kw.items()])
        self.__data__['uuid'] = uuid or generate_uuid()

    def __setitem__(self, key, value):
        self.__data__[key] = self.encode_field(key, value)

    def __contains__(self, key):
        return key in self.__data__

    def __getitem__(self, key):
        value = self.__data__[key]
        return self.decode_field(key, value)

    def __setattr__(self, key, value):
        if key in self.__fields__:
            self.__data__[key] = self.encode_field(key, value)
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        if key.startswith('__'):
            return super(Node, self).__getattribute__(key)

        if key not in self.__data__:
            raise AttributeError('key not found: {}'.format(key))

        value = self.__data__[key]
        return self.decode_field(key, value)

    def to_dict(self):
        return dict([(k, self.encode_field(k, v)) for k, v in self.__data__.items()])

    def to_json(self, **kw):
        return json.dumps(self.to_dict(), **kw)

    def decode_field(self, name, value):
        codec = self.__codecs__.get(name)
        if not codec:
            return value

        return codec.decode(value)

    def encode_field(self, name, value):
        codec = self.__codecs__.get(name)
        if not codec:
            return value or ''

        return codec.encode(value)

    @staticmethod
    def definition(name):
        """
        resolves a :py:class:`Subject` by its type name

        :param name: a dictionary
        :returns: the given :py:class:`Subject` subclass
        """
        try:
            return resolve_subject(name)
        except KeyError:
            raise SubjectDefinitionNotFound('there are no subject subclass defined with the name "{}"'.format(name))

    @classmethod
    def from_data(cls, ___name___=None, **kw):
        """
        creates a new instance of the given :py:class:`Subject` with the provided ``**kwargs``

        :param ___name___: the name of the subject type
        :param ``**kw``: a dictionary
        :returns: an instance of the given :py:class:`Subject` subclass
        """
        name = ___name___ or cls.__name__
        Definition = cls.definition(name)
        return Definition(**kw)

    @classmethod
    def from_dict(Definition, data):
        """
        creates a new instance of the given :py:class:`Subject` with the provided ``data``

        :param data: a dictionary
        :returns: an instance of the given :py:class:`Subject` subclass
        """
        return Definition(**data)

    def get_related_blob_paths(self, repository):
        """
        returns a list of all possible blob paths of a subject instance.

        :param repository: a ``pygit2.Repository``
        :returns: the given :py:class:`Subject` subclass
        """
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
