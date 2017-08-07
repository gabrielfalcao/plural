# -*- coding: utf-8 -*-
import os
import shutil
from plant import Node
from gitgraph import GitGraph

from sure import scenario

node = Node(__file__).dir
sandbox = node.cd('sandbox')


def with_hexastore(name, **kw):
    if not os.path.exists(sandbox.path):
        os.makedirs(sandbox.path)

    def create_store(context):
        context.store_path = sandbox.join(name)
        context.store = GitGraph(os.path.relpath(context.store_path), **kw)

    def destroy_store(context):
        if os.path.isdir(context.store_path):
            shutil.rmtree(context.store_path)

    return scenario(create_store, destroy_store)
