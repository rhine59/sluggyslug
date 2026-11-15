#! /bin/sh
# script to analyse Web log
# David Nichols 
# (1994, 1995)
# 

# set file to work on
AAILOG="../log-luss.html"


DATE=`which date`

rm "$AAILOG"
echo Removed existing logs $NEWLINE


echo "<HTML>" > $AAILOG
echo "<HEAD>" >> $AAILOG
echo "<TITLE>Lancaster University Speleological Society - WWW Access Log</TITLE>" >> $AAILOG
echo "<H1>Lancaster University Speleological Society - WWW Access Log</H1>" >> $AAILOG
echo "</HEAD>" >> $AAILOG

echo "<BODY>" >> $AAILOG

echo A log of all accesses of the Lancaster University Speleological Pages $NEWLINE >> $AAILOG
echo Most local accesses have been filtered out. $NEWLINE >> $AAILOG
echo This log was last run at >> $AAILOG
$DATE >> $AAILOG
echo $NEWLINE $NEWLINE >> $AAILOG


# the awk bit strips out local accesses because
# our DNS isn't set up correctly so we get
# dolphin instead of dolphin.comp.lancs.ac.uk

echo "<H6>" >> $AAILOG
cat  /export/home/www/etc/httpd_1.2/logs/access_log | grep -v lancs | grep -v '148.88' | grep luss |  awk -F' ' '{ if ( $1 ~ '/[.]/' ) print $0 }' >> $AAILOG
echo "</H6>" >> $AAILOG
echo "</BODY>" >> $AAILOG


echo "</BODY>" >> $AAILOG
echo "<ADDRESS>" >> $AAILOG
echo "<HR>LUSS@lancaster.ac.uk" >> $AAILOG
echo "</ADDRESS>" >> $AAILOG

echo "<HR>" >> $AAILOG
echo "See Also..." >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/index.html">Toplevel</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Notices/index.html">Notices</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Trivia/index.html">Trivia</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Articles/index.html">Articles</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Pictures/index.html">Pictures</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Maps/index.html">Maps</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html">Cave Guide</A>" >> $AAILOG
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html">WWW</A>" >> $AAILOG

echo Completed main log $NEWLINE


# run the graph update
stats.sh
echo Completed stats $NEWLINE

# set process going again 
# this log is not atlog, so don't invoke a new process
at -ms now +1 day < log.sh 
