GitGraph - A git-backed graph database
======================================

This is an experimental project with idea taken from the `hexastore
<http://www.vldb.org/pvldb/1/1453965.pdf>`_ paper.

Usage:
------

.. code:: python

    from gitgraph import GitGraph
    from gitgraph import Subject

    store = GitGraph('my-git-cms')

    class Document(Subject):
        indexes = {'title'}
        fields = (
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

    uuid1 = 'deadbeefdeadbeefdeadbeefdeadbeef'
    uuid2 = '1c3b00da1c3b00da1c3b00da1c3b00da'

    # create a couple of "Document" subjects
    docs1 = store.create(
        'Document',
        uuid=uuid1,
        title='Essay',
        body='body1',
    )
    docs2 = store.create(
        Document,
        uuid=uuid2,
        title='Blog',
        body='body2',
    )
    # commit changes
    store.commit()

    # delete existing subject
    store.delete(docs1)
    # commit changes
    store.commit()

    # create or update existing by matching indexes + id
    store.merge(docs1, docs2)

    # recreate the doc1
    docs1 = store.create(
        Document,
        uuid=uuid1,
        title='Essay',
        body='body1',
    )

    # create doc3 with a auto-generated uuid
    docs3 = store.create(
        Document,
        title='Automated',
        body='body1',
    )
    uuid3 = docs3.uuid

    docs11 = store.get_subject_by_uuid('Document', uuid1)
    docs22 = store.get_subject_by_uuid(Document, uuid2)
    docs33 = store.get_subject_by_uuid(Document, uuid3)
    assert docs1 == docs11
    assert docs2 == docs22
    assert docs3 == docs33

    store.delete(docs3)

    blog_documents = set(store.match_subjects_by_index(Document, 'title', lambda title: 'Blog' in title))
    essays_and_posts_documents = set(store.match_subjects_by_index(Document, 'title', lambda title: 'Blog' in title or 'Essay' in title ))
    assert len(blog_documents) == 1
    assert len(essays_and_documents) == 2
    assert docs1 in blog_documents
    assert docs11 in blog_documents

    assert docs2 not in blog_documents
    assert docs22 not in blog_documents

    assert docs1 in essays_and_posts_documents
    assert docs2 in essays_and_posts_documents
    assert docs3 in essays_and_posts_documents

    assert docs11 in essays_and_posts_documents
    assert docs22 in essays_and_posts_documents
    assert docs33 in essays_and_posts_documents

    assert not set(store.scan_all('Document')).difference({blog1, blog2}}
    assert not set(store.scan_all(Document)).difference({blog11, blog22}}
    store.delete(docs2)
    store.commit()

    assert not set(store.scan_all(Document)).difference({blog1}}
    assert not set(store.scan_all('Document')).difference({blog1}}
    assert store.get_subject_by_uuid('Document', uuid1)
    assert not store.get_subject_by_uuid('Document', uuid2)



Basic Axioms:
-------------

- Every *subject name* is a root tree in the repository.
- Every *object* is stored as a git blob, but has a unique uuid which can be accessed through a special index.
- Every *indexed* **predicate** is a sub-tree containing blobs whose name in the tree is the blob_id of the original object, its value is the indexed value itself.
- Objects are stored in the tree under the path: ``SubjectName/objects/:blob_id``
- The blob-id of an **Object** can be retrieved at ``SubjectName/_ids/:uuid4``
- The *uuid4* of an **Object** can be retrieved at ``SubjectName/_uuids/:blob_id``
- Indexed predicates are stored in the tree with the path: ``SubjectName/indexes/<index name>/:blob_id``

You can `visualize <https://github.com/gabrielfalcao/gitgraph/blob/master/tests/functional/test_file_structure.py>`_ what the final file-tree `looks like <https://github.com/gabrielfalcao/gitgraph/blob/master/tests/functional/test_file_structure.py>`_ in the `file-structure functional tests <https://github.com/gabrielfalcao/gitgraph/blob/master/tests/functional/test_file_structure.py#L94>`_.

Supported Operations
--------------------

- Create/Merge subjects by ``uuid4``
- Retrieve subjects by ``uuid4``
- Retrieve subjects by ``blob_id``
- Retrieve subjects by *indexed predicates*
- Delete nodes with all their references


TODO:
-----

- Support directed relationships
- Support querying by relationships
- Use `graphene <https://github.com/graphql-python/graphene>`_ as underlying `OGM <https://en.wikipedia.org/wiki/Object_graph>`_ layer
- Concurrent ZeroMQ server request/reply as graphql interface with multiple compression level options
- Concurrent ZeroMQ server pub/sub as real-time event bus
- RESTful HTTP API as graphql interface
- socket.io HTTP API as real-time event bus
- Replication through git-push
- Merge strategies *(git flow?)*
- Use git-hooks for real time notifications

**Related GraphQL Links** for further design and implementation:

- `Nodes <http://docs.graphene-python.org/en/latest/types/objecttypes/>`_
- `Edges <http://docs.graphene-python.org/en/latest/relay/connection/>`_
- `Schema <http://docs.graphene-python.org/en/latest/types/schema/>`_
- `Querying <http://docs.graphene-python.org/en/latest/execution/dataloader/>`_
