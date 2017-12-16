#!/bin/sh

set -xe

isort --recursive Compiler
pycodestyle Compiler
pydocstyle Compiler
flake8 . 
find . -iname "*.rst" | xargs rstcheck --report 2
