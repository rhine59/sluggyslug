#!/bin/sh

echo $LINE
eval `echo $LINE | awk -F\& '{ print "fields="NF ; for (i=1 ; i<=NF ; i++) print $i } '`

echo '$fields='$fields
echo '$password='$password
echo '$text='$text
echo '$choice='$choice
exit
