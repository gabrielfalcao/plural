# -*- coding: utf-8 -*-
from plural import Subject
from plural import SubjectDefinitionNotFound
from plural import InvalidSubjectDefinition


def define_subject_without_indexes():
    class Post(Subject):
        pass

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


def test_indexes_definition():
    define_subject_without_indexes.when.called.should.have.raised(
        InvalidSubjectDefinition,
        "the <class 'tests.functional.test_subject_definition.Post'> definition should have at least one index"
    )
