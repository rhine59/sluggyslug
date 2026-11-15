#! /bin/sh
# script to produce stats

GRAPH_FILE="../log-graph.html"

rm "$GRAPH_FILE"

echo "<HTML>" >> $GRAPH_FILE
echo "<HEAD>" >> $GRAPH_FILE
echo "<TITLE>Lancaster University Speleological Society - WWW Access Log</TITLE>" >> $GRAPH_FILE
echo "<H1>Lancaster University Speleological Society - WWW Access Log</H1>" >> $GRAPH_FILE
echo "</HEAD>" >> $GRAPH_FILE

echo "<BODY>" >> $GRAPH_FILE

echo Ascii Graph Of Non-local Accesses to LUSS WWW Pages, The X axis is number of reads and the y axis is the day in the month. $NEWLINE >> $GRAPH_FILE
echo Start Date is 22nd May 1995 >> $GRAPH_FILE
echo $NEWLINE $NEWLINE >> $GRAPH_FILE


echo "<H6>" >> $GRAPH_FILE
#echo "<PRE>" >> $GRAPH_FILE

cat  /export/home/www/etc/httpd_1.2/logs/access_log | grep -v lancs | grep -v '148.88' | grep luss |  awk -F' ' '{ if ( $1 ~ '/[.]/' ) print $0 }' >> log-luss

grep `date | awk -F\  '{print Sep"/"$6}'` log-luss | awk -F\[ '{print $2}' |
awk -F\/ '{print $1}' | uniq -c | awk '{print $2" " $1 }' | awk '{printf("%s", $1); for (i=0;i<$2;i++) printf("|");printf("<BR>\n")}' >> $GRAPH_FILE

rm log-luss

echo "</H6>" >> $GRAPH_FILE
#echo "</PRE>" >> $GRAPH_FILE

echo "</BODY>" >> $GRAPH_FILE
echo "<ADDRESS>" >> $GRAPH_FILE
echo "<HR>LUSS@lancaster.ac.uk" >> $GRAPH_FILE
echo "</ADDRESS>" >> $GRAPH_FILE

echo "<HR>" >> $GRAPH_FILE
echo "See Also..." >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/index.html">Toplevel</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Notices/index.html">Notices</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Trivia/index.html">Trivia</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Articles/index.html">Articles</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Pictures/index.html">Pictures</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Maps/index.html">Maps</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html">Cave Guide</A>" >> $GRAPH_FILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html">WWW</A>" >> $GRAPH_FILE


echo Finished main stats

