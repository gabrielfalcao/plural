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

from collections import OrderedDict
from plural.exceptions import InvalidVertexDefinition


VERTEXES = OrderedDict()
VERTEXES_BY_CLASS = OrderedDict()


def vertex_has_index(name, key):
    if name not in VERTEXES:
        return False

    vertex = VERTEXES[name]
    return vertex.indexes.intersection({key})


def get_attribute_from_meta_child(attribute, cls, members):
    return getattr(cls, attribute, members.get(attribute))


def validate_vertex_definition(name, cls, members):
    indexes = get_attribute_from_meta_child('indexes', cls, members) or set()
    if not isinstance(indexes, (set, list, tuple)):
        raise InvalidVertexDefinition('the {} definition has an index property that is not a set, list or tuple: {}'.format(cls, type(indexes)))

    return indexes


def is_vertex_subclass(cls):
    return isinstance(cls, type) and issubclass(cls, MetaVertex.Target) and cls is not MetaVertex.Target and not cls.__module__.startswith('plural.')


class MetaVertex(type):
    def __init__(cls, name, bases, members):
        indexes = set()
        codecs = {}

        if name == 'Vertex':  # and cls.__module__.startswith('plural.models.vertexes'):
            MetaVertex.Target = cls
            super(MetaVertex, cls).__init__(name, bases, members)
            return

        if name == 'MetaVertex':  # and cls.__module__.startswith('plural.models.vertexes'):
            super(MetaVertex, cls).__init__(name, bases, members)
            return

        if name not in ('MetaVertex', 'Vertex') and not cls.__module__.startswith('plural.models.vertexes'):
            VERTEXES[name] = cls
            VERTEXES_BY_CLASS[cls] = name
            indexes = validate_vertex_definition(name, cls, members)

        fields = set(indexes)

        for parent in filter(is_vertex_subclass, bases):
            parent_indexes = getattr(parent, 'indexes', set())
            fields = fields.union(set(parent_indexes))

            parent_codecs = getattr(parent, 'fields', {})
            codecs.update(parent_codecs)

        codecs.update(getattr(cls, 'fields', {}))
        cls.indexes = fields
        cls.__fields__ = {'uuid'}.union(fields)
        cls.__data__ = {}
        cls.__codecs__ = dict([(n, Codec()) for n, Codec in codecs.items()])
        super(MetaVertex, cls).__init__(name, bases, members)


class VertexDefinition(object):
    def __init__(self, label, edge, through=None, fields=None):
        self._label = label
        self._origin = edge
        self._through = through
        self._fields = fields

    def through(self, edge):
        self._through = edge
        return self

    def with_fields(self, edge):
        self._fields = edge
        return self


class outgoing_vertex(VertexDefinition):
    """represents the declaration of an outgoing vertex"""
    direction = 'outgoing'


class incoming_vertex(VertexDefinition):
    """represents the declaration of an incoming vertex"""
    direction = 'incoming'


class indirect_vertex(VertexDefinition):
    """represents the declaration of an indirect vertex"""
    direction = 'indirect'


class VertexFactory(object):
    def __init__(self, edge):
        self.target = edge

    def incoming(self, *args, **kw):
        return incoming_vertex(*args, **kw)

    def outgoing(self, *args, **kw):
        return outgoing_vertex(*args, **kw)

    def indirect(self, *args, **kw):
        return indirect_vertex(*args, **kw)
