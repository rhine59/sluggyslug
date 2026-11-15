$1=="cavename" {;$1="";$2=""; pname = substr($0,3); filename[lines++] = FILENAME;
                                                 pubname[FILENAME] = pname;
             }


END {
print"<HTML>"
print"<HEAD>" 

print"<TITLE>Lancaster University Speleological Society - Cave List</TITLE>"

print"</HEAD>"
print"<BODY>"
print"<H1>Lancaster University Speleological Society - Cave List</H1>"
print"<h2>Caves In The North Of England</h2>"
print"<BR>"
print"<UL>"
for (i=0;i<lines;i++) {
    print"<LI><A HREF=\"http://www.comp.lancs.ac.uk/cgi-bin/clubs/luss/viewpage.sh?"filename[i]"\">"pubname[filename[i]]"</A>";
    }

print"</UL>"
print"</BODY>"

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
print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html\">Cave Guide</A>"
print"<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html\">WWW</A>"
print"</HTML>"
}
