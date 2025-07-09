#!/bin/bash
#
### Refrences ###
## https://wiki.archlinux.org/title/ZFS
## https://wiki.gentoo.org/wiki/ZFS
## https://support.tools/how-to-create-encrypted-zfs-pool/#creating-an-encrypted-zfs-pool
#
### Description ###
## Set up Raspberry Pi 5 with a USB ZFS Mirror
## starting from base Raspberry Pi OS Install

### Start Script ###

### Variables ###
#arc_max=
bits=128000000000
dataset=pantry
dir_arc=/sys/module/zfs/parameters/zfs_arc_max
dir_key=/root/keys
dir_pool=/mnt/zfs
dir_srv=/srv/nfs
#key=
#pool=data

### User Input ###
read -p 'Enter ZFS Main Pool Name: ' pool &&

### Main Script ###

### Update System ###
sudo apt-get update &&
sudo apt-get upgrade -y &&

### Install ZFS ###
sudo apt-get install -y raspberrypi-kernel-headers zfs-dkms zfsutils-linux &&

### Update System Again ###
sudo apt full-upgrade -y &&
sudo apt dist upgrade -y &&

### Create Mountpoint for ZFS Mirror ###
mkdir -p /mnt/zfs/"$pool" &&

### Create ZFS Pool KeyFile ###
sudo dd if=/dev/random of="$dir_key"/"$pool".key bs=64 count=1 &&
ls "$dir_key"/"$pool".key

### Create ZFS Mirror ###
lsblk
read -p 'Enter First Device to be used for ZFS Mirror: ' dev_1 &&
read -p 'Enter Second Device to be used for ZFS Mirror: ' dev_2 &&
#sudo zpool create -R "$dir_pool" "$pool" mirror "$dev_1" "$dev_2" &&
sudo zpool create \
	-R "$dir_pool" \
	-o compression=on \
	-o dedup=on \
	-o encryption=on \
	-o keyformat=raw \
	-o keylocation=file://"$dir_key"/"$pool".key \
	"$pool" mirror \
	"$dev_1" "$dev_2" &&

### Tune and Optimize Pool ###
#sudo zpool set autoexpand=on "$pool" &&
#sudo zpool set autoreplace=on "$pool" &&

#sudo zfs set compression=zstd "$pool" &&
#sudo zfs set atime=off "$pool" &&
#sudo zfs set xattr=sa "$pool" &&
#sudo zfs set dnodesize=auto "$pool" &&
#sudo zfs set recordsize=1M "$pool" &&
#sudo zfs set primarycache=all "$pool" &&
#sudo zfs set secondarycache=all "$pool" &&
#sudo zfs set sync=standard "$pool" &&

## Enable Deduplication ##
sudo zfs set dedup=on "$pool" &&

### Create Directory for Dataset Keyfiles ###
sudo mkdir -p "$dir_key" &&

### Create Keys ###
sudo dd if=/dev/random of="$dir_key" bs=64 count=1 iflag=fullblock &&

### Set Up ZFS Datasets ###
lsblk
sudo zfs create \
	-o compression=on \
	-o encryption=on \
	-o keyformat=raw \
	-o keyloaction=file:///"$dir_key"/"$key" \
	"$pool"/"$dataset" &&

### Load Datasets ###
sudo zfs load-key "$pool"/"$dataset" &&

### Mount Datasets ###
sudo zfs mount "$pool"/"$dataset" &&

### Bind Datasets to NFS Server ###
sudo mount --bind "$dir_pool"/"$pool"                  "$dir_srv"/"$pool" &&

### Add Pool and Datasets to Crypttab ###
sudo tee /etc/crypttab <<EOF
## USB Data Server ##
EOF

### Add Pool and Datasets to FSTab ###
sudo tee /etc/fstab <<EOF
## USB Data Server ##
/mnt/zfs/media                  /srv/nfs/media                  none    bind,defaults,nofail,x-systemd.requires=zfs-mount.service       0       0
EOF

### Read Total Memory ###
cat /proc/meminfo | grep MemTotal

### Tune ZFS ARC Memory Usage ###
su root &&
cat "$dir_arc"
echo "$bits" >> "$dir_arc" &&
cat "$dir_arc"
exit &&

### End Main Script ###

### Salutation ###
echo "Successfully Completed Setup of ZFS Pool and all Datasets."
