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
from plural import Edge
from plural import codec

from tests.vertices import AuthoredDocument
from tests.vertices import TaggedDocument
from tests.vertices import CarPurchase
from tests.vertices import CarSale
from tests.vertices import CarDeal
from plural.models.meta.vertices import outgoing_vertex
from plural.models.meta.vertices import indirect_vertex
from plural.models.meta.vertices import incoming_vertex


class Vehicle(Edge):
    indexes = {
        'max_speed',
    }
    fields = {
        'max_speed': codec.Number,
    }


class Person(Edge):
    indexes = {
        'name',
    }
    fields = {
        'name': codec.Unicode,
    }


class Car(Vehicle):
    indexes = {
        'brand',
        'model',
    }
    fields = {
        'brand': codec.Unicode,
        'model': codec.Unicode,
        'last_used': codec.DateTime,
        'metadata': codec.JSON,
    }

    vertices = [
        incoming_vertex('sold_by', 'Person').through(CarSale),
        outgoing_vertex('bought_by', 'Person').through(CarPurchase),
        indirect_vertex('deal', 'Person').through(CarDeal),
    ]


class Tag(Edge):
    indexes = {'name'}
    fields = {
        'name': codec.Unicode,
    }


class Author(Edge):
    indexes = {
        'name',
        'email',
    }


class Document(Edge):
    indexes = {'title', 'content'}
    fields = {
        'title': codec.Unicode,
    }

    vertices = [
        incoming_vertex('authored_by', Author).through(AuthoredDocument),
        outgoing_vertex('tagged_by', Tag).through(TaggedDocument),
    ]
