#!/bin/bash

source /var/www/$1/deploy/pyenv/bin/activate
python /var/www/$1/trackersite/manage.py process_tasks
