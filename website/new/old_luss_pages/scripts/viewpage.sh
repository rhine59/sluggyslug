#!/bin/sh
 
echo "Content-type: text/html"
echo
 
nawk -f viewer.awk $QUERY_STRING
 
