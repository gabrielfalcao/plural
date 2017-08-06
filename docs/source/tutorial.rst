.. _Tutorial:


.. highlight:: bash



Basic Usage
===========

Instalation
-----------

.. code:: bash

    pip install gitgraph


Declaring Subjects
------------------


.. code:: python

    from gitgraph import GitGraph
    from gitgraph import Subject

    store = GitGraph('my-git-cms')

    class Document(Subject):
        indexes = {'title'}
        predicates = (
            ('title', codec.Unicode),
            ('body', codec.Unicode),
            ('created_at', codec.DateTime),
            ('published_at', codec.DateTime),
        )

        incoming = {
            'authored_by': Author,
        }
        outgoing = {
            'contains': Tag,
        }

Create
------

.. code:: python

    uuid1 = 'deadbeefdeadbeefdeadbeefdeadbeef'

    # providing your own uuid
    docs1 = store.create(
        'Document',
        uuid=uuid1,
        title='Essay',
        body='body1',
    )

    # auto-generated uuid
    docs2 = store.create(
        Document,
        title='Blog',
        body='body2',
    )

    store.commit()

    uuid2 = docs2.uuid


Retrieve
--------

One By UUID
~~~~~~~~~~~

.. code:: python

    # Using the class Document as subject type
    docs1 = store.get_subject_by_uuid(Document, uuid1)

    # Using the subject label
    docs2 = store.get_subject_by_uuid('Document', uuid2)


Many By Indexed Predicate
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python


    from gitgraph.query import predicate
    # functional
    query = lambda title: 'Blog' in title

    # DSL
    query = predicate('title').contains('Blog')
    blog_documents = set(store.match_subjects_by_index(Document, 'title', query))

    # With Regex
    query = predicate('title').matches('([Bb]log|[Ee]ssa[yi]s?)')
    blogs_and_essays = set(store.match_subjects_by_index(Document, 'title', query))

Update
------

.. code:: python

    docs1.title = 'new title'

    docs2.title = 'documento dois'
    docs2.body = '<p>Hello</p>'

    store.merge(docs1, docs2)

    # recreate the doc1
    docs1 = store.create(
        Document,
        uuid=uuid1,
        title='Essay',
        body='body1',
    )



Delete
------

.. code:: python

    store.delete(docs1)
    store.commit()
