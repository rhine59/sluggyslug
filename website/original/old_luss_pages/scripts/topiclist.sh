#!/bin/sh
# display search lists

# set a couple of variables
HOME=/export/home/www/htdocs/rec-and-travel/luss
SEARCHDIR=$HOME/WWW/Search

# get type of list
eval `echo $QUERY_STRING | awk -F\& '{ for (i=1 ; i<=NF ; i++) print $i }'`

# html header
cat $SEARCHDIR/topiclist0.txt | sed s/%%list%%/$list/g

# List topics
if test "X$list" = "Xtopic"
then cat <<!
To search the database either enter the <B><TT>Code</TT></B>
or enter the <B><TT>topic</TT></B> keyword
<P>
!

cat $SEARCHDIR/subject.search | awk -F\; '
BEGIN {
	print "<TABLE><TR><TH>Code<TH>Topic<TH>Description</TR>"
}
$1 == "*" {
	if ( length($2) == 1 )
	print "<TR><TD VALIGN=TOP><B>"$2"</B><TD VALIGN=TOP>"$3"<TD><B>"$4"</B></TR>"
	else
	print "<TR><TD VALIGN=TOP>"$2"<TD VALIGN=TOP>"$3"<TD>"$4"</TR>"
}
END {
	print "</TABLE>"
}'
fi

# list countries
if test "X$list" = "Xcountry"
then cat <<!
To search the database enter the <I>Internatinal Distingishing Symbol</I>,
the www suffix, or the name of the country. Countries with entries are
listed below.
<P>
!

awk -F\; '
BEGIN {
	country = 0
	print "<TABLE><TR><TH>Country<TH>Code<TH>WWW Code<TH>Aliases</TR>"
}
# load countries file into array
FILENAME == "country.search" && $1 == "*" {
	country++
	name[country]=$2 ; abbr[country]=$3
	www[country]=$4 ; other[country]=$5
}
# load continents and display
FILENAME == "continent.search" && $1 == "*" {
	num = split ( $2 , a , "," )
	print "<TR><TD COLSPAN=4><B>" a[1]
                for ( i=2 ; i<=num ; i++ ){
                        if ( i != num ) print ", " a[i]
                        else print " or " a[i]
                }
                print "</B></TD></TR>"
# now display the list of countries
	num = split ($3 , b , "," )
	for ( i=1 ; i<=num ; i++){
		for ( j=1 ; j<=country ; j++ ){
			if ( abbr[j] == b[i] ){
				print "<TR><TD>"name[j]"<TD>"abbr[j]"<TD>"www[j]"<TD>"other[j]"</TR>"
				break
			}
		}
	}
#	print "</TR>"
}
END {
	print "</TABLE>"
}' country.search continent.search
fi

# html footer
cat $SEARCHDIR/topiclist9.txt
exit
