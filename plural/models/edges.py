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
from plural.models.meta.edges import MetaEdge
from plural.models.meta.edges import SUBJECTS
from plural.models.meta.edges import is_edge_subclass

from plural.models.element import Element

from plural.exceptions import EdgeDefinitionNotFound


def resolve_edge_name(edge):
    """
    :param edge: an :py:class:`Edge` instance or string
    :returns: a string
    """
    if isinstance(edge, Element):
        edge = edge.__class__

    if is_edge_subclass(edge):
        return edge.__name__
    elif edge is None:
        return '*'
    elif isinstance(edge, basestring):
        return edge
    else:
        msg = (
            'resolve_edge_name() takes a Edge subclass, '
            'a string or None. Got {}'
        )
        raise TypeError(msg.format(repr(edge)))


def resolve_edge(edge):
    """
    :param edge: an :py:class:`Edge` instance or string
    :returns: a :py:class:`Edge` subclass
    """
    if is_edge_subclass(edge):
        return edge
    elif isinstance(edge, basestring):
        return SUBJECTS[edge]
    else:
        msg = (
            'resolve_edge() takes a Edge subclass or '
            'a string. Got {}'
        )
        raise TypeError(msg.format(repr(edge)))


class Edge(Element):
    """represents a node type (or "model", if you will)."""
    __metaclass__ = MetaEdge

    @staticmethod
    def definition(name):
        """
        resolves a :py:class:`Edge` by its type name

        :param name: a dictionary
        :returns: the given :py:class:`Edge` subclass
        """
        try:
            return resolve_edge(name)
        except KeyError:
            raise EdgeDefinitionNotFound('there are no edge subclass defined with the name "{}"'.format(name))

    def get_related_blob_paths(self, repository):
        """
        returns a list of all possible blob paths of a :py:class:`Edge` instance.

        :param repository: a ``pygit2.Repository``
        :returns: the given :py:class:`Edge` subclass
        """
        edge_name = self.__class__.__name__
        uuid = self.uuid
        blob_id_path = '{edge_name}/_ids/{uuid}'.format(**locals())
        blob_id = repository[repository.index[blob_id_path].oid].data
        context = {
            'edge_name': edge_name,
            'blob_id': blob_id,
            'uuid': uuid,
        }
        paths = [
            '{edge_name}/_ids/{uuid}',
            '{edge_name}/_uuids/{blob_id}',
            '{edge_name}/indexes/uuid/{blob_id}',
            '{edge_name}/objects/{blob_id}',
        ]
        for predicate in self.indexes:
            context['predicate'] = predicate
            paths.append('{edge_name}/indexes/{predicate}/{blob_id}'.format(**context))

        return map(lambda path: path.format(**context), paths)

    @classmethod
    def from_data(cls, ___name___=None, **kw):
        """
        creates a new instance of the given :py:class:`Element` with the provided ``**kwargs``

        :param ___name___: the name of the element type
        :param ``**kw``: a dictionary
        :returns: an instance of the given :py:class:`Element` subclass
        """
        name = ___name___ or cls.__name__
        Definition = cls.definition(name)
        return Definition(**kw)

    @classmethod
    def from_dict(Definition, data):
        """
        creates a new instance of the given :py:class:`Element` with the provided ``data``

        :param data: a dictionary
        :returns: an instance of the given :py:class:`Element` subclass
        """
        return Definition(**data)
