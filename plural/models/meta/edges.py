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

from collections import defaultdict
from collections import OrderedDict
from plural.models.element import Element
from plural.exceptions import InvalidSubjectDefinition


SUBJECTS = OrderedDict()
SUBJECTS_BY_CLASS = OrderedDict()
SUBJECT_VERTEXES = defaultdict(OrderedDict)


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


class Vertex(object):
    def __init__(self, target, attributes, reverse_label=None):
        self.origin = None
        self.target = target
        self.codecs = attributes
        self.reverse_label = None

    def attach_origin(self, origin):
        self.origin = origin
        SUBJECT_VERTEXES[self.origin][self.direction] = self
        if not self.reverse_label:
            origin_name = origin.__name__.lower()
            self.reverse_label = "{}s".format(origin_name)

    def is_attached(self):
        return is_node_subclass(self.origin)


class IncomingVertex(Vertex):
    """represents a vertex coming from the origin into the target
    (O)-[v]->(T)
    """
    direction = 'incoming'


class OutgoingVertex(Vertex):
    """represents a vertex going out the target into the origin
    (O)<-[v]-(T)

    """
    direction = 'outgoing'


class IndirectVertex(Vertex):
    """represents a vertex that connects two edges without direction
    (O)-[v]-(T)
    """
    direction = 'indirect'


class VertexFactory(object):
    def __init__(self, subject):
        self.target = subject

    def incoming(self, attributes=None, reverse_label=None):
        return IncomingVertex(self.target, attributes=dict(attributes or {}), reverse_label=reverse_label)

    def outgoing(self, attributes=None, reverse_label=None):
        return OutgoingVertex(self.target, attributes=dict(attributes or {}), reverse_label=reverse_label)


def is_node_subclass(cls):
    return isinstance(cls, type) and issubclass(cls, Element) and cls is not Element and not cls.__module__.startswith('plural.')


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
        cls.v = VertexFactory(cls)
        cls.__fields__ = {'uuid'}.union(fields)
        cls.__data__ = {}
        cls.__codecs__ = dict([(n, Codec()) for n, Codec in codecs.items()])
        super(MetaSubject, cls).__init__(name, bases, members)
