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
import re
from plural.query import predicate

LIST_OF_DICTS = [
    {"name": "Foo Bar"},
    {"name": "John Doe"},
    {"name": "Wee Woo"},
]

LIST_OF_VALUES = [
    "Foo Bar",
    "John Doe",
    "Wee Woo",
]


def test_query_contains_generates_lambda_filter_with_list_of_dicts():
    ('predicate("field").contains("string") with a list of dicts')

    query = predicate('name').contains('oo')
    result = list(filter(query, LIST_OF_DICTS))

    result.should.equal([
        {"name": "Foo Bar"},
        {"name": "Wee Woo"},
    ])


def test_query_contains_generates_lambda_filter_with_a_list_of_values():
    ('predicate("field").contains("string") with a list of values')

    query = predicate('name').contains('oo')
    result = list(filter(query, LIST_OF_VALUES))

    result.should.equal([
        "Foo Bar",
        "Wee Woo",
    ])


def test_query_matches_regex_generates_lambda_filter_with_list_of_dicts():
    ('predicate("field").matches("regex") with a list of dicts against regex')

    query = predicate('name').regex.matches('OO', re.IGNORECASE)
    result = list(filter(query, LIST_OF_DICTS))

    result.should.equal([
        {"name": "Foo Bar"},
        {"name": "Wee Woo"},
    ])


def test_query_matches_regex_generates_lambda_filter_with_a_list_of_values():
    ('predicate("field").matches("regex") with a list of values against regex')

    query = predicate('name').regex.matches('oo')
    result = list(filter(query, LIST_OF_VALUES))

    result.should.equal([
        "Foo Bar",
        "Wee Woo",
    ])


def test_query_matches_string_generates_lambda_filter_with_list_of_dicts():
    ('predicate("field").matches("string") with a list of dicts')

    query = predicate('name').matches('Foo Bar')
    result = list(filter(query, LIST_OF_DICTS))

    result.should.equal([
        {"name": "Foo Bar"},
    ])


def test_query_matches_string_generates_lambda_filter_with_a_list_of_values():
    ('predicate("field").matches("string") with a list of values')

    query = predicate('name').matches('Foo Bar')
    result = list(filter(query, LIST_OF_VALUES))

    result.should.equal([
        "Foo Bar",
    ])
