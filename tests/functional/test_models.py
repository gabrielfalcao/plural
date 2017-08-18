# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime
from tests.functional.scenarios import with_hexastore
from tests.subjects import Car


@with_hexastore('vehicles')
def test_codecs_from_string(context):

    tesla1 = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand='Tesla', max_speed='160.4', last_used='2017/08/18 16:20:00')
    tesla1.max_speed.should.equal(Decimal('160.4'))
    tesla1.last_used.should.equal(datetime(2017, 8, 18, 16, 20, 0))
    tesla1.to_dict().should.equal({
        'brand': 'Tesla',
        'last_used': '2017-08-18T16:20:00',
        'max_speed': '160.4',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
    })


@with_hexastore('vehicles')
def test_codecs_from_native_types(context):
    tesla2 = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand='Tesla', max_speed=Decimal('160.4'), last_used=datetime(2017, 8, 18, 16, 20, 0))
    tesla2.max_speed.should.equal(Decimal('160.4'))
    tesla2.last_used.should.equal(datetime(2017, 8, 18, 16, 20, 0))
    tesla2.to_dict().should.equal({
        'brand': 'Tesla',
        'last_used': '2017-08-18T16:20:00',
        'max_speed': '160.4',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
    })
