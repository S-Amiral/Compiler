#!/bin/sh

set -xe

pycodestyle .
pydocstyle .
isort --recursive .
flake8 .
find . -iname "*.rst" | xargs rstcheck --report 2
