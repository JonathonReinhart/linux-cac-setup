#!/bin/bash

YUM_PKGS="pcsc-lite p11-kit coolkey openconnect"

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
yum install -y $YUM_PKGS
echo "done."

echo -e "\nEnabling pcscd..."
systemctl enable pcscd
systemctl start pcscd
echo "done."
