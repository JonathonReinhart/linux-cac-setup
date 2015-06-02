#!/bin/bash

YUM_PKGS="pcsc-lite p11-kit coolkey openconnect"

set -e

if [ $(id -u) != "0" ]; then
    echo "Must be run as root" >&2
    exit 1
fi

echo -e "\nInstalling packages..."
yum install -y $YUM_PKGS
echo "done."

echo -e "\nEnabling pcscd..."
systemctl enable pcscd
systemctl start pcscd
echo "done."
