#!/bin/bash

mkdir -p /var/www/files.wikimedia.cz/datasets

mysqldump wmcz_web_posts_p | gzip > /var/www/files.wikimedia.cz/datasets/web-posts/wmcz_web_posts_p.sql.gz
