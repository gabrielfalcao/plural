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

from uuid import uuid4
# from time import mktime
from decimal import Decimal
from datetime import datetime, date, time


def generate_uuid():
    return uuid4().hex


def serialize_commit(commit):
    data = {
        'author': {
            'name': commit.author.name,
            'email': commit.author.email,
        },
        'committer': {
            'name': commit.committer.name,
            'email': commit.committer.email,
        },
        'message': commit.message,
        'date': datetime.utcfromtimestamp(float(commit.commit_time)),
    }
    return data


class AutoCodec(object):
    def decode(self, obj):
        return obj

    def encode(self, obj):
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()

        if isinstance(obj, (Decimal)):
            return bytes(obj)

        if callable(getattr(obj, 'to_dict', None)):
            return obj.to_dict()

        if obj is None:
            return b''

        return obj
