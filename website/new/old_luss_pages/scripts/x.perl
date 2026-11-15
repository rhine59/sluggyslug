#!/bin/perl

$len=$ENV{'CONTENT_LENGTH'};
$request_method=$ENV{'REQUEST_METHOD'};
$content_type=$ENV{'CONTENT_TYPE'};
$remote_user=$ENV{'REMOTE_USER'};
$remote_addr=$ENV{'REMOTE_ADDR'};
$remote_host=$ENV{'REMOTE_HOST'};
$content_len=$ENV{'CONTENT_LENGTH'};
$server_software=$ENV{'SERVER_SOFTWARE'};
$server_name=$ENV{'SERVER_NAME'};
$server_protocol=$ENV{'SERVER_PROTOCOL'};
$server_port=$ENV{'SERVER_PORT'};
$gateway_interface=$ENV{'GATEWAY_INTERFACE'};
$http_accept=$ENV{'HTTP_ACCEPT'};
$path_info=$ENV{'PATH_INFO'};
$path_translated=$ENV{'PATH_TRANSLATED'};
$script_name=$ENV{'SCRIPT_NAME'};
$query_string=$ENV{'QUERY_STRING'};

@vars=();

print "Content-type: text/html\n";
print "\n";
print "\n";

print "<HTML><HEAD><TITLE>x.perl</TITLE><HEAD><BODY><H1>x.perl</H1>";
print "<HR>";
print "<B>Default Information</B>";
print "<BR>request_method = $request_method";
print "<BR>content_type = $content_type";
print "<BR>remote_user = $remote_user";
print "<BR>remote_addr = $remote_addr";
print "<BR>remote_host = $remote_host";
print "<BR>content_len = $content_len";
print "<BR>server_software = $server_software";
print "<BR>server_name = $server_name";
print "<BR>server_protocol = $server_protocol";
print "<BR>server_port = $server_port";
print "<BR>gateway_interface = $gateway_interface";
print "<BR>http_accept = $http_accept";
print "<BR>path_info = $path_info";
print "<BR>path_translated = $path_translated";
print "<BR>script_name = $script_name";
print "<BR>query_string = $query_string";
print "<HR>";

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

while (($fieldname, $fieldvalue) = each (%vars) )
{
        print "<B>$fieldname:</B><BR>$fieldvalue<BR>\n"; 
}
print "<HR>";





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

