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
from collections import OrderedDict
from gitgraph.exceptions import InvalidSubjectDefinition
from gitgraph.util import generate_uuid


SUBJECTS = OrderedDict()
SUBJECTS_BY_CLASS = OrderedDict()


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
    if not isinstance(indexes, (set, list, tuple)):
        raise InvalidSubjectDefinition('the {} definition has an index property that is not a set, list or tuple: {}'.format(cls, type(indexes)))

    return indexes


class Node(object):
    """baseclass of Subject, exists solely for meta-programming purposes"""

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


def is_node_subclass(cls):
    return isinstance(cls, type) and issubclass(cls, Node) and cls is not Node and not cls.__module__.startswith('gitgraph.')


class MetaSubject(type):
    def __init__(cls, name, bases, members):
        indexes = set()
        codecs = {}

        if name not in ('MetaSubject', 'Subject') and cls.__module__ != __name__:
            SUBJECTS[name] = cls
            SUBJECTS_BY_CLASS[cls] = name
            indexes = validate_subject_definition(name, cls, members)

        fields = set(indexes)

        for parent in filter(is_node_subclass, bases):
            parent_indexes = getattr(parent, 'indexes', set())
            fields = fields.union(set(parent_indexes))

            parent_codecs = getattr(parent, 'fields', {})
            codecs.update(parent_codecs)

        codecs.update(getattr(cls, 'fields', {}))
        cls.indexes = fields
        cls.__fields__ = {'uuid'}.union(fields)
        cls.__data__ = {}
        cls.__codecs__ = dict([(n, Codec()) for n, Codec in codecs.items()])
        super(MetaSubject, cls).__init__(name, bases, members)
