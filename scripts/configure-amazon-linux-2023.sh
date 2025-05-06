#!/bin/bash

# configure a non-gpu Amazon Linux 2023 instance for Nice DCV
# https://repost.aws/articles/ARq0LbVvRwTRukVpS6Zt1uZw/how-do-i-install-gui-graphical-desktop-on-amazon-ec2-instances-running-amazon-linux-2023-al2023

# NOTE: Amazon Linux 2023 is more tailored to server-side use, so putting a GUI on it takes effort.
# this example is to illustrate how to do it, but other distros like Rocky may be better suited for GUI use.

sudo dnf groupinstall "Desktop" -y
sudo sed -i '/^\[daemon\]/a WaylandEnable=false' /etc/gdm/custom.conf
sudo systemctl set-default graphical.target

cd /tmp
sudo rpm --import https://d1uj6qtbmh3dt5.cloudfront.net/NICE-GPG-KEY
curl -L -O https://d1uj6qtbmh3dt5.cloudfront.net/nice-dcv-amzn2023-$(arch).tgz
tar -xvzf nice-dcv-amzn2023-$(arch).tgz && cd nice-dcv-*-amzn2023-$(arch)
sudo dnf install -y ./nice-dcv-server-*.rpm
sudo dnf install -y ./nice-dcv-web-viewer-*.rpm
sudo dnf install -y ./nice-xdcv-*.rpm
sudo systemctl enable dcvserver

sudo sed -i "/^\[session-management\/automatic-console-session/a owner=\"ec2-user\"\nstorage-root=\"%home%\"" /etc/dcv/dcv.conf
sudo sed -i "s/^#create-session/create-session/g" /etc/dcv/dcv.conf

sudo dnf install -y xorg-x11-drv-dummy
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

sudo reboot