#!/bin/sh
umask 0

echo "Content-type: text/html"
echo

FILENAME=`/usr/local/bin/perl -e 'require "./cgi-lib.pl";&ReadParse(\*input);print &PrintVariables(\%input);' |\
nawk '$1=="filename" {filename=$3;next}\
 		     {lines[l++]=$0}\
	 END {\
		file="../CaveGuide/"filename;
		if (filename) for (i=0;i<l;i++) print lines[i] > file;\
		print file;\
	     }'`

if [ -f "$FILENAME" ] ; then
	echo "<H3>This entry has been added to the Cave Guide...</H3>"
	nawk -f ./viewer.awk $FILENAME
else
	echo "<H1>Lancaster University Speleological Society - Cave Guide</H1>"
	echo "<H3>Sorry the password was wrong, try again.<H3>"
fi

echo "</BODY>"
