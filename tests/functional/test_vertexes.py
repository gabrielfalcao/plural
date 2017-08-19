# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal
from tests.functional.scenarios import with_hexastore
from tests.edges import Car, Person
from tests.vertexes import CarPurchase
from tests.vertexes import CarSales


@with_hexastore('vehicles')
def test_codecs_from_string(context):

    tesla = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand='Tesla')
    elon = Person(uuid='bad1d3a5bad1d3a5bad1d3a5bad1d3a5', name='Elon Musk')
    chuck = Person(uuid='1c3b00da1c3b00da1c3b00da1c3b00da', name='Chuck Norris')

    purchased_by_chuck_norris = CarPurchase(
        uuid='fedcba98fedcba98fedcba98fedcba98',
        origin=chuck,
        target=tesla,
        contract_signed_at='2017/08/18 16:20:00',
        payment_sent_at='2017/08/18 16:20:00',
    )

    sold_by_elon = CarSales(
        uuid='76543210765432107654321076543210',
        origin=elon,
        target=tesla,
        contract_signed_at='2017/08/18 16:20:00',
        payment_sent_at='2017/08/18 16:20:00',
    )

    sold_by_elon.to_dict().should.equal({
        'contract_signed_at': '2017-08-18T16:20:00',
        'payment_sent_at': '2017/08/18 16:20:00',
        'uuid': '76543210765432107654321076543210',
    })
    purchased_by_chuck_norris.to_dict().should.equal({
        'contract_signed_at': '2017-08-18T16:20:00',
        'payment_sent_at': '2017-08-18T16:20:00',
        'uuid': 'fedcba98fedcba98fedcba98fedcba98',
    })


@with_hexastore('vehicles')
def test_codecs_from_native_types(context):
    tesla = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand='Tesla')
    elon = Person(uuid='bad1d3a5bad1d3a5bad1d3a5bad1d3a5', name='Elon Musk')
    chuck = Person(uuid='1c3b00da1c3b00da1c3b00da1c3b00da', name='Chuck Norris')

    tesla.to_dict().should.equal({
        'brand': 'Tesla',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
    })

    purchased_by_chuck_norris = CarPurchase(
        uuid='fedcba98fedcba98fedcba98fedcba98',
        origin=chuck,
        target=tesla,
        contract_signed_at=datetime(2017, 8, 18, 16, 20, 0),
        payment_sent_at=datetime(2017, 8, 18, 16, 20, 0),
        tested_at=datetime(2017, 8, 18, 16, 20, 0),
        price=Decimal('58314.15'),
    )

    sold_by_elon = CarSales(
        uuid='76543210765432107654321076543210',
        origin=elon,
        target=tesla,
        contract_signed_at=datetime(2017, 8, 18, 16, 20, 0),
        payment_received_at=datetime(2017, 8, 18, 16, 20, 0),
        tested_at=datetime(2017, 8, 18, 16, 20, 0),
        price=Decimal('58314.15'),
    )

    purchased_by_chuck_norris.to_dict().should.equal({
        'contract_signed_at': '2017-08-18T16:20:00',
        'payment_sent_at': '2017-08-18T16:20:00',
        'uuid': 'fedcba98fedcba98fedcba98fedcba98',
        'tested_at': '2017-08-18T16:20:00',
        'price': '58314.15',
    })

    sold_by_elon.to_dict().should.equal({
        'contract_signed_at': '2017-08-18T16:20:00',
        'payment_received_at': '2017-08-18T16:20:00',
        'uuid': '76543210765432107654321076543210',
        'tested_at': '2017-08-18T16:20:00',
        'price': '58314.15',
    })


@with_hexastore('vehicles')
def test_codecs_null_fields(context):
    tesla = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand=None)
    elon = Person(uuid='bad1d3a5bad1d3a5bad1d3a5bad1d3a5', name=None)
    chuck = Person(uuid='1c3b00da1c3b00da1c3b00da1c3b00da', name=None)

    purchased_by_chuck_norris = CarPurchase(
        uuid='fedcba98fedcba98fedcba98fedcba98',
        origin=chuck,
        target=tesla,
        contract_signed_at=None,
        payment_sent_at=None,
        tested_at=None,
        price=None,
    )

    sold_by_elon = CarSales(
        uuid='76543210765432107654321076543210',
        origin=elon,
        target=tesla,
        contract_signed_at=None,
        payment_received_at=None,
        tested_at=None,
        price=None,
    )

    purchased_by_chuck_norris.to_dict().should.equal({
        'contract_signed_at': '',
        'payment_sent_at': '',
        'uuid': 'fedcba98fedcba98fedcba98fedcba98',
        'tested_at': '',
        'price': '',
    })

    sold_by_elon.to_dict().should.equal({
        'contract_signed_at': '',
        'payment_received_at': '',
        'uuid': '76543210765432107654321076543210',
        'tested_at': '',
        'price': '',
    })
