TODO:
-----

- Support directed relationships
- Support querying by relationships
- Support ``store.rollback()`` as counterpart of ``.commit()``
- Use `json-regex graph-query-language <https://jrgql.github.io/>`_
- Build web UI with `react digraph <https://github.com/uber/react-digraph>`_
- Concurrent ZeroMQ server request/reply as graphql interface with multiple compression level options
- Concurrent ZeroMQ server pub/sub as real-time event bus
- RESTful HTTP API as graphql interface
- socket.io HTTP API as real-time event bus
- Replication through git-push
- Merge strategies *(git flow?)*
- Use git-hooks for real time notifications
- Allow arguments in codecs, i.e.: ``codec.DateTime(utc=True, _now=True)``
