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

### Main Script ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Executing Main Script..."

### User Input ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
read -p 'Enter ZFS Main Pool Name: ' pool &&

### Update System ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Updating Operating System..."
sudo apt-get update &&
sudo apt-get upgrade -y &&
echo "Successfully Updated Operating System!"

### Install ZFS ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Installing ZFS File System..."
sudo apt-get install -y raspberrypi-kernel-headers zfs-dkms zfsutils-linux &&
echo "Successfully Installed ZFS File System!"

### Update System Again ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Updating System After Post ZFS Installation..."
sudo apt full-upgrade -y &&
sudo apt dist upgrade -y &&
echo "Successfully Updated Operating System incorporating ZFS!"

### Create Mountpoint for ZFS Mirror ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Creating Mountpoint for ZFS Mirror..."
mkdir -p /mnt/zfs/"$pool" &&
ls /mnt/zfs
echo "Successfully Created ZFS Mountpoint!"

### Create Directory for ZFS Keyfiles ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Creating Directory for ZFS Keyfiles..."
sudo mkdir -p "$dir_key" &&
ls "$dir_key"
echo "Successfully Created Directory for ZFS Keyfiles!"

### Create ZFS Pool KeyFile ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Creating "$pool" KeyFile..."
sudo dd if=/dev/random of="$dir_key"/"$pool".key bs=64 count=1 &&
ls "$dir_key"/"$pool".key
echo "Successfully Created "$pool" Keyfile!"

### Create ZFS Mirror ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Creating ZFS Mirror "$pool"..."
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
echo "Successfully Created ZFS Mirror "$pool"!"

### Tune and Optimize Pool ###
#printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
#echo "Optimizing "$pool"..."
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
#echo "Successfully Optimized "$pool"!"

## Enable Deduplication ##
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Enabling Deduplication..."
sudo zfs set dedup=on "$pool" &&
echo "Successfully Enabled Deduplication!"

## Bind Pool to NFS Server ##
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Binding "$pool" to NFS Server..."
sudo mount --bind "$dir_pool"/"$pool" "$dir_srv"/"$pool" &&
echo "Successfully Mounted "$pool" for NFS Access!"

### Data Set Configuration ###

## Create Keys ##
#printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
#sudo dd if=/dev/random of="$dir_key" bs=64 count=1 iflag=fullblock &&

## Set Up ZFS Datasets ##
#lsblk
#sudo zfs create \
#	-o compression=on \
#	-o encryption=on \
#	-o keyformat=raw \
#	-o keyloaction=file:///"$dir_key"/"$key" \
#	"$pool"/"$dataset" &&

## Load Datasets ##
#sudo zfs load-key "$pool"/"$dataset" &&

## Mount Datasets ##
#sudo zfs mount "$pool"/"$dataset" &&

## Bind Datasets to NFS Server ##
#sudo mount --bind "$dir_pool"/"$pool"                  "$dir_srv"/"$pool" &&

### End Dataset Configuration ###

### Edit Configuration Files ###

## Add Pool and Datasets to Crypttab ##
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Adding "$pool" to CryptTab..."
sudo tee /etc/crypttab <<EOF
## USB Data Server ##
EOF
echo "Successfully Added "$pool" to CryptTab!"

## Add Pool and Datasets to FSTab ##
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Adding "$pool" to FSTab..."
sudo tee /etc/fstab <<EOF
## USB Data Server ##
/mnt/zfs/media                  /srv/nfs/media                  none    bind,defaults,nofail,x-systemd.requires=zfs-mount.service       0       0
EOF
echo "Successfully Added "$pool" to FSTab!"

## Read Total Memory ##
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
cat /proc/meminfo | grep MemTotal
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&

## Tune ZFS ARC Memory Usage ##
su root &&
cat "$dir_arc"
echo "$bits" >> "$dir_arc" &&
cat "$dir_arc"
exit &&

### End Configuration ###

### End Main Script ###

### Salutation ###
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
echo "Successfully Completed Setup of ZFS Pool "$pool" and all Datasets!"
printf '%*s\n' "${COLUMS:-$(tput cols)}" '' | tr ' ' '#' &&
