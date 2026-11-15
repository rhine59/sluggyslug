#! /bin/sh
# script to analyse Web  

# set file to work on
LOGFILE="../log-luss.html"


DATE=`which date`

rm "$LOGFILE"
echo Removed existing logs $NEWLINE


echo "<HTML>" > $LOGFILE
echo "<HEAD>" >> $LOGFILE
echo "<TITLE>Lancaster University Speleological Society - WWW Access Log</TITLE>" >> $LOGFILE
echo "<H1>Lancaster University Speleological Society - WWW Access Log</H1>" >> $LOGFILE
echo "</HEAD>" >> $LOGFILE

echo "<BODY>" >> $LOGFILE

echo A log of all accesses of the Lancaster University Speleological Pages $NEWLINE >> $LOGFILE
echo Most local accesses have been filtered out. $NEWLINE >> $LOGFILE
echo This log was last run at >> $LOGFILE
$DATE >> $LOGFILE
echo $NEWLINE $NEWLINE >> $LOGFILE


# the awk bit strips out local accesses because
# our DNS isn't set up correctly so we get
# dolphin instead of dolphin.comp.lancs.ac.uk

echo "<H6>" >> $LOGFILE
cat  /export/home/www/etc/httpd_1.2/logs/access_log | grep -v lancs | grep -v '148.88' | grep luss |  awk -F' ' '{ if ( $1 ~ '/[.]/' ) print $0 }' >> $LOGFILE
echo "</H6>" >> $LOGFILE
echo "</BODY>" >> $LOGFILE


echo "</BODY>" >> $LOGFILE
echo "<ADDRESS>" >> $LOGFILE
echo "<HR>LUSS@lancaster.ac.uk" >> $LOGFILE
echo "</ADDRESS>" >> $LOGFILE

echo "<HR>" >> $LOGFILE
echo "See Also..." >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/index.html">Toplevel</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Notices/index.html">Notices</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Trivia/index.html">Trivia</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Articles/index.html">Articles</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Pictures/index.html">Pictures</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/Maps/index.html">Maps</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html">Cave Guide</A>" >> $LOGFILE
echo "<A HREF="http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html">WWW</A>" >> $LOGFILE

echo Completed main log $NEWLINE


# run the graph update
stats.sh
echo Completed stats $NEWLINE

# set process going again 
# this log is not atlog, so don't invoke a new process
# at -ms now +1 day < log2.sh 
