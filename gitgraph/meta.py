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
from collections import OrderedDict
from gitgraph.exceptions import InvalidSubjectDefinition


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


class MetaSubject(type):
    def __init__(cls, name, bases, members):
        indexes = set()

        if name not in ('MetaSubject', 'Subject') and cls.__module__ != __name__:
            SUBJECTS[name] = cls
            SUBJECTS_BY_CLASS[cls] = name
            indexes = validate_subject_definition(name, cls, members)

        fields = {'uuid'}.union(indexes)
        cls.__fields__ = fields
        cls.__data__ = {}
        super(MetaSubject, cls).__init__(name, bases, members)
