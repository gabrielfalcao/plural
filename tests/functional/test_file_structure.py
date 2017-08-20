# -*- coding: utf-8 -*-

from plural.query import predicate
from tests.functional.helpers import list_file_tree
from tests.functional.scenarios import with_hexastore
from tests.edges import Document


@with_hexastore('cms')
def test_create_edge(context):
    store = context.store

    uuid1 = 'deadbeefdeadbeefdeadbeefdeadbeef'
    uuid2 = '1c3b00da1c3b00da1c3b00da1c3b00da'

    # Edge can be created
    docs1 = store.create_edge(
        'Document',
        uuid=uuid1,
        title='Essay',
        content='content1',
    )
    docs2 = store.create_edge(
        Document,
        uuid=uuid2,
        title='Blog',
        content='content2',
    )

    store.commit()

    store.delete(docs1)
    store.commit()
    store.merge(docs1, docs2)
    docs1 = store.create_edge(
        'Document',
        uuid=uuid1,
        title='Essay',
        content='content1',
    )
    docs2 = store.create_edge(
        'Document',
        uuid=uuid2,
        title='Blog',
        content='content2',
    )
    store.commit()

    docs11 = store.get_edge_by_uuid('Document', uuid1)
    docs22 = store.get_edge_by_uuid(Document, uuid2)
    docs1.should.equal(docs11)
    docs2.should.equal(docs22)

    matcher = lambda title: 'Blog' in title
    blog_documents = set(store.match_edges_by_index('Document', 'title', matcher))
    blog_documents.should.have.length_of(1)
    blog_documents.should.equal({docs2})

    blog_documents = set(store.match_edges_by_index('Document', 'title', predicate('title').contains('Blog')))
    blog_documents.should.have.length_of(1)
    blog_documents.should.equal({docs2})

    blog_documents = set(store.match_edges_by_index('Document', 'title', predicate('title').regex.matches('[Bb]log')))
    blog_documents.should.have.length_of(1)
    blog_documents.should.equal({docs2})

    set(store.scan_all('Document')).should.equal({
        docs1,
        docs2,
    })
    set(store.scan_all(Document)).should.equal({
        docs1,
        docs2,
    })
    sorted(list_file_tree(store.path)).should.equal(sorted([
        'Document/_ids/1c3b00da1c3b00da1c3b00da1c3b00da',
        'Document/_ids/deadbeefdeadbeefdeadbeefdeadbeef',
        'Document/_uuids/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/_uuids/fae1f98f713ead9b174a8d953ded3f70c42e6542',
        'Document/indexes/content/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/indexes/content/fae1f98f713ead9b174a8d953ded3f70c42e6542',
        'Document/indexes/title/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/indexes/title/fae1f98f713ead9b174a8d953ded3f70c42e6542',
        'Document/indexes/uuid/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/indexes/uuid/fae1f98f713ead9b174a8d953ded3f70c42e6542',
        'Document/objects/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/objects/fae1f98f713ead9b174a8d953ded3f70c42e6542',
    ]))
    store.delete(docs2)
    store.commit()
    sorted(list_file_tree(store.path)).should.equal(sorted([
        'Document/_ids/deadbeefdeadbeefdeadbeefdeadbeef',
        'Document/_uuids/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/indexes/content/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/indexes/title/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/indexes/uuid/c5a61004c0bab3a5ee1244e719ade9ebd381f892',
        'Document/objects/c5a61004c0bab3a5ee1244e719ade9ebd381f892'
    ]))


@with_hexastore('cms-bare', bare=True)
def test_bare(context):
    store = context.store

    uuid1 = 'deadbeefdeadbeefdeadbeefdeadbeef'
    uuid2 = '1c3b00da1c3b00da1c3b00da1c3b00da'

    # Edge can be created
    docs1 = store.create_edge(
        'Document',
        uuid=uuid1,
        title='Essay',
        content='content1',
    )
    docs2 = store.create_edge(
        Document,
        uuid=uuid2,
        title='Blog',
        content='content2',
    )

    store.commit()

    store.delete(docs1)
    store.commit()
    store.merge(docs1, docs2)
    docs1 = store.create_edge(
        'Document',
        uuid=uuid1,
        title='Essay',
        content='content1',
    )
    docs2 = store.create_edge(
        'Document',
        uuid=uuid2,
        title='Blog',
        content='content2',
    )
    store.commit()

    docs11 = store.get_edge_by_uuid('Document', uuid1)
    docs22 = store.get_edge_by_uuid(Document, uuid2)
    docs1.should.equal(docs11)
    docs2.should.equal(docs22)

    matcher = lambda title: 'Blog' in title
    blog_documents = set(store.match_edges_by_index('Document', 'title', matcher))
    blog_documents.should.have.length_of(1)
    blog_documents.should.equal({docs2})
    set(store.scan_all('Document')).should.equal({
        docs1,
        docs2,
    })
    set(store.scan_all(Document)).should.equal({
        docs1,
        docs2,
    })
    list_file_tree(store.path).should.have.length_of(36)
    store.delete(docs2, auto_commit=True)
    list_file_tree(store.path).should.have.length_of(45)
