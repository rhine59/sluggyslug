#!/bin/sh

echo "Content-type: text/html"
echo

nawk -f viewcaves.awk `ls ../CaveGuide/*.dba | sort`

