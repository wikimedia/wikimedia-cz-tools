#!/bin/bash

ssh masaryk /home/urbanecm/bin/sqldump tracker_main | mysql tracker_prod # Sync production database
cd /home/urbanecm/Documents/git/wmcz/gsuite-tools/update_tracker_users
source ../venv/bin/activate
python update_tracker_users.py
