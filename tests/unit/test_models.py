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

from gitgraph.models import Subject
from gitgraph.models import resolve_subject_name
from gitgraph.models import resolve_subject


class Vehicle(Subject):
    indexes = {
        'max_speed',
        'min_speed',
    }


def test_resolve_subject_name():
    'resolve_subject_name() should return a string'

    resolve_subject_name('Vehicle').should.equal('Vehicle')
    resolve_subject_name(None).should.equal('*')
    resolve_subject_name(Vehicle).should.equal('Vehicle')
    resolve_subject_name.when.called_with({}).should.have.raised(
        TypeError,
        'resolve_subject_name() takes a Subject subclass, a string or None. Got {}'
    )


def test_resolve_subject():
    'resolve_subject() should return a string'

    resolve_subject('Vehicle').should.equal(Vehicle)
    resolve_subject(Vehicle).should.equal(Vehicle)
    resolve_subject.when.called_with(None).should.have.raised(
        TypeError,
        'resolve_subject() takes a Subject subclass or a string. Got None'
    )
