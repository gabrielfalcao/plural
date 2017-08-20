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
from pygit2 import GIT_FILEMODE_BLOB
from mock import patch, call, MagicMock

from plural.store import PluralStore
from tests.edges import Car
from tests.edges import Person
from tests.vertices import CarPurchase
from tests.vertices import CarSale
from .scenarios import with_graph_store


@patch('plural.store.Signature')
@patch('plural.store.init_repository')
def test_constructor(init_repository, Signature):
    ('PluralStore.add_remote() should create a remote')

    repository = MagicMock(name='repository')
    store = PluralStore(
        '/opt/git',
        True,
        'User Name',
        'email@hostname',
        'refs/heads/db',
        repository,
    )

    Signature.assert_has_calls([
        call('User Name', 'email@hostname'),
        call('User Name', 'email@hostname'),
    ])

    store.should.have.property('path').being.equal('/opt/git')
    store.should.have.property('bare').being.equal(True)
    store.should.have.property('repository').being.equal(repository)
    store.should.have.property('default_branch').being.equal('refs/heads/db')
    store.should.have.property('author').being.equal(Signature.return_value)
    store.should.have.property('commiter').being.equal(Signature.return_value)
    store.should.have.property('queries').being.equal([])


@with_graph_store('/path/to/folder')
@patch('plural.store.Signature')
@patch('plural.store.init_repository')
def test_add_remote(context, init_repository, Signature):
    ('PluralStore.add_remote() should create a remote')

    context.store.add_remote('name', 'ssh://user@remote:path')

    context.store.repository.remotes.create.assert_called_once_with(
        'name',
        'ssh://user@remote:path',
    )


@with_graph_store('/path/to/folder')
def test_serialize(context):
    ('PluralStore.serialize() should return a pretty json string')

    result = context.store.serialize({
        'foo': 'bar',
    })

    result.should.equal('{"foo": "bar"}')


@with_graph_store('/path/to/folder')
def test_deserialize(context):
    ('PluralStore.deserialize() should parse a json object')

    result = context.store.deserialize('{\n  "foo": "bar"\n}')
    result.should.equal({
        'foo': 'bar',
    })


@with_graph_store('/path/to/folder')
@patch('plural.store.pygit2')
@patch('plural.store.serialize_commit')
def test_iter_versions(context, serialize_commit, pygit2):
    ('PluralStore.iter_versions() should return a generator of serialized commits')

    serialize_commit.side_effect = lambda c: 'SERIALIZED:{}'.format(c)
    context.store.repository.walk.return_value = [
        'commit-one',
        'commit-two',
    ]

    result = context.store.iter_versions()
    result.should.be.a('types.GeneratorType')

    serialized_commits = list(result)

    serialized_commits.should.equal([
        'SERIALIZED:commit-one',
        'SERIALIZED:commit-two',
    ])


@with_graph_store('/path/to/folder')
@patch('plural.store.pygit2')
@patch('plural.store.serialize_commit')
def test_get_versions(context, serialize_commit, pygit2):
    ('PluralStore.iter_versions() should return a generator of serialized commits')

    serialize_commit.side_effect = lambda c: 'SERIALIZED:{}'.format(c)
    context.store.repository.walk.return_value = [
        'commit-one',
        'commit-two',
    ]

    result = context.store.get_versions()

    result.should.equal([
        'SERIALIZED:commit-one',
        'SERIALIZED:commit-two',
    ])


@with_graph_store('/path/to/folder')
@patch('plural.store.IndexEntry')
def test_add_spo(context, IndexEntry):
    ('PluralStore.add_spo() should add an IndexEntry to the repo')

    context.store.repository.create_blob.return_value = 'blob-id'
    IndexEntry.return_value = 'index-entry'

    context.store.add_spo('edge', 'predicate', 'object')
    context.store.repository.create_blob.assert_called_once_with('object')
    context.store.repository.index.add.assert_called_once_with('index-entry')
    IndexEntry.assert_called_once_with(
        'edge/predicate', 'blob-id', GIT_FILEMODE_BLOB)


@with_graph_store('/path/to/folder')
@patch('plural.store.PluralStore.create_edge')
def test_save_nodes(context, create):
    ('PluralStore.save_nodes() should .create_edge() each given node ')
    create.side_effect = lambda name, **data: 'mock-{}'.format(name.lower())
    car1 = Car(uuid='uuid1', brand='Ferrari', model='F1')
    car2 = Car(uuid='uuid2', brand='Tesla', model='Model S')

    nodes = context.store.save_nodes(car1, car2)

    nodes.should.equal(['mock-car', 'mock-car'])

    create.assert_has_calls([
        call('Car', brand='Ferrari', model='F1', uuid='uuid1'),
        call('Car', brand='Tesla', model='Model S', uuid='uuid2'),
    ])


