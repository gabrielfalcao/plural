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
import graphene
import json
import logging
from gevent.pool import Pool
from gevent.event import Event
import zmq.green as zmq
from pprint import pprint
from agentzero.core import SocketManager

logger = logging.getLogger('server')


class Person(graphene.ObjectType):
    name = graphene.String()

    def resolve_name(self, args, context, info):
        return "Jack"


class Query(graphene.ObjectType):
    person = graphene.Field(Person)

    def resolve_person(self, args, context, info):
        return Person(**args)


schema = graphene.Schema(query=Query, types=[Person])


class GraphServer(object):
    def __init__(self, sleep_interval=3, pool_size=8):
        self.context = zmq.Context()
        self.sockets = SocketManager(zmq, self.context)
        self.sleep_interval = sleep_interval
        self.pool_size = pool_size
        self.pool = Pool(pool_size)
        self.allowed_to_run = Event()
        self.allowed_to_run.set()

    def should_run(self):
        return self.allowed_to_run.is_set()

    def listener_coroutine(self, socket_name, reply_bind_addr):
        # TODO: DEALER/ROUTER + internal multiplexing of request ids?
        self.sockets.ensure_and_bind(socket_name, zmq.REP, reply_bind_addr, zmq.POLLIN | zmq.POLLOUT)
        self.sockets.set_socket_option(socket_name, zmq.IDENTITY, socket_name)

        while self.should_run():
            if not self.process_request(socket_name):
                logger.debug('waiting %s second%s', self.sleep_interval, self.sleep_interval == 1 and '' or 's')

    def process_request(self, socket_name):
        data = self.sockets.recv_safe(socket_name, timeout=self.sleep_interval)
        if data:
            logger.info('processed request')
            pprint(data)
            query = data['query']
            result = schema.execute(query)
            if result.errors:
                payload = {
                    'errors': "\n".join(map(unicode, result.errors))
                }
            else:
                payload = {
                    'result': json.dumps(result.data, indent=2)
                }
            self.sockets.send_safe(socket_name, payload)
            return True
        return False

    def run(self, reply_bind_addr='tcp://*:6000'):
        logger.info('listening on %s', reply_bind_addr)
        self.pool.spawn(self.listener_coroutine, 'reply1', reply_bind_addr)
        self.pool.join(raise_error=True)

    def stop(self):
        self.allowed_to_run.clear()
        self.sockets.close('reply1')
        self.pool.kill()
