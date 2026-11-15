BEGIN{cavename="Unknown Cave";location="Unknown";
	grade="Unknown";gridreference="Unknown";
	cavelength=0; cavedepth=0; cavealtitude=0}

$1=="cavename" {;$1="";$2=""; cavename = substr($0,3); }
$1=="permit" {;$1="";$2=""; permit = substr($0,3); }
$1=="permitfrom" {;$1="";$2=""; permitfrom = substr($0,3); }
$1=="location" && $3!="Any" {;$1="";$2=""; location = substr($0,3); }
$1=="grade" && $3!="Any" {;$1="";$2=""; grade = substr($0,3); }
$1=="gridreference" {;$1="";$2=""; gridreference = substr($0,3); }
$1=="cavelength" {;$1="";$2=""; cavelength = substr($0,3); }
$1=="cavedepth" {;$1="";$2=""; cavedepth = substr($0,3); }
$1=="cavealtitude" {;$1="";$2=""; cavealtitude = substr($0,3); }
$1=="description" {;$1="";$2=""; description[d++] = substr($0,3); }



END {


print"<HTML>"
print"<HEAD>"

print"<TITLE>LUSS Cave Guide - "cavename"</TITLE>"
print"<H1>Lancaster University Speleological Society Cave Guide - "cavename"</H1>"
print"</HEAD>"
print"<BODY>"

print"<H2>Information:</H2>"
print"<strong>Location: </strong>"location"<BR>"
print"<strong>Grid Reference: </strong>"gridreference"<BR>"
print"<strong>BCRA Grade: </strong>"grade"<BR>"
print"<strong>Altitude: </strong>"cavealtitude" metres<BR>"
print"<strong>Length: </strong>"cavelength" metres<BR>"
print"<strong>Depth: </strong>"cavedepth" metres<BR>"
print"<strong>Permit Required: </strong>" permit "<strong>   Available From: </strong>"permitfrom"<BR>"

print"<H2>Description:</H2>"
if (!d) print "No Description";
else for (i=0;i<d;i++) print description[i];




print"<P>"

	print"<ADDRESS>"
      	print"<HR>LUSS@lancaster.ac.uk"
        print"</ADDRESS>"
        print""
        print"<HR>"
        print"See Also..."
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/index.html\">Toplevel</A>"
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Notices/index.html\">Notices</A>"
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Trivia/index.html\">Trivia</A>"
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Articles/index.html\">Articles</A>"
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Pictures/index.html\">Pictures</A>"
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Maps/index.html\">Maps</A>"
	print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html\">Cave Guide</A>"
        print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html\">WWW</A>"
        print""
        print""



print"</HTML>"    

}
