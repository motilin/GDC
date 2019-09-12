#!/bin/bash

while read prefix path
do
	wget ${path}
done < $1
