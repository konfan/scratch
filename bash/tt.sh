#!/bin/bash


g=${1-"/"}
e=${2-"/etc"}
c=${0%$(basename ${0})}

d=asdfrererfff

echo $g
echo $e
echo $c
echo ${d%"fff"}
