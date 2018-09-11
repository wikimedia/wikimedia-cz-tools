#!/bin/bash

echo 'DELETE FROM revision WHERE rev_page=100 AND rev_timestamp < (CURRENT_TIMESTAMP - INTERVAL 1 YEAR);' | sql inner_wiki && php /var/www/wiki.wikimedia.cz/mw/maintenance/purgeOldText.php --wiki=inner_wiki --purge
