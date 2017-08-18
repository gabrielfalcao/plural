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

from hashlib import sha256
from gitgraph.meta import MetaSubject
from gitgraph.meta import Node
from gitgraph.meta import SUBJECTS

from gitgraph.exceptions import SubjectDefinitionNotFound


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
    __metaclass__ = MetaSubject

    @classmethod
    def definition(cls, name):
        try:
            return resolve_subject(name)
        except KeyError:
            raise SubjectDefinitionNotFound('there are no subject subclass defined with the name "{}"'.format(name))

    @classmethod
    def from_data(cls, ___name___=None, **kw):
        name = ___name___ or cls.__name__
        Definition = cls.definition(name)
        return Definition(**kw)

    @classmethod
    def from_dict(Definition, data):
        return Definition(**data)

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
