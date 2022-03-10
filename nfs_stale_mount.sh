#!/bin/bash
while :
do
  while read _ _ mount _; do 
    read -t1 < <(stat -t "$mount") || echo "$mount"; 
  done < <(mount | grep 'nfs') >> nfs_array.txt
  
  for i in $(cat nfs_array.txt); do umount -lf $i; done
  sleep 5
done
