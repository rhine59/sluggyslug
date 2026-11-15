#!/bin/sh
umask 0
echo "Content-type: image/gif"
echo ""

read NUM < counter.dat
NUM=`expr $NUM + 1`
echo $NUM > counter.dat
./texttogif "(There have been $NUM accesses to this site since 24th April 1995)"
