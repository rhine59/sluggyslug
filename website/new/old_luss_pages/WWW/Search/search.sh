#!/bin/sh

awk -F; '
BEGIN {
	header = 0
}
FILENAME="header.search" {
	header++
	index[header]=$1
	mounted[header]=$2
	language[header]=$3
	created[header]=$4
	modified[header]=$5
	topics[header]=$6
	initials[header]=$7
	name[header]=$8
	url[header]=$9
}

{
	if ( $1 :q

' header.search
