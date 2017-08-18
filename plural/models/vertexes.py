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
from plural.meta import MetaVertex
from plural.meta import VERTEXES
from plural.models.element import Element

from plural.exceptions import VertexDefinitionNotFound


def resolve_vertex_name(subj):
    """
    :param subj: an :py:class:`Vertex` instance or string
    :returns: a string
    """
    if isinstance(subj, type) and issubclass(subj, Vertex):
        return subj.__name__
    elif subj is None:
        return '*'
    elif isinstance(subj, basestring):
        return subj
    else:
        msg = (
            'resolve_vertex_name() takes a Vertex subclass, '
            'a string or None. Got {}'
        )
        raise TypeError(msg.format(repr(subj)))


def resolve_vertex(subj):
    """
    :param subj: an :py:class:`Vertex` instance or string
    :returns: a :py:class:`Vertex` subclass
    """
    if isinstance(subj, type) and issubclass(subj, Vertex):
        return subj
    elif isinstance(subj, basestring):
        return VERTEXES[subj]
    else:
        msg = (
            'resolve_vertex() takes a Vertex subclass or '
            'a string. Got {}'
        )
        raise TypeError(msg.format(repr(subj)))


class Vertex(Element):
    """represents a node type (or "model", if you will)."""
    __metaclass__ = MetaVertex

    @staticmethod
    def definition(name):
        """
        resolves a :py:class:`Vertex` by its type name

        :param name: a dictionary
        :returns: the given :py:class:`Vertex` subclass
        """
        try:
            return resolve_vertex(name)
        except KeyError:
            raise VertexDefinitionNotFound('there are no vertex subclass defined with the name "{}"'.format(name))

    def get_related_blob_paths(self, repository):
        """
        returns a list of all possible blob paths of a :py:class:`Vertex` instance.

        :param repository: a ``pygit2.Repository``
        :returns: the given :py:class:`Vertex` subclass
        """
        vertex_name = self.__class__.__name__
        uuid = self.uuid
        blob_id_path = '{vertex_name}/_ids/{uuid}'.format(**locals())
        blob_id = repository[repository.index[blob_id_path].oid].data
        context = {
            'vertex_name': vertex_name,
            'blob_id': blob_id,
            'uuid': uuid,
        }
        paths = [
            '{vertex_name}/_ids/{uuid}',
            '{vertex_name}/_uuids/{blob_id}',
            '{vertex_name}/indexes/uuid/{blob_id}',
            '{vertex_name}/objects/{blob_id}',
        ]
        for predicate in self.indexes:
            context['predicate'] = predicate
            paths.append('{vertex_name}/indexes/{predicate}/{blob_id}'.format(**context))

        return map(lambda path: path.format(**context), paths)
