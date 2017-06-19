# -*- coding: utf-8 -*-

from gitgraph import Subject
from gitgraph import codec

from tests.functional.helpers import list_file_tree
from tests.functional.scenarios import with_hexastore


class Tag(Subject):
    indexes = {'name'}


class Author(Subject):
    indexes = {
        'name',
        'email',
    }


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


@with_hexastore('cms')
def test_(context):
    store = context.store

    uuid1 = 'deadbeefdeadbeefdeadbeefdeadbeef'
    uuid2 = '1c3b00da1c3b00da1c3b00da1c3b00da'

    # Subject can be created
    docs1 = store.create(
        'Document',
        uuid=uuid1,
        title='Essay',
        content='content1',
    )
    docs2 = store.create(
        Document,
        uuid=uuid2,
        title='Blog',
        content='content2',
    )

    store.commit()
    store.delete(docs1)
    store.commit()
    store.merge(docs1, docs2)
    docs1 = store.create(
        'Document',
        uuid=uuid1,
        title='Essay',
        content='content1',
    )
    docs2 = store.create(
        'Document',
        uuid=uuid2,
        title='Blog',
        content='content2',
    )
    store.commit()

    docs11 = store.get_subject_by_uuid('Document', uuid1)
    docs22 = store.get_subject_by_uuid(Document, uuid2)
    docs1.should.equal(docs11)
    docs2.should.equal(docs22)

    matcher = lambda title: 'Blog' in title
    blog_documents = set(store.match_subjects_by_index('Document', 'title', matcher))
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
    list_file_tree(store.path).should.equal([
        u'Document/_ids/1c3b00da1c3b00da1c3b00da1c3b00da',
        u'Document/_ids/deadbeefdeadbeefdeadbeefdeadbeef',
        u'Document/_uuids/7fab47d1e50cfe3682a12acfce2f5208d619d5f6',
        u'Document/_uuids/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/indexes/content/7fab47d1e50cfe3682a12acfce2f5208d619d5f6',
        u'Document/indexes/content/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/indexes/title/7fab47d1e50cfe3682a12acfce2f5208d619d5f6',
        u'Document/indexes/title/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/indexes/uuid/7fab47d1e50cfe3682a12acfce2f5208d619d5f6',
        u'Document/indexes/uuid/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/objects/7fab47d1e50cfe3682a12acfce2f5208d619d5f6',
        u'Document/objects/d5af9edffb41a006f51f80695f2cf3a841f8cf96'
    ])
    store.delete(docs2)
    store.commit()
    list_file_tree(store.path).should.equal([
        u'Document/_ids/deadbeefdeadbeefdeadbeefdeadbeef',
        u'Document/_uuids/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/indexes/content/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/indexes/title/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/indexes/uuid/d5af9edffb41a006f51f80695f2cf3a841f8cf96',
        u'Document/objects/d5af9edffb41a006f51f80695f2cf3a841f8cf96'
    ])


if __name__ == '__main__':
    test()
