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

from gitgraph.models import resolve_subject_name
from gitgraph.models import resolve_subject
from gitgraph.store import serialize_commit
from gitgraph.store import GitGraphStore
from gitgraph.models import Subject
from gitgraph.exceptions import SubjectDefinitionNotFound
from gitgraph.exceptions import InvalidSubjectDefinition


class GitGraph(GitGraphStore):
    pass


__all__ = (
    'resolve_subject',
    'resolve_subject_name',
    'serialize_commit',
    'GitGraphStore',
    'GitGraph',
    'Subject',
    'SubjectDefinitionNotFound',
    'InvalidSubjectDefinition',
)
