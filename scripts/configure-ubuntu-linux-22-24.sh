#!/bin/bash

# configure a non-gpu Ubuntu 22 or 24 instance for Nice DCV
# https://repost.aws/articles/ARJtZxRiOURwWI2qSWjl4AaQ/how-do-i-install-gui-graphical-desktop-on-amazon-ec2-instances-running-ubuntu-linux

export DEBIAN_FRONTEND=noninteractive
sudo apt update
sudo apt install -y ubuntu-desktop-minimal
sudo sed -i '/^\[daemon\]/a WaylandEnable=false' /etc/gdm3/custom.conf
sudo systemctl set-default graphical.target

cd /tmp
OS_VERSION=$(. /etc/os-release;echo $VERSION_ID | sed -e 's/\.//g')
curl -L -O https://d1uj6qtbmh3dt5.cloudfront.net/nice-dcv-ubuntu$OS_VERSION-$(arch).tgz
tar -xvzf nice-dcv-ubuntu$OS_VERSION-$(arch).tgz && cd nice-dcv-*-$(arch)
sudo apt install -y ./nice-dcv-server_*.deb
sudo apt install -y ./nice-dcv-web-viewer_*.deb
sudo apt install -y ./nice-xdcv_*.deb
sudo usermod -aG video dcv
sudo systemctl enable dcvserver

sudo sed -i "/^\[session-management\/automatic-console-session/a owner=\"ubuntu\"\nstorage-root=\"%home%\"" /etc/dcv/dcv.conf
sudo sed -i "s/^#create-session/create-session/g" /etc/dcv/dcv.conf

sudo apt install -y xserver-xorg-video-dummy
sudo tee /etc/X11/xorg.conf > /dev/null << EOF
Section "Device"
    Identifier "DummyDevice"
    Driver "dummy"
    Option "UseEDID" "false"
    VideoRam 512000
EndSection

Section "Monitor"
    Identifier "DummyMonitor"
    HorizSync   5.0 - 1000.0
    VertRefresh 5.0 - 200.0
    Option "ReducedBlanking"
EndSection

Section "Screen"
    Identifier "DummyScreen"
    Device "DummyDevice"
    Monitor "DummyMonitor"
    DefaultDepth 24
    SubSection "Display"
        Viewport 0 0
        Depth 24
        Virtual 4096 2160
    EndSubSection
EndSection
EOF

sudo systemctl isolate multi-user.target && sudo systemctl isolate graphical.target
sudo systemctl stop dcvserver && sudo systemctl start dcvserver