#**************************
#Step 06: ec2run07_Part4b.sh
#
#Run this after Step 05 in the first part of file
#ec2run07_Part4a.py

#ssh  -i /Users/JeffM/Jeff/AWS_Programming/New-ProgAWS_Notes/Keys/KeyPair07.pem #ec2-user@54.193.104.254

#we have not mounted the volume yet in linux
lsblk


#see if there is any data on xvdf
sudo file -s /dev/xvdf

#mount the volume in linux
sudo mkdir /mnt/dz


#mount the volume we created from a snapshot
sudo mount /dev/sdf /mnt/dz -t ext4


cd /mnt/dz
ls

#see if our data is still here
cat cats.txt

#if you see any errors accessing the volume try
#dmesg - uncomment it
#dmesg | tail
logout

#************************
#Next Step 07:  ec2run07_Part5.py
#****************************************
