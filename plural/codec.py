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
import bz2
import json
import zlib
from decimal import Decimal
from dateutil.parser import parse as parse_datetime


class Codec(object):  # pragma: no cover
    def encode(self, data):
        if not data:
            return ''

        return self.dumps(data)

    def decode(self, string):
        if not isinstance(string, basestring):
            return string

        return self.loads(string)

    def loads(self, string):
        raise NotImplementedError

    def dumps(self, string):
        raise NotImplementedError


class Binary(Codec):
    def loads(self, binary):
        return binary

    def dumps(self, binary):
        return binary


class Gzip(Codec):
    def loads(self, binary):
        return zlib.deompress(binary)

    def dumps(self, binary):
        return zlib.compress(binary)


class Bzip2(Codec):
    def loads(self, binary):
        return bz2.deompress(binary)

    def dumps(self, binary):
        return bz2.compress(binary)


class Unicode(Codec):
    """codec for UTF-8 dumpsd strings"""
    encoding = 'utf-8'

    def dumps(self, string):
        return string.encode(self.encoding)

    def loads(self, string):
        return string.decode(self.encoding)


class DateTime(Codec):
    """codec for datetime objects"""
    def dumps(self, datetime):
        return datetime.isoformat()

    def loads(self, string):
        return parse_datetime(string)


class Number(Codec):
    """codec for Decimal objects"""
    def dumps(self, number):
        return bytes(number)

    def loads(self, string):
        return Decimal(string)


class JSON(Codec):
    """codec for JSON objects"""

    def dumps(self, data):
        return json.dumps(data)

    def loads(self, string):
        return json.loads(string)
