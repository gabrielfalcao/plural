#!/usr/bin/env python
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
# import time
# import json
from plural import Plural
from plural import Edge
# from plural import codec

# from datetime import datetime


class Tag(Edge):
    indexes = {'name'}


def run_benchmark(item_count, commit_every_create=False):
    store = Plural('benchmark-{}'.format(item_count))

    for x in range(item_count):
        name = bytes(x)
        store.create(Tag, name=name)
        if commit_every_create:
            store.commit()

    store.commit()


run_benchmark(10000, commit_every_creat=False)
