# -*- coding: utf-8 -*-
import os


def iter_file_tree(path):
    for root, dirs, files in os.walk(path):
        if '.git' in root:
            continue

        for name in files:
            yield os.path.join(root, name).replace("{}{}".format(path.strip(os.sep), os.sep), '')

def list_file_tree(path):
    return list(iter_file_tree(path))
