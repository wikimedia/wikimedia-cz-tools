#!/bin/bash

pocetRadnychClenu=$(echo 'select count(*) from user where user_name not in (select ipb_address from ipblocks) and user_id not in (select ug_user from user_groups where ug_group in ("bot", "techaccount"));' | mysql --defaults-extra-file=~/.sqlconf/inner_wiki.conf wikiusers | sed 1d)

# Get things from wiki
pocetSymClenu=$(php /var/www/wiki.wikimedia.cz/mw/maintenance/getText.php --wiki=inner_wiki "Členové/Počet sympatizujících členů")
pocetCestClenu=$(php /var/www/wiki.wikimedia.cz/mw/maintenance/getText.php --wiki=inner_wiki "Členové/Počet čestných členů")

echo $(($pocetSymClenu+$pocetCestClenu+$pocetRadnychClenu)) | php /var/www/wiki.wikimedia.cz/mw/maintenance/edit.php --wiki=inner_wiki --summary="Robot: Aktualizace počtu členů" --bot --minor --user=UrbanecmBot Členové/Celkový_počet_členů
echo $pocetRadnychClenu | php /var/www/wiki.wikimedia.cz/mw/maintenance/edit.php --wiki=inner_wiki --summary="Robot: Aktualizace počtu členů" --bot --minor --user=UrbanecmBot Členové/Počet_řádných_členů
echo Členové | php /var/www/wiki.wikimedia.cz/mw/maintenance/purgePage.php --wiki=inner_wiki -q
echo $pocetRadnychClenu | php  /var/www/www.wikimedia.cz/mw/maintenance/edit.php --wiki=pub_wiki --summary="Robot: Aktualizace počtu členů" --bot --minor --user=UrbanecmBot Lidé/Počet_řádných_členů
echo Lidé | php /var/www/www.wikimedia.cz/mw/maintenance/purgePage.php --wiki=pub_wiki -q
