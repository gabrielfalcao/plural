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
import tty
import sys


class Repl(object):
    def __init__(self, callback, out=None, err=None):
        self.out = out or sys.stdout
        self.err = err or sys.stderr
        self.callback = callback
        self.history = []
        self.history_pos = 0
        self.query = ''

    def prompt(self):
        ps1 = '\033[1;35mGraphQL> \033[0m'
        result = None
        while not self.query.endswith(';'):
            if ps1:
                sys.stdout.write(ps1)
                ps1 = ''

            char = sys.stdin.read(1)
            if not char:
                continue

            if char == '\033[A' and len(self.history) > (self.history_pos * -1):
                self.history_pos -= 1
                result = self.history[self.history_pos]
                sys.stdout.write('\r')
                break
            elif char == '\n':
                if not self.query.rstrip().endswith(';'):
                    ps1 = '\033[1;30m... \033[0m'
                self.query += ''
                continue
            elif char == ';':
                break
            else:
                self.query += char
                continue

        if result is None:
            result = self.query

        self.history.append(self.query)
        self.query = ''

        return result

    def evaluate(self, value):
        return self.callback(value)

    def mainloop(self):
        while True:
            data = self.evaluate(self.prompt())
            if 'errors' in data:
                self.err.write("\033[0;31m")
                self.err.write(data['errors'])
                self.err.write("\033[0m")
                self.err.write("\n")
                self.err.flush()
            else:
                self.out.write("\033[1;37m")
                self.out.write(data['result'])
                self.out.write("\033[0m")
                self.out.write("\n")
                self.out.flush()

    def run(self):

        try:
            self.mainloop()
            return 0
        except KeyboardInterrupt:
            self.err.write('\r')
            self.err.flush()
            self.out.write('\r')
            self.out.flush()
            return 1
