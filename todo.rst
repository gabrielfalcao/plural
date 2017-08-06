TODO:
-----

- Support directed relationships
- Support querying by relationships
- Support ``store.rollback()`` as counterpart of ``.commit()``
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
