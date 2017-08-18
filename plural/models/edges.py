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
from plural.meta import MetaSubject
from plural.meta import SUBJECTS
from plural.models.element import Element

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


class Subject(Element):
    """represents a node type (or "model", if you will)."""
    __metaclass__ = MetaSubject

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

    def get_related_blob_paths(self, repository):
        """
        returns a list of all possible blob paths of a :py:class:`Subject` instance.

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
