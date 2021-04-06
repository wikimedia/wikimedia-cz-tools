#!/bin/bash

set -e

scriptdir="`dirname \"$0\"`"

mysql < $scriptdir/update_news_web.sql
mysql < $scriptdir/update_news_category.sql
mysql < $scriptdir/update_news_tags.sql
