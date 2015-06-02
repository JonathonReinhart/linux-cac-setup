#!/bin/bash

source common.sh

echo "All hardware tokens (Smart Cards) available to PKCS #11:"
(p11tool --list-tokens | grep -B3 -A4 'Hardware token') || \
    error "None found! Is your reader connected and smart card inserted?"
