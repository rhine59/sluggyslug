#!/bin/perl

@vars=();

$remote_user=$ENV{'REMOTE_USER'};
$remote_addr=$ENV{'REMOTE_ADDR'};
$remote_host=$ENV{'REMOTE_HOST'};
$content_len=$ENV{'CONTENT_LENGTH'};

read(stdin, $input, $content_len);

$input =~ tr/+/ /;
$pos = index($input, "&");
while ($pos != -1)
{
  $item = substr($input, 0, $pos);
  $input = substr($input, $pos+1);
  print tmpfile $item."\n";
  do process($item);
  $pos = index($input, "&");
}
do process($input);

print "Content-type: text/html\n";
print "\n";
print "\n";

print "<HTML>";
print "<HEAD>";
print "<TITLE>Cave Added, Cave Database, Lancaster University Speleological Society</TITLE>";
print "</HEAD>";

print "<BODY>";
print "<IMG ALIGN=right SRC=\"http://www.comp.lancs.ac.uk/clubs/luss/Pictures/logo-small.gif\">";
print "<H1>Cave Added</H1>";
print "<H2>Cave Database</H2>";
print "<H3>Lancaster University Speleological Society</H3>";
print "<HR>";

print "The following information has been added to the cave database...(not yet)<BR>";

#print "<B>remote_user:</B> $remote_user";
#print "<B><BR>remote_addr:</B> $remote_addr";
#print "<B><BR>remote_host:</B> $remote_host";

while (($fieldname, $fieldvalue) = each (%vars) )
{
	print "<BR><B>$fieldname:</B>$fieldvalue\n"; 
}

$filename = `/export/home/www/htdocs/rec-and-travel/luss/scripts/tmpfilename /export/home/www/htdocs/rec-and-travel/luss/test/CaveGuide`;
print "<BR>In the file... $filename";

open(DATAFILE, ">$filename");

print DATAFILE "remote_user $remote_user\n";
print DATAFILE "remote_addr $remote_addr\n";
print DATAFILE "remote_host $remote_host\n";

while (($fieldname, $fieldvalue) = each (%vars) )
{
	# Remove the carriage returns from any field values
	$fieldvalue =~s/\n/ /g;

	# Then write them out to the file
	print DATAFILE "$fieldname $fieldvalue\n";
}
close(DATAFILE);







print "</BODY>";

print "<ADDRESS>";
print "<HR>LUSS\@lancaster.ac.uk";
print "</ADDRESS>";
print "<HR>";
print"See Also...";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/index.html\">Toplevel</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Notices/index.html\">Notices</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Trivia/index.html\">Trivia</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Articles/index.html\">Articles</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Pictures/index.html\">Pictures</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Maps/index.html\">Maps</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html\">Cave Guide</A> ";
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html\">WWW</A> ";

print "</BODY></HTML>";


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

