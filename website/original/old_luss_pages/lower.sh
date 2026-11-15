#!/bin/sh
for i in `ls T*`
do
echo $i
num=` echo $i | awk -FP '{print $2}' | awk -F. '{print "t95p" $1 ".jpg"}'`
mv $i $num
echo $num
done
exit

