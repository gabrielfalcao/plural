# -*- coding: utf-8 -*-
import re


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
            return lambda value: bool(regex.search(unicode(value)))
        else:
            return lambda value: value == pattern

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
        return lambda value: member in value
