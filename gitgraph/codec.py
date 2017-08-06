# -*- coding: utf-8 -*-
#
# <GitGraph - Git-powered library>
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

from decimal import Decimal
from dateutil.parser import parse as parse_datetime


class Codec(object):
    def decode(self, string):
        raise NotImplementedError

    def encode(self, string):
        raise NotImplementedError


class Unicode(Codec):
    encoding = 'utf-8'

    def encode(self, string):
        return string.encode(self.encoding)

    def decode(self, string):
        return string.decode(self.encoding)


class DateTime(Codec):
    def encode(self, datetime):
        return datetime.isoformat()

    def decode(self, string):
        return parse_datetime(string)


class Number(Codec):
    def encode(self, number):
        return bytes(number)

    def decode(self, string):
        return Decimal(string)
