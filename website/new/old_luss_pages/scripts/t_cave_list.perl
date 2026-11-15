#!/bin/perl

print "Content-type: text/html\n";
print "\n";
print "\n";

print "<HTML>";
print "<HEAD>";
print "<TITLE>List All Caves, Cave Database, Lancaster University Speleological Society</TITLE>";
print "</HEAD>";

print "<BODY>";
print "<IMG ALIGN=right SRC=\"http://www.comp.lancs.ac.uk/clubs/luss/Pictures/logo-small.gif\">";
print "<H1>List All Caves</H1>";
print "<H2>Cave Database</H2>";
print "<H3>Lancaster University Speleological Society</H3>";
print "<HR>";

# READ THE DIRECTORY LIST INTO THE ARRAY

opendir (DATADIR, "/export/home/www/htdocs/rec-and-travel/luss/test/Data");

$filename = readdir(DATADIR);
while($filename ne "" )
{
	if ( ( $filename ne ".") && ( $filename ne ".." ) )
	{
		push (@direct_array, $filename);
	}
	$filename = readdir(DATADIR);
}
closedir(DATADIR);

# FOR EACH ELEMENT IN AN ARRAY PRINT A HTML LINK TO THE DISPLAY SCRIPT?FILENAME

for ($i=0; $i<scalar(@direct_array); $i++)
{

	$filename = "/export/home/www/htdocs/rec-and-travel/luss/test/Data/".$direct_array[$i];

	open(DATAFILE, $filename);

#	print "<TR><TH> </TH><TD> </TD></TR>";

	print "<TABLE BORDER>";
	print "<TR><TH ALIGN=right>Filename </TH><TD>$filename</TD></TR>";

	$line = <DATAFILE>;
	while ( $line ne "" )
	{
		# split that line into two parts

		# up to the first space
		$split_pos = index($line, " ");
		$field_name = substr ($line, 0, $split_pos);
#		print "$field_name: </B>";

		$field_value = substr ($line, $split_pos +1, -1);
#		print "$field_value";

		print "<TR><TH ALIGN=right>$field_name</TH><TD>$field_value</TD></TR>";

		$line = <DATAFILE>;
		$field_name = "";
		$field_value = "";

	}

	print "</TABLE>";

}




print "</BODY>";

print `cat /export/home/www/htdocs/rec-and-travel/luss/tail.html`;


# ------------------------------------------------------------
 
sub process
{
  local($i, $r, $ch, $pos);
  local($s)=$_[0];
  for ($i=0; $i<length($s); $i++)
  {
    $ch=substr($s,$i,1);
    if ($ch eq "%") { $r .= pack("c",hex(substr($s,$i+1,2))); $i+=2; }
    else { $r .= $ch; }
  }
  $pos=index($r,"=");
  if ($pos == -1) { return; }
  $vars{substr($r,0,$pos)}=substr($r,$pos+1);
}
 
# ------------------------------------------------------------

	
