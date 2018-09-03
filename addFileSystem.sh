#!/bin/bashqq
#**********************
#Step 03: ec2run07_Part2b.sh
#*********************
#Run the commands in this file in an ssh
#console after running the Python commands in
#ec2run07_Part2a.py


#make sure sdf is there
cat /proc/partitions
lsblk

#check for data on the device
#sdf is actually a symlink to xvdf
sudo file -s /dev/sdf

#/dev/xvdf: data - if you see output that says "data" it means there is
#no data on the device
sudo file -s /dev/xvdf

ls /dev/sdf

#create a filesystem on sdf, again sdf is a symlink for  xvdf
sudo mke2fs -t ext4 -F -j /dev/sdf

#now that the device has a filesystem on it, mount it
sudo mkdir -p /mnt/data-store
sudo mount /dev/sdf /mnt/data-store
df -T
cd /mnt/data-store
sudo chmod 777 .

#type something in, whatever you type in gets into file cats.txt
#hit return followed by control-d to get out of the ca
sudo echo "cat is cute." > cats.txt
cat cats.txt

#now see if there is data in the volume
#you will see several things including ext4
sudo file -s /dev/xvdf

#*************************
#Next Step 04 is in ec2run07_Part3.py
