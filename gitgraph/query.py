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

import re


is_dict = lambda item: isinstance(item, dict)


class Query(object):
    def __init__(self, *args, **kw):
        self.regex_mode = False
        self.construct(*args, **kw)

    @property
    def regex(self):
        self.regex_mode = True
        return self


class predicate(Query):
    """creates matchers for predicates of subjects
    """

    def construct(self, name):
        self.name = name

    def matches(self, pattern, *args, **kw):
        """ matches by string value or regex

        ::

            >>> from re import IGNORECASE
            >>> from gitgraph.query import predicate
            >>>
            >>> query = predicate('email').regex.matches('@gmail.com', IGNORECASE)
        """
        if self.regex_mode:
            regex = re.compile(pattern, *args, **kw)
            return lambda value: bool(regex.search(unicode(self.get_value(value))))
        else:
            return lambda value: self.get_value(value) == pattern

    def get_value(self, value):
        return is_dict(value) and value[self.name] or value

    def contains(self, member):
        """match if the given member is inside of a predicate value

        ::

            >>> from re import IGNORECASE
            >>> from gitgraph.query import predicate
            >>>
            >>> query1 = predicate('email').contains('@gmail.com')
            >>>
            >>> query2 = predicate('email').regex.matches('@(g|hot|yahoo)mail.com$', IGNORECASE)
        """
        return lambda value: member in self.get_value(value)
