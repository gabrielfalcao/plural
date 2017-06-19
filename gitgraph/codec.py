# -*- coding: utf-8 -*-
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
