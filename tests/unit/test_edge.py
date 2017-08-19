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
import json
from plural.models.edges import Edge
from plural.models.meta.edges import edge_has_index
from plural.exceptions import InvalidEdgeDefinition
from tests.edges import Person


def test_edge_from_data_to_dict():
    ('Edge.from_data(**fields).to_dict() should contain its data')

    input_data = {
        'name': 'Foo Bar',
        'birthdate': '1973/07/04',
    }

    foobar = Person.from_data(**input_data)
    foobar.should.be.a(Person)

    foobar.to_dict().should.have.key('name').being.equal('Foo Bar')
    foobar.to_dict().should.have.key('birthdate').being.equal('1973/07/04')
    foobar.to_dict().should.have.key('uuid').being.a(basestring)


def test_edge_from_dict_get_item():
    ('Edge.from_data(**fields)["field_name"] should return its value')

    input_data = {
        'name': 'Foo Bar',
        'birthdate': '1973/07/04',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
    }

    foobar = Person.from_dict(input_data)
    foobar.should.be.a(Person)

    foobar['uuid'] = 'woot'
    foobar.should.have.key('name').being.equal('Foo Bar')
    foobar.should.have.key('birthdate').being.equal('1973/07/04')
    foobar.should.have.key('uuid').being.a(basestring)
    foobar.should_not.have.key('invalid-one')


def test_edge_from_dict_get_attribute():
    ('Edge.from_data(**fields).field_name should return its value')

    input_data = {
        'name': 'Foo Bar',
        'birthdate': '1973/07/04',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
    }

    foobar = Person.from_dict(input_data)
    foobar.should.be.a(Person)

    foobar.uuid = 'woot'
    foobar.should.have.property('name').being.equal('Foo Bar')
    foobar.should.have.property('birthdate').being.equal('1973/07/04')
    foobar.should.have.property('uuid').being.equal('woot')
    hash(foobar).should.equal(6193599141153582213)
    hasattr(foobar, '__invalid__').should.be.false
    hasattr(foobar, 'invalid').should.be.false

    foobar.to_json().should.equal(json.dumps(foobar.to_dict()))
    bytes(foobar).should.match('^Person[{]')
    repr(foobar).should.match('^tests.edges.Person[{]')
    foobar.should.equal(foobar)


def test_edge_has_index():
    ('edge_has_index() should return a set')

    edge_has_index('Person', 'name').should.equal({'name'})
    edge_has_index('Person', 'email').should.be.false
    edge_has_index('Unknown', 'name').should.be.false


def test_define_invalid_edge_no_indexes():
    ('declaring Edge without indexes should raise InvalidEdgeDefinition')

    def declare():
        class Thing(Edge):
            pass

    declare.when.called.should.have.raised(InvalidEdgeDefinition)


def test_define_invalid_edge_invalid_indexes():
    ('declaring Edge with invalid indexes should raise InvalidEdgeDefinition')

    def declare():
        class Thing(Edge):
            indexes = 'invalid'

    declare.when.called.should.have.raised(InvalidEdgeDefinition)
