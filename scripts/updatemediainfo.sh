#!/bin/bash

source /var/www/tracker.wikimedia.cz/deploy/pyenv/bin/activate
python /var/www/tracker.wikimedia.cz/trackersite/manage.py update_mediainfo
deactivate
source /var/www/tracker2.wikimedia.cz/deploy/pyenv/bin/activate
python /var/www/tracker2.wikimedia.cz/trackersite/manage.py update_mediainfo
