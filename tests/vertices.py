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
from plural import IncomingVertex
from plural import OutgoingVertex
from plural import codec


class CarPurchase(IncomingVertex):
    indexes = {'contract_signed_at', 'payment_sent_at'}
    fields = {
        'contract_signed_at': codec.DateTime,
        'payment_sent_at': codec.DateTime,
    }


class CarSale(OutgoingVertex):
    indexes = {'contract_signed_at', 'payment_received_at'}
    fields = {
        'contract_signed_at': codec.DateTime,
        'payment_received_at': codec.DateTime,
    }


class CarDeal(OutgoingVertex):
    indexes = {'delivered_at'}
    fields = {
        'delivered_at': codec.DateTime,
    }


class AuthoredDocument(IncomingVertex):
    indexes = {'created_at', 'modified_at'}
    fields = {
        'created_at': codec.DateTime,
        'modified_at': codec.DateTime,
    }


class TaggedDocument(OutgoingVertex):
    indexes = {'created_at'}
    fields = {
        'created_at': codec.DateTime,
    }
