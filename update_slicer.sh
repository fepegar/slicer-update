#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
PYTHON_SCRIPT=$BASEDIR/update_slicer.py
yes Y | python $PYTHON_SCRIPT

