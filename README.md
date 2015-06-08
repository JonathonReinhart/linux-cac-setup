# linux-cac-setup
Scripts for enabling DoD CAC usage on modern Linux distros

### `setup_fedora.sh`
This script performs all necessary setup for using a CAC on Fedora Linux. It was written on Fedora 21, but should work on any distro using `yum` and `systemd`.

When you run this script (as root), it will:
- Install the following packages:
  - `pcsc-lite`
  - `p11-kit`
  - `coolkey`
  - `openconnect`
- Enable the `pcscd` service
- Enable `p11-kit` (and openconnect) to use `libcoolkey.so`


### `openconnect-cac`
This is a wrapper for `openconnect` which helps select the correct certificate on your CAC for authentication. It requires Python 2.7+

To use it, simply put it somewhere in your `$PATH`, and execute: `openconnect-cac vpn.example.com` (with your VPN URL). It will invoke `p11tool` to find your CAC and allow you to select the appropriate certificate. (In my experience, the "CAC Email Signature Certificate" was the correct one).
