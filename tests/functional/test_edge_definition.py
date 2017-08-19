# -*- coding: utf-8 -*-
from plural import Edge
from plural import EdgeDefinitionNotFound
from plural import InvalidEdgeDefinition


def define_edge_without_indexes():
    class Post(Edge):
        pass

def test_edge_definition():

    Edge.definition.when.called_with('Actor').should.have.raised(
        EdgeDefinitionNotFound,
        'there are no edge subclass defined with the name "Actor"'
    )

    class Actor(Edge):
        indexes = {
            'name',
        }

    Edge.definition('Actor').should.equal(Actor)


def test_indexes_definition():
    define_edge_without_indexes.when.called.should.have.raised(
        InvalidEdgeDefinition,
        "the <class 'tests.functional.test_edge_definition.Post'> definition should have at least one index"
    )
