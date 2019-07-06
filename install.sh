#!/bin/bash

apt update
apt upgrade

# Will be needed later
apt install -y unzip unionfs-fuse

# Create the directory structure
[[ -d defrag-base ]] || mkdir defrag-base
[[ -d defrag-maps ]] || mkdir defrag-maps
[[ -d proxymod-base ]] || mkdir -p proxymod-base/defrag/
[[ -d quake3-base ]] || mkdir -p quake3-base/baseq3
[[ -d servers ]] || mkdir -p servers/mount

# Determine the latest version of DeFRaG mod available
#TODO remove --no-check-certificate when cgg adds autorenew for certbot
DEFRAG_MOD_URL=$(cd /tmp/ && wget --spider -r --no-parent --no-check-certificate https://q3defrag.org/files/defrag/ 2>&1 | grep -E "\-\-2" | grep "defrag_" | grep -v "beta" | cut -d' ' -f4 | sort | tail -n1)

# Download the latest version of DeFRaG mod
#TODO remove --insecure when NM adds autorenew for certbot
curl --insecure $DEFRAG_MOD_URL > defrag-base/defrag.zip

# Unzip DeFRaG mod
cd defrag-base
unzip -o defrag.zip
# Cleanup
rm defrag.zip
cd -

# Clone Quake3e by Cyrax, q3e is the fastest engine for q3 dedi server
[[ -d Quake3e ]] || git clone https://github.com/ec-/Quake3e.git

# Install required packages for building Quake3e
apt install -y make gcc build-essential libcurl4-openssl-dev

# Build Quake3e dedicated server only, omit client.
cd Quake3e
make BUILD_CLIENT=0

# Cleanup 
cd -

# Copy over the Quake3e binary
cp Quake3e/build/release-linux-x86/quake3e.ded quake3-base/quake3e.ded

# Remove unused packages at the end
apt autoremove -y
