#!/bin/bash
# Run with sudo
set -e
set -x
disk=$1
name=${2:-data}
# maybe use this https://unix.stackexchange.com/questions/632161/how-to-run-parted-mklabel-in-a-script-without-user-prompt
parted "$disk" --script -- mklabel msdos
parted "$disk" --script -- mkpart primary fat32 1MiB 100%
#parted "$disk" --script -- name 1  "$name"
mkfs.vfat -F32 "${disk}1"
