#!/bin/bash
export LIBGIT2=$VIRTUAL_ENV
wget https://github.com/libgit2/libgit2/archive/v0.26.0.tar.gz
tar xzf v0.26.0.tar.gz
cd libgit2-0.26.0/
cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2
make
make install
