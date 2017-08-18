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
from plural import Subject
from plural import codec


class Vehicle(Subject):
    indexes = {
        'max_speed',
    }
    fields = {
        'max_speed': codec.Number,
    }


class Person(Subject):
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

    sold_by = Person.v.incoming({
        'contract_signed_at': codec.DateTime,
    }, 'sales')

    bought_by = Person.v.outgoing({
        'contract_signed_at': codec.DateTime,
    }, 'purchases')


class Tag(Subject):
    indexes = {'name'}


class Author(Subject):
    indexes = {
        'name',
        'email',
    }


class Document(Subject):
    indexes = {'title', 'content'}
    fields = {
        'title': codec.Unicode,
    }

    authored_by = Author.v.incoming({
        'created_at': codec.DateTime,
        'modified_at': codec.DateTime,
    }, 'documents')

    tagged_by = Tag.v.outgoing([
        ('created_at', codec.DateTime),
    ], 'documents')
