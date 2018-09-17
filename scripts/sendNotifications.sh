#!/bin/bash

source /var/www/tracker.wikimedia.cz/deploy/pyenv/bin/activate
echo "select * from tracker_notification" | /home/urbanecm/bin/sql tracker_main > /home/urbanecm/tmp/last_tracker_notification_tracker_main.txt
echo "select * from tracker_notification" | /home/urbanecm/bin/sql tracker_test > /home/urbanecm/tmp/last_tracker_notification_tracker_test.txt
python /var/www/tracker.wikimedia.cz/trackersite/manage.py sendnotifications
python /var/www/tracker2.wikimedia.cz/trackersite/manage.py sendnotifications
