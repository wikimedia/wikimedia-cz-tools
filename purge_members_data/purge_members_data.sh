#!/bin/bash

echo 'DELETE FROM revision WHERE rev_page=100 AND rev_timestamp < (CURRENT_TIMESTAMP - INTERVAL 2 YEAR);' | mysql innerwiki && php /var/www/wikis/mw/current/maintenance/run.php purgeOldText.php --wiki=innerwiki --purge
