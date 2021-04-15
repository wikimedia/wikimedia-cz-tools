#!/bin/bash

mkdir -p /var/www/files.wikimedia.cz/datasets

mysqldump wmcz_reports_p | gzip > /var/www/files.wikimedia.cz/datasets/wmcz_reports_p.sql.gz
