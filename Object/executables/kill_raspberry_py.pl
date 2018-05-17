#!/usr/bin/perl
#$val= $ARGV[0];
$val = "object.py";
if ($val eq '')
{
   print "\ngive an argument\n\n";
   exit
} 

@aaa=`ps aux | egrep $val| awk '{print \$2}'`;

print @aaa;
foreach (@aaa)
{
  `kill -9 $_`;
}

