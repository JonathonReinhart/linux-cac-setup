#!/bin/bash

yum_pkgs="pcsc-lite p11-kit coolkey openconnect"
libcoolkey="/usr/lib64/pkcs11/libcoolkeypk11.so"
coolkey_p11mod="/etc/pkcs11/modules/libcoolkey.module"

# setup colors
if [ -t 1 ]; then
    COLOR_RED="\033[31m"
    COLOR_OFF="\033[0m"
fi


error() {
    local message="$1"
    local exitcode="${2:-2}" # default 2
    echo -e "${COLOR_RED}Error: ${message}${COLOR_OFF}"
    exit $exitcode
}

set -e

if [ $(id -u) != "0" ]; then
    error "Must be run as root" 1
fi

echo -e "\nInstalling packages..."
yum install -y $yum_pkgs
echo "done."

echo -e "\nEnabling pcscd..."
systemctl enable pcscd
systemctl start pcscd
echo "done."

echo -e "\nEnabling libcoolkey pcks11 module..."
test -f $libcoolkey || error "$libcoolkey missing"
test -f $coolkey_p11mod && error \
    "$coolkey_p11mod already exists. Please remove and try again."
echo "module:$libcoolkey" > $coolkey_p11mod
echo "done."
