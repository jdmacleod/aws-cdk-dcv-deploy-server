#!/bin/bash

# configure a non-gpu SUSE 15 instance for Nice DCV
# https://repost.aws/articles/ARGF6bVA19QC6IVcaUy-69Ag/how-do-i-install-gui-graphical-desktop-on-amazon-ec2-instances-running-suse-linux-enterprise-server-15-sles-15

# install the AWS SSM agent, and start it
sudo zypper install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl stop amazon-ssm-agent && sudo systemctl start amazon-ssm-agent

sudo zypper install -y -t pattern gnome_basic
sudo update-alternatives --set default-displaymanager /usr/lib/X11/displaymanagers/gdm
sudo sed -i "s/DEFAULT_WM=\"\"/DEFAULT_WM=\"gnome\"/" /etc/sysconfig/windowmanager
sudo systemctl set-default graphical.target

cd /tmp
sudo rpm --import https://d1uj6qtbmh3dt5.cloudfront.net/NICE-GPG-KEY
curl -L -O https://d1uj6qtbmh3dt5.cloudfront.net/nice-dcv-sles15-x86_64.tgz
tar -xzf nice-dcv-sles15-x86_64.tgz && cd nice-dcv-*-sles15-x86_64
sudo zypper install -y ./nice-dcv-server-*.rpm
sudo zypper install -y ./nice-dcv-web-viewer-*.rpm
sudo zypper install -y ./nice-xdcv-*.rpm
sudo usermod -a -G video dcv
sudo systemctl enable dcvserver

sudo sed -i "/^\[session-management\/automatic-console-session/a owner=\"ec2-user\"\nstorage-root=\"%home%\"" /etc/dcv/dcv.conf
sudo sed -i "s/^#create-session/create-session/g" /etc/dcv/dcv.conf

sudo zypper install -y xf86-video-dummy
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

sudo firewall-offline-cmd --add-port 8443/tcp
sudo firewall-offline-cmd --add-port 8443/udp

sudo systemctl isolate multi-user.target && sudo systemctl isolate graphical.target
sudo systemctl stop dcvserver && sudo systemctl start dcvserver
