#!/bin/sh

echo "Content-type: text/html"
echo
#from here on, you can echo ANY html to stdout, and it will appear on
#the browser...


/usr/local/bin/perl -e 'require "./cgi-lib.pl";&ReadParse(\*input);print &PrintVariables(\%input);' | nawk -f search.awk

