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

import logging

import zmq.green as zmq
from agentzero.core import SocketManager

logger = logging.getLogger('server')


class GraphClient(object):
    def __init__(self, request_connect_addr='tcp://127.0.0.1:6000'):
        self.context = zmq.Context()
        self.sockets = SocketManager(zmq, self.context)
        self.sockets.ensure_and_connect('query', zmq.REQ, request_connect_addr, zmq.POLLIN | zmq.POLLOUT)
        print 'connected to', request_connect_addr

    def request(self, data):
        self.sockets.send_safe('query', data)
        result = self.sockets.recv_safe('query')
        return result

    def query(self, string):
        return self.request({'query': string})
