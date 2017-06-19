# -*- coding: utf-8 -*-
from gitgraph import Subject
from gitgraph import SubjectDefinitionNotFound


def test_subject_definition():

    Subject.definition.when.called_with('Actor').should.have.raised(
        SubjectDefinitionNotFound,
        'there are no subject subclass defined with the name "Actor"'
    )

    class Actor(Subject):
        indexes = {
            'name',
        }

    Subject.definition('Actor').should.equal(Actor)
