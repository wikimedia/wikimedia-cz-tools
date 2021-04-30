#!/bin/bash

mkdir -p /var/www/files.wikimedia.cz/datasets/web-posts

mysqldump wmcz_web_posts_p | gzip > /var/www/files.wikimedia.cz/datasets/web-posts/wmcz_web_posts_p.sql.gz

for table in blogposts news_category news_tags news_web; do
	mysql wmcz_web_posts_p -e "SELECT * FROM $table" > /var/www/files.wikimedia.cz/datasets/web-posts/$table.tsv
done

cd /var/www/files.wikimedia.cz/datasets
tar czf data.tar.gz web-posts
mv data.tar.gz web-posts
