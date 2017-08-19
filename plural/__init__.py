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

from plural.models.edges import resolve_edge_name
from plural.models.edges import resolve_edge
from plural.store import serialize_commit
from plural.store import PluralStore
from plural.models.edges import Edge
from plural.models.vertices import Vertex
from plural.models.vertices import IncomingVertex
from plural.models.vertices import OutgoingVertex
from plural.models.vertices import IndirectVertex
from plural.models.meta.vertices import incoming_vertex
from plural.models.meta.vertices import outgoing_vertex
from plural.models.meta.vertices import indirect_vertex
from plural.exceptions import EdgeDefinitionNotFound
from plural.exceptions import InvalidEdgeDefinition


class Plural(PluralStore):
    pass


__all__ = (
    'resolve_edge',
    'resolve_edge_name',
    'serialize_commit',
    'PluralStore',
    'Plural',
    'Edge',
    'Vertex',
    'IncomingVertex',
    'OutgoingVertex',
    'IndirectVertex',
    'incoming_vertex',
    'outgoing_vertex',
    'indirect_vertex',
    'EdgeDefinitionNotFound',
    'InvalidEdgeDefinition',
)
