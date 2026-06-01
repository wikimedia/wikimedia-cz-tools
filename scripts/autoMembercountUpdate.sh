#!/bin/bash

set -e

pocetRadnychClenu=$(echo 'select count(*) from user where user_id not in (select bt_user from block join block_target on bl_target=bt_id where bt_user is not null) and user_id not in (select ug_user from user_groups where ug_group in ("bot", "techaccount", "nonmember"))' | mysql wikiusers | sed 1d)

# Get things from wiki
pocetSymClenu=$(php /var/www/wikis/mw/maintenance/run.php getText.php --wiki=innerwiki "Členové/Počet sympatizujících členů")
pocetCestClenu=$(php /var/www/wikis/mw/maintenance/run.php getText.php --wiki=innerwiki "Členové/Počet čestných členů")

echo $(($pocetSymClenu+$pocetCestClenu+$pocetRadnychClenu)) | php /var/www/wikis/mw/maintenance/run.php edit.php --wiki=innerwiki --summary="Robot: Aktualizace počtu členů" --bot --minor --quiet --user=UrbanecmBot Členové/Celkový_počet_členů
echo $pocetRadnychClenu | php /var/www/wikis/mw/maintenance/run.php edit.php --wiki=innerwiki --summary="Robot: Aktualizace počtu členů" --bot --minor --quiet --user=UrbanecmBot Členové/Počet_řádných_členů
echo Členové | php /var/www/wikis/mw/maintenance/run.php purgePage.php --wiki=innerwiki -q
