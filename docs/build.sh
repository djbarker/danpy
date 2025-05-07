#!/usr/bin/bash

make clean

# Note: the paths following ../python/boltzmann are excludes.
sphinx-apidoc -ef \
    -o source/api \
    --templatedir=source/_templates \
    ../src/danpy \

make html