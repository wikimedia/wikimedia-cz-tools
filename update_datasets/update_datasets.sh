#!/bin/bash

set -e

scriptdir="`dirname \"$0\"`"
cd $scriptdir

for folder in website other; do
	cd $folder
	for sql in *.sql; do
		mysql < $sql
	done
	cd $OLDPWD
done
