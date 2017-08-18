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
import sys
import argparse
import logging
import coloredlogs
from plural.server import GraphServer
from plural.repl import Repl
from plural.client import GraphClient

coloredlogs.DEFAULT_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'


def execute_plural_server():  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog='plural-server',
        description='ZMQ Reply Server that executes queries')

    parser.add_argument(
        '-b', '--reply-bind-addr',
        default='tcp://*:6000',
        help='ZMQ address to bind to'
    )

    parser.add_argument(
        '--color',
        action='store_true',
        default=True,
        help='colored logs'
    )
    parser.add_argument(
        '-l', '--log-level',
        default='DEBUG',
        choices=('DEBUG', 'INFO', 'WARNING')
    )

    args = parser.parse_args()
    server = GraphServer()
    if args.color:
        coloredlogs.install(level=args.log_level)

    logging.warning('EXPERIMENTAL FEATURE: server')
    try:
        server.run(args.reply_bind_addr)
    except KeyboardInterrupt:
        server.stop()
        sys.stdout.write("\r")
        sys.stderr.write("\r")
        sys.stdout.flush()
        sys.stderr.flush()


def execute_plural_client():  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog='plural-client',
        description='ZMQ client')
    parser.add_argument(
        '-a', '--address',
        default='tcp://127.0.0.1:6000',
        help='ZMQ server address to connect to'
    )

    args = parser.parse_args()
    logging.warning('EXPERIMENTAL FEATURE: client')

    client = GraphClient(args.address)

    repl = Repl(client.query)
    exitcode = repl.run()
    raise SystemExit(exitcode)
