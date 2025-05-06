#!/bin/bash

# configure a non-gpu Amazon Linux 2 instance for Nice DCV
# https://repost.aws/articles/ARuqicSphdQ8-GiwZC2-QOXg/how-do-i-install-gui-graphical-desktop-on-amazon-ec2-instances-running-amazon-linux-2-al2

sudo yum install -y gdm gnome-session gnome-classic-session gnome-session-xsession
sudo yum install -y xorg-x11-server-Xorg xorg-x11-fonts-Type1 xorg-x11-drivers
sudo yum install -y gnome-terminal gnu-free-fonts-common gnu-free-mono-fonts gnu-free-sans-fonts gnu-free-serif-fonts
sudo systemctl set-default graphical.target

cd /tmp
sudo rpm --import https://d1uj6qtbmh3dt5.cloudfront.net/NICE-GPG-KEY
curl -L -O https://d1uj6qtbmh3dt5.cloudfront.net/nice-dcv-amzn2-$(arch).tgz
tar -xvzf nice-dcv-amzn2-$(arch).tgz && cd nice-dcv-*-amzn2-$(arch)
sudo yum install -y ./nice-dcv-server-*.rpm
sudo yum install -y ./nice-dcv-web-viewer-*.rpm
sudo yum install -y ./nice-xdcv-*.rpm
sudo systemctl enable dcvserver

sudo sed -i "/^\[session-management\/automatic-console-session/a owner=\"ec2-user\"\nstorage-root=\"%home%\"" /etc/dcv/dcv.conf
sudo sed -i "s/^#create-session/create-session/g" /etc/dcv/dcv.conf

sudo yum install -y xorg-x11-drv-dummy
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