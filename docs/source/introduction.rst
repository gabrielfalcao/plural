.. _Introduction:


.. highlight:: bash


Introduction
------------

Installing
~~~~~~~~~~

.. code:: bash

   pip install gitgraph

Concepts
~~~~~~~~

Influenced by the `hexastore <http://www.vldb.org/pvldb/1/1453965.pdf>`_ paper.

- Every *subject name* is a root tree in the repository.
- Every *object* is stored as a git blob, but has a unique uuid which can be accessed through a special index.
- Every *indexed* **predicate** is a sub-tree containing blobs whose name in the tree is the blob_id of the original object, its value is the indexed value itself.
- Objects are stored in the tree under the path: ``SubjectName/objects/:blob_id``
- The blob-id of an **Object** can be retrieved at ``SubjectName/_ids/:uuid4``
- The *uuid4* of an **Object** can be retrieved at ``SubjectName/_uuids/:blob_id``
- Indexed predicates are stored in the tree with the path: ``SubjectName/indexes/<index name>/:blob_id``


Supported Operations
~~~~~~~~~~~~~~~~~~~~

- Create/Merge subjects by ``uuid4``
- Retrieve subjects by ``uuid4``
- Retrieve subjects by ``blob_id``
- Retrieve subjects by *indexed predicates*
- Delete nodes with all their references
