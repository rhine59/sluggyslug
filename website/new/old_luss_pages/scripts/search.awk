function printarray (arrayname,arraylength)
{
	if (arraylength==0) 
		print arrayname[0]
	else 
		for (i=0;i<arraylength;i++) print arrayname[i]
}


$2=="=" {cat=$1;$1="";$2=""; find[cat"."optnum[cat]++] = substr($0,3)}

END {
 while (("/bin/ls ../CaveGuide/*.dba" | getline) ==1)
 {
   file = $0;
   foundhere=0
   while (getline < file)
   {
      var=$1;
      $1="";$2="";val=substr($0,3);
      for (fopt in find)
      {
	  f=substr(fopt,1,index(fopt,".")-1);
          if (var == f && val == find[fopt])
          {
	      foundhere++;
	  }
          else {if (var == "cavename") cavename = val}
      }
   }
   filescore[foundhere]=filescore[foundhere]"<LI><A HREF=\"http://www.comp.lancs.ac.uk/cgi-bin/clubs/luss/viewpage.sh?"file"\">"cavename"</A> "
   close (file);
 }

     

print "<HTML>"
print "<HEAD>"

print "<TITLE>Lancaster University Speleological Society - Cave Guide Search Results</TITLE>"
print "<H1>Lancaster University Speleological Society - Cave Guide Search Results</H1>"


print "</HEAD>"
print "<BODY>"

print "<h2>Search Results</h2>"

print "These are the caves which match all (or some) of your requirements. "
print "The number to the left indicates the percentage of your wants which "
print "they matched. Click on a cave name to see the full entry for that cave."
print "<P>"

print"<UL>"

for (f in find) maxnum++;

for (f=maxnum;f;f--) {
       if (filescore[f]) {
           matchsuccess = int(f*100/maxnum);
           print "<LI>" matchsuccess "<UL>" filescore[f] "</UL>";
        }
}
print"</UL>"
print "</BODY>"



print "<ADDRESS>"
print "<HR>LUSS@lancaster.ac.uk"
print "</ADDRESS>"

print "<HR>"
print "See Also..."
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/index.html\">Toplevel</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Notices/index.html\">Notices</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Trivia/index.html\">Trivia</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Articles/index.html\">Articles</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Pictures/index.html\">Pictures</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Maps/index.html\">Maps</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/CaveGuide/index.html\">Cave Guide</A>"
print "<A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/WWW/index.html\">WWW</A>"
print "</HTML>" 

}

