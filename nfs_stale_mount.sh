#!/bin/bash

while read _ _ mount _; do 
 read -t1 < <(stat -t "$mount") || echo "$mount"; 
done < <(mount | grep 'nfs') >> nfs_array.txt
sleep 5

for i in $(cat nfs_array.txt); do umount -lf $i ; sleep 10; done
