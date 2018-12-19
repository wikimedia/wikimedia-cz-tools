#!/bin/bash

pocetRadnychClenu=$(echo 'select count(*) from user where user_name not in (select ipb_address from ipblocks) and user_id not in (select ug_user from user_groups where ug_group in ("bot", "techaccount"));' | mysql wikiusers | sed 1d)

# Get things from wiki
pocetSymClenu=$(php /var/www/wikis/mw/maintenance/getText.php --wiki=innerwiki "Členové/Počet sympatizujících členů")
pocetCestClenu=$(php /var/www/wikis/mw/maintenance/getText.php --wiki=innerwiki "Členové/Počet čestných členů")

echo $(($pocetSymClenu+$pocetCestClenu+$pocetRadnychClenu)) | php /var/www/wikis/mw/maintenance/edit.php --wiki=innerwiki --summary="Robot: Aktualizace počtu členů" --bot --minor --user=UrbanecmBot Členové/Celkový_počet_členů
echo $pocetRadnychClenu | php /var/www/wikis/mw/maintenance/edit.php --wiki=innerwiki --summary="Robot: Aktualizace počtu členů" --bot --minor --user=UrbanecmBot Členové/Počet_řádných_členů
echo Členové | php /var/www/wikis/mw/maintenance/purgePage.php --wiki=innerwiki -q
echo $pocetRadnychClenu | php  /var/www/wikis/mw/maintenance/edit.php --wiki=pubwiki --summary="Robot: Aktualizace počtu členů" --bot --minor --user=UrbanecmBot Lidé/Počet_řádných_členů
echo Lidé | php /var/www/wikis/mw/maintenance/purgePage.php --wiki=pubwiki -q
