#!/bin/sh
# display and process search.

# set a couple of variables
HOME=/export/home/www/htdocs/rec-and-travel/luss
SEARCHDIR=$HOME/WWW/Search

# testing only
# QUERY_STRING="password=Derek&screen=main&option=1&option=2"

# get variables from command line
eval `echo $QUERY_STRING | awk -F\& '
	BEGIN { option = "" }
	{ print "fields="NF
		for (i=1 ; i<=NF ; i++) {
			split($i , a , "=")
			if ( a[1] == "password" )
				print $i
			if ( a[1] == "screen" )
				print $i
			if ( a[1] == "search" )
				print $i
			if ( a[1] == "option" ){
				if ( option == "" )
					option = a[2]
				else
					option = option "," a[2]
			}
		}
	}
	END { print "option="option }'`

# is the password valid?
if test "%$password%" = "%Derek%"
then
	valid="ok"
	VALID=YES
else
	valid="fail"
	VALID=
fi

SEARCH=`echo $search | sed -f $SEARCHDIR/convert.sed`

# HTML header
cat $SEARCHDIR/topic0.txt

# dispay the screen and the password
# set the screen
screen="main"

sed -e s/%%password%%/$password/g -e s/%%valid%%/$valid/g \
	-e s/%%screen%%/$screen/g -e s/%%search%%/$SEARCH/g \
	$SEARCHDIR/topic1.txt

# to lower case : move ' and ' and ' or ' to '+' and ','
SEARCH=`echo $SEARCH | sed -f $SEARCHDIR/tolower.sed \
	-e 's/ and /+/g' -e 's/ or /,/g' -e 's/ not /!/'`

# make into sensible fields
SEARCH=`echo $SEARCH | awk '
{
	line=""
	sep=""
	num = split( $1 , a , "+" )
	for ( i=1 ; i <= num ; i++ ){
		if ( a[i] != "" ){
			line=line sep a[i]
			sep="+"
		}
	}
	string=""
	sep=""
	num = split ( line , b , "," )
	for ( i=1 ; i<=num ; i++ ){
		if ( b[i] != "" ){
			string=string sep b[i]
			sep=","
		}
	}
	search=""
	sep=""
	num = split ( string , c , "!" )
	for ( i=1 ; i <=num ; i++ ){
		if ( c[i] != "" ){
			search=search sep c[i]
			sep="!"
		}
	}
	print search
}'`

# do the search
if test -n $SEARCH
then
	search.sh $SEARCH
fi
	
# display the environment
# set |sed -e 'a\
# <BR>'
echo "QUERY_STRING="$QUERY_STRING"<BR>"
echo "<TABLE BORDER=0 CELLPADDING=20><TR><TD VALIGN=TOP>"
echo "password="$password"<BR>"
echo "screen="$screen"<BR>"
echo "option="$option"<BR>"
echo "search="$search"<BR>"
echo "</TD><TD VALIGN=TOP>"
echo "fields="$fields"<BR>"
echo "valid="$valid"<BR>"
echo "VALID="$VALID"<BR>"
echo "SEARCH="$SEARCH"<BR>"
echo "number="$number"<BR>"
echo "</TD></TR></TABLE>"

# HTML footer
cat $SEARCHDIR/topic9.txt
exit
