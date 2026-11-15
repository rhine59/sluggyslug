#!/bin/sh
umask 0


echo "Content-type: text/html"
echo

/usr/local/bin/perl -e 'require "./cgi-lib.pl";&ReadParse(\*input);print &PrintVariables(\%input);' | nawk -f cavepasswd.awk