@with_graph_store('/path/to/folder')
@patch('plural.store.PluralStore.save_nodes')
@patch('plural.store.PluralStore.commit')
def test_merge(context, commit, save_nodes):
    ('PluralStore.merge() should .save_nodes() and .commit()')

    save_nodes.return_value = 'the-saved-nodes'

    car1 = Car(brand='Ferrari', model='F1')
    car2 = Car(brand='Tesla', model='Model S')

    nodes = context.store.merge(car1, car2)

    nodes.should.equal('the-saved-nodes')

    save_nodes.assert_called_once_with(car1, car2)
    commit.assert_called_once_with()


@with_graph_store('/path/to/folder')
@patch('plural.store.pygit2.hash')
@patch('plural.store.PluralStore.add_spo')
def test_create_edge(context, add_spo, git_object_hash):
    ('PluralStore.create_edge() should add spos for its indexes')

    git_object_hash.return_value = 'git-object-hash'
    data = {
        'uuid': 'generated-uuid4',
        'max_speed': '160.4',
        'brand': 'Tesla',
        'model': 'Model S',
        'nickname': 'Lightning'
    }
    tesla = context.store.create_edge(Car, **data)
    tesla.should.be.a(Car)
    tesla.to_dict().should.be.a(dict)

    add_spo.assert_has_calls([
        call('Car/indexes/model', 'git-object-hash', 'Model S'),
        call('Car/indexes/max_speed', 'git-object-hash', '160.4'),
        call('Car/indexes/nickname', 'git-object-hash', 'Lightning'),
        call('Car/indexes/brand', 'git-object-hash', 'Tesla'),
        call('Car/indexes/uuid', 'git-object-hash', 'generated-uuid4'),
        call('Car/objects', 'git-object-hash', tesla.to_json()),
        call('Car/_ids', 'generated-uuid4', 'git-object-hash'),
        call('Car/_uuids', 'git-object-hash', 'generated-uuid4'),
    ])


@with_graph_store('/path/to/folder')
@patch('plural.store.pygit2.hash')
@patch('plural.store.PluralStore.add_spo')
def test_create_vertex_incoming(context, add_spo, git_object_hash):
    ('PluralStore.create_vertex() should add spos for its indexes')

    git_object_hash.return_value = 'git-object-hash'
    tesla = Car(uuid='car-uuid', brand='Tesla')
    chuck = Person(uuid='chuck-uuid', name='Chuck Norris')

    purchase = context.store.create_vertex(
        CarPurchase,
        uuid='purchase-uuid',
        origin=chuck,
        target=tesla,
        contract_signed_at='2017-08-18 00:31:45',
        payment_sent_at='2017-07-04 15:25:35',
    )
    purchase.should.be.a(CarPurchase)
    purchase.to_dict().should.be.a(dict)

    add_spo.assert_has_calls([
        call('CarPurchase/indexes/contract_signed_at', 'git-object-hash', '2017-08-18 00:31:45'),
        call('CarPurchase/indexes/uuid', 'git-object-hash', 'purchase-uuid'),
        call('CarPurchase/indexes/payment_sent_at', 'git-object-hash', '2017-07-04 15:25:35'),
        call('CarPurchase/_ids', 'purchase-uuid', 'git-object-hash'),
        call('CarPurchase/_uuids', 'git-object-hash', 'purchase-uuid'),
        call('Car/incoming/bought_by/Person', 'chuck-uuid', 'car-uuid')
    ])


# @with_graph_store('/path/to/folder')
# @patch('plural.store.pygit2.hash')
# @patch('plural.store.PluralStore.add_spo')
# def test_create_vertex_outgoing(context, add_spo, git_object_hash):
#     ('PluralStore.create_vertex() should add spos for its indexes')

#     git_object_hash.return_value = 'git-object-hash'
#     tesla = Car(uuid='car-uuid', brand='Tesla')
#     elon = Person(uuid='elon-uuid', name='Elon Musk')

#     sale = context.store.create_vertex(
#         CarSale,
#         uuid='sales-uuid',
#         origin=elon,
#         target=tesla,
#         contract_signed_at='2017-08-18 00:31:45',
#         payment_received_at='2017-07-04 15:25:35',
#     )

#     sale.should.be.a(CarSale)
#     sale.to_dict().should.be.a(dict)

#     add_spo.assert_has_calls([
#         call('Car/outgoing/sold_by/Person', 'uuid', 'elon-uuid'),
#         call('CarSale/indexes/contract_signed_at', 'git-object-hash', 'contract-signed-at'),
#         call('CarSale/indexes/payment_sent_at', 'git-object-hash', 'payment-sent-at'),
#         call('CarSale/indexes/uuid', 'git-object-hash', 'sale-uuid'),
#         call('CarSale/objects', 'git-object-hash', sale.to_json()),
#         call('CarSale/_ids', 'sale-uuid', 'git-object-hash'),
#         call('CarSale/_uuids', 'git-object-hash', 'sale-uuid')
#     ])
