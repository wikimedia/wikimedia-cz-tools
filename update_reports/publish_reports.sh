#!/bin/bash

mkdir -p /var/www/files.wikimedia.cz/datasets/wmcz_reports

mysqldump wmcz_reports_p | gzip > /var/www/files.wikimedia.cz/datasets/wmcz_reports/wmcz_reports_p.sql.gz

for table in blogposts news_category news_tags news_web; do
	mysql wmcz_reports_p -e "SELECT * FROM $table" > /var/www/files.wikimedia.cz/datasets/wmcz_reports/$table.tsv
done

cd /var/www/files.wikimedia.cz/datasets
tar czf data.tar.gz wmcz_reports
mv data.tar.gz wmcz_reports
