#!/bin/bash

scriptdir="`dirname \"$0\"`"
cd $scriptdir
source ../venv/bin/activate
python update_teamdrive_list.py
