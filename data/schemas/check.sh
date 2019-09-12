#!/bin/bash

for schema in *.xsd
do
	name=${schema#*.}
	name=${name%.*}
	echo ${name}
	ls ~/mottip/pycharmProjects/GDC/data/xml/clinical/*/*/* | grep ${name}
done
