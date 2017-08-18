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
import json
from decimal import Decimal
from dateutil.parser import parse as parse_datetime


class Codec(object):  # pragma: no cover
    def decode(self, string):
        raise NotImplementedError

    def encode(self, string):
        raise NotImplementedError


class Unicode(Codec):
    encoding = 'utf-8'

    def encode(self, string):
        if not string:
            return ''

        return string.encode(self.encoding)

    def decode(self, string):
        if not isinstance(string, basestring):
            return string

        return string.decode(self.encoding)


class DateTime(Codec):
    def encode(self, datetime):
        if not datetime:
            return ''

        return datetime.isoformat()

    def decode(self, string):
        if not isinstance(string, basestring):
            return string

        return parse_datetime(string)


class Number(Codec):
    def encode(self, number):
        if not number:
            return ''
        return bytes(number)

    def decode(self, string):
        if not isinstance(string, basestring):
            return string

        return Decimal(string)


class JSON(Codec):
    def encode(self, data):
        if not data:
            return ''

        return json.dumps(data)

    def decode(self, string):
        if not isinstance(string, basestring):
            return string

        return json.loads(string)
