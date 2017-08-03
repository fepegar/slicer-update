#!/usr/bin/env bash

source activate py2

BASEDIR=$(dirname "$0")
PYTHON_SCRIPT=$BASEDIR/update_slicer.py
yes Y | $PYTHON_SCRIPT $1

source deactivate