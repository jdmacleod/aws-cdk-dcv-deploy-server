#!/bin/bash

# configure a non-gpu RHEL 8/9 or Rocky 8/9 instance for Nice DCV
# https://repost.aws/articles/AR4Nbl3SxTSIW3WpFSUJhzXg/how-do-i-install-gui-graphical-desktop-on-amazon-ec2-instances-running-rhel-rocky-linux-8-9

if (! systemctl list-units | grep -q amazon-ssm-agent); then
  if (arch | grep -q x86); then
    sudo dnf install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_amd64/amazon-ssm-agent.rpm
  else
    sudo dnf install -y https://s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/linux_arm64/amazon-ssm-agent.rpm
  fi
fi

sudo dnf update -y
sudo dnf groupinstall -y 'Server with GUI'
sudo dnf groupinstall -y GNOME
sudo sed -i '/^\[daemon\]/a WaylandEnable=false' /etc/gdm/custom.conf
sudo systemctl set-default graphical.target

cd /tmp
sudo rpm --import https://d1uj6qtbmh3dt5.cloudfront.net/NICE-GPG-KEY
OS_VERSION=$(. /etc/os-release;echo $VERSION_ID | sed -e 's/\..*//g')
curl -L -O https://d1uj6qtbmh3dt5.cloudfront.net/nice-dcv-el$OS_VERSION-$(arch).tgz
tar -xvzf nice-dcv-el$OS_VERSION-$(arch).tgz && cd nice-dcv-*-el$OS_VERSION-$(arch)
sudo dnf install -y ./nice-dcv-server-*.rpm
sudo dnf install -y ./nice-dcv-web-viewer-*.rpm
sudo dnf install -y ./nice-xdcv-*.rpm
sudo systemctl enable dcvserver

if (cat /etc/os-release | grep -q Rocky); then
  USER="rocky"
else
  USER="ec2-user"
fi
sudo sed -i "/^\[session-management\/automatic-console-session/a owner=\"$USER\"\nstorage-root=\"%home%\"" /etc/dcv/dcv.conf
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

if (which firewall-offline-cmd); then
  sudo systemctl stop firewalld
  sudo firewall-offline-cmd --add-port 8443/tcp
  sudo firewall-offline-cmd --add-port 8443/udp
  sudo systemctl start firewalld
fi

sudo systemctl isolate multi-user.target && sudo systemctl isolate graphical.target
sudo systemctl stop dcvserver && sudo systemctl start dcvserver
