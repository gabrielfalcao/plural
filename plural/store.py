# -*- coding: utf-8 -*-
#
# <Plural - Git-powered graph database library>
# Copyright (C) <2017>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import json
import pygit2
from fnmatch import fnmatch

from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import GIT_RESET_HARD
from pygit2 import init_repository
from pygit2 import IndexEntry
from pygit2 import Signature
from plural.models.meta.edges import edge_has_index
from plural.models.meta.vertices import vertex_has_index
from plural.models.meta.edges import is_edge_subclass
from plural.models.meta.vertices import is_vertex_subclass
from plural.models.edges import Edge
from plural.models.vertices import Vertex
from plural.models.edges import resolve_edge_name
from plural.models.vertices import resolve_vertex_name
from plural.util import generate_uuid
from plural.util import serialize_commit
from plural.util import AutoCodec


class PluralStore(object):
    """Data store that manipulates a single git repository

    :param path: ``bytes`` - the path to the git repository ``string``
    :param bare: ``bool`` - manipulate git objects only
    :param author_name: ``unicode`` - the name of the default git author.
    :param author_email: ``unicode`` - the email of the default git author.
    """
    def __init__(self, path=None, bare=False,
                 author_name='hexastore',
                 author_email='hexastore@git',
                 default_branch='refs/heads/master',
                 repository=None):
        path = path or self.__class__.__name__.lower()
        self.path = path
        self.bare = bare
        self.repository = repository or init_repository(path, bare=bare)
        self.author = Signature(author_name, author_email)
        self.commiter = Signature(author_name, author_email)
        self.queries = []
        self.default_branch = default_branch

    def add_remote(self, name, url):
        """adds a remote repository

        :param name: ``bytes``
        :param url: ``bytes``
        """
        self.repository.remotes.create(name, url)

    def serialize(self, obj):
        """serializes an object, meant for internal use only.

        :param obj: a hashable object
        :returns: ``string``
        """
        default = AutoCodec().encode
        return json.dumps(obj, sort_keys=True, default=default)

    def deserialize(self, string):
        """deserialize a string into an object, meant for internal use only.

        :param string: a hashable object
        :returns: ``a hashable object``
        """
        return json.loads(string)

    def iter_versions(self, branch='master'):
        """iterates over all the commits of the repo
        :param branch: the branch name
        :returns: an iterator of dictionaries with commit metadata
        """
        for commit in self.repository.walk(self.repository.head.target, pygit2.GIT_SORT_TOPOLOGICAL):
            yield serialize_commit(commit)

    def get_versions(self, branch='master'):
        """same :py:meth:`as iter_versions` but returns a list
        :returns: a list
        """
        results = list(self.iter_versions(branch))
        return results

    def add_spo(self, edge, predicate, data):
        """creates a staged entry of edge, predicate and object

        :param edge:
        :param predicate:
        :param data:
        :returns: ``bytes`` - the blob id
        """
        edge = resolve_edge_name(edge)
        blob_id = self.repository.create_blob(data)
        entry = IndexEntry(os.path.join(edge, predicate), blob_id, GIT_FILEMODE_BLOB)
        self.repository.index.add(entry)
        return blob_id

    def create(self, element, **obj):
        if is_edge_subclass(element):
            new = self.create_edge(element, **obj)
            self.queries.append(
                ' '.join(map(bytes, ['CREATE EDGE', repr(new)]))
            )
            return new
        elif is_vertex_subclass(element):
            new = self.create_vertex(element, **obj)
            self.queries.append(
                ' '.join(map(bytes, ['CREATE VERTEX', repr(new)]))
            )
            return new

    def create_vertex(self, vertex, **obj):
        """creates a staged vertex entry including its indexed fields.

        :param vertex: a string or a :py:class:`Vertex` subclass reference
        :param ``**kw``: the field values
        :returns: an instance of the given vertex

        """
        vertex = resolve_vertex_name(vertex)
        predicate_ids = []

        vertex_uuid = obj.pop('uuid', generate_uuid())
        obj['uuid'] = vertex_uuid

        vertex_data = self.serialize(obj)
        object_hash = bytes(pygit2.hash(vertex_data))
        object_path = os.path.join(vertex, 'objects')

        id_path = os.path.join(vertex, '_ids')
        uuid_path = os.path.join(vertex, '_uuids')

        original_obj = obj.copy()
        origin = obj.pop('origin')
        target = obj.pop('target')

        indexes = {}
        for key in obj.keys():
            value = obj.get(key, None)
            if vertex_has_index(vertex, key):
                indexes[key] = value

            predicate_path = os.path.join(vertex, 'indexes', key)
            predicate_ids.append(self.add_spo(predicate_path, object_hash, value))

        self.add_spo(id_path, vertex_uuid, object_hash)
        self.add_spo(uuid_path, object_hash, vertex_uuid)

        origin_name = resolve_edge_name(origin)
        target_name = resolve_edge_name(target)
        RelationhipModel = Vertex.definition(vertex)

        label = RelationhipModel.label
        # call('Car/incoming/bought_by/Person', 'chuck-uuid', 'car-uuid'),
        # call('___vertices___/Car/bought_by/Person', 'chuck-uuid', 'car-uuid'),
        path_templates = {
            'incoming': '{to}/incoming/{label}/{from}',
            'outgoing': '{from}/outgoing/{label}/{to}',
            'indirect': '{}/indirect/{label}/{}',
        }
        vertex_path_template = path_templates[RelationhipModel.direction]

        ctx = {
            'label': label
        }
        direction = RelationhipModel.direction
        # self.add_spo(object_path, object_hash, vertex_data)

        if direction == 'incoming':
            from_uuid = origin.uuid
            ctx['from'] = origin_name
            to_uuid = target.uuid
            ctx['to'] = target_name
            vertex_path = vertex_path_template.format(**ctx)
            self.add_spo(vertex_path, from_uuid, to_uuid)

        elif direction == 'outgoing':
            from_uuid = target.uuid
            ctx['from'] = target_name
            to_uuid = origin.uuid
            ctx['to'] = origin_name
            vertex_path = vertex_path_template.format(**ctx)
            self.add_spo(vertex_path, from_uuid, to_uuid)

        elif direction == 'indirect':
            from_uuid = target.uuid
            to_uuid = origin.uuid

            path = vertex_path_template.format(target_name, origin_name, **ctx)
            self.add_spo(path, from_uuid, to_uuid)

            path = vertex_path_template.format(origin_name, target_name, **ctx)
            self.add_spo(path, to_uuid, from_uuid)

        return RelationhipModel.from_data(vertex, **original_obj)

    def create_edge(self, edge, **obj):
        """creates a staged edge entry including its indexed fields.

        :param edge: a string or a :py:class:`Edge` subclass reference
        :param ``**kw``: the field values
        :returns: an instance of the given edge

        """
        predicate_ids = []

        edge = resolve_edge_name(edge)
        edge_uuid = obj.pop('uuid', generate_uuid())
        obj['uuid'] = edge_uuid

        edge_data = self.serialize(obj)
        object_hash = bytes(pygit2.hash(edge_data))
        object_path = os.path.join(edge, 'objects')

        id_path = os.path.join(edge, '_ids')
        uuid_path = os.path.join(edge, '_uuids')

        indexes = {}
        for key in obj.keys():
            value = obj.get(key, None)
            if edge_has_index(edge, key):
                indexes[key] = value

            predicate_path = os.path.join(edge, 'indexes', key)
            predicate_ids.append(self.add_spo(predicate_path, object_hash, value))

        self.add_spo(object_path, object_hash, edge_data)
        self.add_spo(id_path, edge_uuid, object_hash)
        self.add_spo(uuid_path, object_hash, edge_uuid)

        return Edge.from_data(edge, **obj)

    def save_nodes(self, *nodes):
        """creates staged entries for all the given edge nodes, regardless of type

        :param ``*nodes``: a list of edge instances
        """

        result = []
        for node in nodes:
            n = self.create_edge(node.__class__.__name__, **node.to_dict())
            result.append(n)

        return result

    def merge(self, *nodes, **kw):
        """saves and commits all given nodes

        :param ``*nodes``: a list of edge instances
        :param auto_commit: ``bool`` - default: ``True``
        :returns: a list with the created nodes
        """
        auto_commit = kw.pop('auto_commit', True)
        result = self.save_nodes(*nodes)
        if auto_commit:
            self.commit()
        return result

    def trace_path(self, entries):
        return map(lambda entry: (entry.path, bytes(entry.oid)), entries)

    def glob(self, pattern, treeish=None):
        treeish = treeish or self.repository.index
        return filter(lambda entry: fnmatch(entry.path, pattern), treeish)

    def scan_all(self, edge_name=None, treeish=None, pattern='*'):
        """scans all nodes

        :returns: a generator that produces :py:class:`Edge` instances with the scanned data
        """
        edge_name = resolve_edge_name(edge_name)
        treeish = treeish or self.repository.index
        pattern = os.path.join(edge_name, 'objects', pattern)
        for entry in self.glob(pattern):
            blob = self.repository[entry.oid]
            data = self.deserialize(blob.data)
            yield Edge.from_data(edge_name, **data)

    def delete(self, *nodes, **kw):
        """deletes and (optionally) commits all given nodes

        :param ``*nodes``: a list of edge instances to be deleted
        :param auto_commit: ``bool`` - default: ``False``
        :returns: a list with the deleted nodes
        """
        auto_commit = kw.pop('auto_commit', False)
        deleted = []
        for node in nodes:
            for path, oid in self.trace_path(self.glob('*{}*'.format(node.uuid))):
                map(self.repository.index.remove, node.get_related_blob_paths(self.repository))
                self.queries.append(
                    ' '.join(map(bytes, ['DELETE', node]))
                )
            deleted.append(node)

        if auto_commit:
            self.commit()

        return nodes

    def get_edge_by_uuid(self, edge_name, uuid):
        """retrieves a edge by id

        :param edge_name: the edge name or type
        :param uuid: the uuid value
        """
        edge_name = resolve_edge_name(edge_name)
        pattern = os.sep.join([edge_name, '_ids', uuid])
        for entry in self.glob(pattern):
            edge_blob_id = self.repository[entry.oid].data
            blob = self.repository[edge_blob_id]
            return Edge.from_data(edge_name, **self.deserialize(blob.data))

    def get_vertex_by_uuid(self, vertex_name, uuid):
        """retrieves a vertex by id

        :param vertex_name: the vertex name or type
        :param uuid: the uuid value
        """
        vertex_name = resolve_vertex_name(vertex_name)
        pattern = os.sep.join([vertex_name, '_ids', uuid])
        for entry in self.glob(pattern):
            vertex_blob_id = self.repository[entry.oid].data
            blob = self.repository[vertex_blob_id]
            return Vertex.from_data(vertex_name, **self.deserialize(blob.data))

    def match_edges_by_index(self, edge_name, field_name, match_callback):
        """retrieves multiple edges by indexed field

        :param edge_name: the edge name or type
        :param uuid: the uuid value
        """
        edge_name = resolve_edge_name(edge_name)
        pattern = os.sep.join([edge_name or '*', 'indexes', '*'])
        # for index, oid in filter(lambda (index, oid): field_name in index, self.glob(pattern)):
        for index, oid in self.trace_path(self.glob(pattern)):
            path, blob_id = os.path.split(index)
            edge_name = path.split(os.sep)[0]
            value = self.repository[oid].data
            if match_callback(value):
                blob = self.repository[blob_id]
                data = self.deserialize(blob.data)
                Definition = Edge.definition(edge_name)
                yield Definition(**data)

    def match_vertices_by_index(self, vertex_name, field_name, match_callback):
        """retrieves multiple vertices by indexed field

        :param vertex_name: the vertex name or type
        :param uuid: the uuid value
        """
        vertex_name = resolve_vertex_name(vertex_name)
        pattern = os.sep.join([vertex_name or '*', 'indexes', '*'])
        # for index, oid in filter(lambda (index, oid): field_name in index, self.glob(pattern)):
        for index, oid in self.trace_path(self.glob(pattern)):
            path, blob_id = os.path.split(index)
            vertex_name = path.split(os.sep)[0]
            value = self.repository[oid].data
            if match_callback(value):
                blob = self.repository[blob_id]
                data = self.deserialize(blob.data)
                Definition = Vertex.definition(vertex_name)
                yield Definition(**data)

    def commit(self, query=None):
        """creates a commit with the staged objects"""
        author = None

        if not query:
            query = '\n'.join(sorted(set(self.queries)))

        # commit
        tree_id = self.repository.index.write_tree()
        parent_commits = []
        if self.repository.references.objects:
            parent_commits = [self.repository.head.target]

        commit_id = self.repository.create_commit(
            self.default_branch,
            author or self.author,
            self.commiter,
            query,
            tree_id,
            parent_commits,
        )
        self.queries = []
        self.repository.head.set_target(commit_id)
        if not self.bare:
            self.repository.reset(commit_id, GIT_RESET_HARD)
        return commit_id
