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
This is a wrapper for `openconnect` which helps select the correct certificate on your CAC for authentication.
