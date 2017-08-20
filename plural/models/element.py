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
from collections import OrderedDict
from hashlib import sha256
from plural.util import generate_uuid
from plural.util import AutoCodec


class Element(object):
    """json-serializable data-model for Edges and Vertices"""

    def __init__(self, uuid=None, **kw):
        self.uuid = kw.get('uuid', uuid)
        self.__data__ = OrderedDict([(k, self.decode_field(k, v)) for k, v in kw.items()])
        self.__data__['uuid'] = uuid or generate_uuid()

    def __setitem__(self, key, value):
        self.__data__[key] = self.encode_field(key, value)

    def __contains__(self, key):
        return key in self.__data__

    def __getitem__(self, key):
        value = self.__data__[key]
        return self.decode_field(key, value)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return object.__setattr__(self, key, value)

        if key in self.__fields__:
            self.__data__[key] = self.encode_field(key, value)
        else:
            object.__setattr__(self, key, value)

    def __getattr__(self, key):
        if key.startswith('_'):
            return super(Element, self).__getattribute__(key)

        if key not in self.__data__:
            raise AttributeError('key not found: {}'.format(key))

        value = self.__data__[key]
        return self.decode_field(key, value)

    def to_dict(self):
        return dict([(k, self.encode_field(k, v)) for k, v in self.__data__.items()])

    def to_json(self, **kw):
        kw['sort_keys'] = True
        kw['default'] = AutoCodec().encode
        return json.dumps(self.to_dict(), **kw)

    def decode_field(self, name, value):
        codec = self.__codecs__.get(name, AutoCodec())
        if not codec:
            return value

        return codec.decode(value)

    def encode_field(self, name, value):
        codec = self.__codecs__.get(name, AutoCodec())
        if not codec:
            return value or ''

        return codec.encode(value)

    def __hash__(self):
        return int(sha256(self.to_json()).hexdigest(), 16)

    def __str__(self):
        return ''.join([self.__class__.__name__, self.to_json()])

    def __repr__(self):
        return ".".join([self.__class__.__module__, bytes(self)])

    def __eq__(self, other):
        return isinstance(other, Element) and self.to_dict() == other.to_dict()

    @classmethod
    def from_data(cls, ___name___=None, **kw):
        """
        creates a new instance of the given :py:class:`Element` with the provided ``**kwargs``

        :param ___name___: the name of the element type
        :param ``**kw``: a dictionary
        :returns: an instance of the given :py:class:`Element` subclass
        """
        name = ___name___ or cls.__name__
        Definition = cls.definition(name)
        return Definition(**kw)

    @classmethod
    def from_dict(Definition, data):
        """
        creates a new instance of the given :py:class:`Element` with the provided ``data``

        :param data: a dictionary
        :returns: an instance of the given :py:class:`Element` subclass
        """
        return Definition(**data)
