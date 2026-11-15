BEGIN 	{ printf "Content-type: text/html\n\n<HTML><HEAD>\n<TITLE>List of Postscript files</TITLE>\n<H1>List of Postscript Files</H1>\n</HEAD><BODY>\n"}
	{ printf "<LI><A HREF=\"http://www.comp.lancs.ac.uk/clubs/luss/Exploration/Spain/Postscript/" $1 ".ps\">" $1 "</A>\n"}
END 	{ printf "</BODY>\n<ADDRESS><HR>LUSS@lancaster.ac.uk</ADDRESS>\n"}
