# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime
from tests.functional.scenarios import with_hexastore
from tests.subjects import Car


@with_hexastore('vehicles')
def test_codecs_from_string(context):

    tesla1 = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand='Tesla', max_speed='160.4', last_used='2017/08/18 16:20:00', metadata='{"foo": "bar"}')
    tesla1.brand.should.equal('Tesla')
    tesla1.max_speed.should.equal(Decimal('160.4'))
    tesla1.last_used.should.equal(datetime(2017, 8, 18, 16, 20, 0))
    tesla1.to_dict().should.equal({
        'brand': 'Tesla',
        'last_used': '2017-08-18T16:20:00',
        'max_speed': '160.4',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
        'metadata': '{"foo": "bar"}',
    })


@with_hexastore('vehicles')
def test_codecs_from_native_types(context):
    tesla2 = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand='Tesla', max_speed=Decimal('160.4'), last_used=datetime(2017, 8, 18, 16, 20, 0), metadata={"foo": "bar"})
    tesla2.brand.should.equal('Tesla')
    tesla2.max_speed.should.equal(Decimal('160.4'))
    tesla2.last_used.should.equal(datetime(2017, 8, 18, 16, 20, 0))
    tesla2.to_dict().should.equal({
        'brand': 'Tesla',
        'last_used': '2017-08-18T16:20:00',
        'max_speed': '160.4',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
        'metadata': '{"foo": "bar"}',
    })


@with_hexastore('vehicles')
def test_codecs_null_fields(context):
    tesla3 = Car(uuid='deadbeefdeadbeefdeadbeefdeadbeef', brand=None, max_speed=None, last_used=None, metadata=None)
    tesla3.brand.should.be.none
    tesla3.max_speed.should.be.none
    tesla3.last_used.should.be.none
    tesla3.to_dict().should.equal({
        'brand': '',
        'last_used': '',
        'max_speed': '',
        'uuid': 'deadbeefdeadbeefdeadbeefdeadbeef',
        'metadata': '',
    })
