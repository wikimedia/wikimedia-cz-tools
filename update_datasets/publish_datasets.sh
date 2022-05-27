#!/bin/bash

set -e

# delete all old data
rm -rf /var/www/files.wikimedia.cz/datasets
mkdir /var/www/files.wikimedia.cz/datasets

for database in website other; do
	# create SQL dump of the tables
	mysqldump datasets_${database}_p | gzip > /var/www/files.wikimedia.cz/datasets/$database.sql.gz

	# dump TSVs as well
	mkdir -p /var/www/files.wikimedia.cz/datasets/$database
	while read table; do
		mysql datasets_${database}_p -e "SELECT * FROM $table" > /var/www/files.wikimedia.cz/datasets/$database/$table.tsv
	done < <(mysql -e "SHOW TABLES;" datasets_${database}_p | sed 1d)

	cd /var/www/files.wikimedia.cz/datasets
	tar czf $database.tar.gz $database
done
