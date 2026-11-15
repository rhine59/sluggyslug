#!/bin/sh
CURRENT=`pwd`
( cd /export/home/www/htdocs/rec-and-travel/luss/Exploration/Spain/Postscript/
ls *.ps |
awk -F. -f $CURRENT/postscript.awk
)
