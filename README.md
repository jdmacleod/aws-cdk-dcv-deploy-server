
# AWS CDK - Deploy DCV Server

Deploys a DCV server instance

- Using a specific DCV instance AMI -
- Into an existing VPC
- Using a specific hardware profile

## Manual Deployment Using AWS Console and pre-built Nice DCV AMI from Marketplace

Using the AWS Console->EC2

Deploy Instance steps

Search AMI Catalog - Marketplace, use "DCV" as search term

Nice DCV for Amazon Linux 2

<https://aws.amazon.com/marketplace/seller-profile?id=74eff437-1315-4130-8b04-27da3fa01de1>

Select the AMI for Amazon Linux 2 and Nice DCV

Select "Subscribe on instance launch"

AMI id ami-017d0c53440a48b8b is revealed.

Instance type g4dn.xlarge is automatically selected.

Choose Key Pair "dcv-key-pair", which had already been created.

Initial instance creation failed, hit quota limit of 0 vCPU for account, can't access G instances?... Sent quota increase request to Amazon - Case ID 174361014200212.

Quota updated, trying second time.

Instance launched successfully. 3/3 checks passed.

Connect to Instance with SSH (root)

```bash
ssh -i "ec2-key-pair.pem" root@ec2-54-213-171-84.us-west-2.compute.amazonaws.com
...
Please login as the user "ec2-user" rather than the user "root".
```

```bash
ssh -i "ec2-key-pair.pem" ec2-user@ec2-54-213-171-84.us-west-2.compute.amazonaws.com
...
```

SSH connection successful.

Update OS for Instance.

```bash
sudo yum update
```

Check Nvidia Graphics

```bash
nvidia-smi
...
Reports Tesla T4 graphics, Driver 550.90.10, CUDA 12.4
```

Create a System-level user

```bash
sudo adduser jason --create-home --user-group
```

Set the password for user jason (to jason, for this test)

```bash
sudo passwd jason
...
```

Check DCV Sessions

```bash
sudo dcv list-sessions
There are no sessions available.
```

Create a virtual DCV session for user 'jason'

```bash
sudo dcv create-session console --type virtual --owner jason
```

Check DCV Sessions

```bash
sudo dcv list-sessions
Session: 'console' (owner:jason type:virtual)
```

Connect to instance from MacOS Sequoia with DCV client

Used public IP address of 54.213.171.84 in Nice DCV Client.

Connection successful.

Open Terminal.

Use glxgears to test Nvidia Graphics

```bash
glxgears
...
```

## Manual Deployment Using AWS Console with Manual Setup (instance running Ubuntu 2024, non-GPU)

<https://aws.amazon.com/blogs/aws/nice-desktop-cloud-visualization-dcv-is-now-amazon-dcv/>

AWS Console -> EC2

Launch Instance

Quick Start: Select Ubuntu. This is Ubuntu Server 24.04 LTS - AMI ami-075686beab831bb7f

Select Instance Type t2.large

Select Key Pair dcv-key-pair (has already been created)

Choose Security Group "NICE DCV" - with 2 Inbound Rules

- UDP Port 8443
- TCP Port 8443

Launch instance reports success.

Wait for instance to initialize and pass 2/2 status checks.

Unable to connect to instance to install DCV software. NICE DCV security group did not have SSH access, and no AWS Session Manager IAM Role was assigned.

Terminate instance.

EC2->Security Group copy Nice DCV Security group to new security group called Nice DCV + SSH

Add rule permitting inbound TCP traffic on port 22 (SSH) from my IP address.

Save.

Launch new Ubuntu instance with Nice DCV + SSH Security Group.

Instance launched, but ssh errors trying to connect from MacOS 15.3.2 with the Key Pair (rsa)

```bash
ssh -i "dcv-key-pair.pem" ubuntu@ec2-54-202-245-203.us-west-2.compute.amazonaws.com -v
...
Load key "dcv-key-pair.pem": invalid format
debug1: No more authentication methods to try.
ubuntu@ec2-54-202-245-203.us-west-2.compute.amazonaws.com: Permission denied (publickey).
```

Will generate a new Key Pair 'ec2-key-pair' using ed25519 and try again.

```bash
ssh -i "ec2-key-pair.pem" ubuntu@ec2-35-90-54-90.us-west-2.compute.amazonaws.com
...
Permissions 0644 for 'ec2-key-pair.pem' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "ec2-key-pair.pem": bad permissions
ubuntu@ec2-35-90-54-90.us-west-2.compute.amazonaws.com: Permission denied (publickey).
```

Fix permissions on Key Pair file

```bash
chmod 400 ec2-key-pair.pem
```

```bash
ssh -i "ec2-key-pair.pem" ubuntu@ec2-35-90-54-90.us-west-2.compute.amazonaws.com
...
```

SSH Connection succeded.

### Update Ubuntu

```bash
sudo apt-get update
```

### Install Graphical Desktop on Ubuntu

```bash
# install desktop packages (takes 2-3 minutes)
sudo apt install ubuntu-desktop

# install a desktop manager (seems to have been installed by above command)
sudo apt install gdm3

# reboot
sudo reboot
```

### Download DCV Server Packages

<https://www.amazondcv.com/>

Check architecture

```bash
uname -m
x86_64
```

Download DCV Server 2024.0 for Ubuntu Linux 24, x86_64

```bash
wget https://d1uj6qtbmh3dt5.cloudfront.net/2024.0/Servers/nice-dcv-2024.0-19030-ubuntu2404-x86_64.tgz
```

Unpack DCV Server

```bash
tar xzvf nice-dcv-2024.0-19030-ubuntu2404-x86_64.tgz
```

Install the server

```bash
cd nice-dcv-2024.0-19030-ubuntu2404-x86_64/
# install server
sudo apt install ./nice-dcv-server_2024.0.19030-1_amd64.ubuntu2404.deb
sudo apt install ./nice-xdcv_2024.0.654-1_amd64.ubuntu2404.deb
# install web viewer to allow connections from a web browser
sudo apt install ./nice-dcv-web-viewer_2024.0.19030-1_amd64.ubuntu2404.deb
```

For an instance with no GPU, install a dummy X11 driver and configure X11 to use it.

<https://docs.aws.amazon.com/dcv/latest/adminguide/setting-up-installing-linux-prereq.html#linux-prereq-nongpu>

Install dummy video driver

```bash
sudo apt install xserver-xorg-video-dummy
```

Create the new file `/etc/X11/xorg.conf` with the following contents:

```bash
sudo vi /etx/X11/xorg.conf
```

File Contents

```bash
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
```

Restart X Server for changes to take effect

```bash
sudo systemctl isolate multi-user.target
sudo systemctl isolate graphical.target
```

Start DCV Service

```bash
sudo systemctl enable dcvserver.service
sudo systemctl start dcvserver.service
sudo systemctl status dcvserver.service
```

Create a user at the OS level, and assign a password and home directory.

Follow the prompts to provide information.

```bash
sudo adduser jason
...
```

Added test user jason/jason.

Check DCV Sessions

```bash
sudo dcv list-sessions
There are no sessions available.
```

Create a virtual DCV session for user 'jason'

```bash
sudo dcv create-session console --type virtual --owner jason
```

Check DCV Sessions

```bash
ubuntu@ip-172-31-37-212:~/nice-dcv-2024.0-19030-ubuntu2404-x86_64$ sudo dcv list-sessions
Session: 'console' (owner:jason type:virtual)
```

Connect to Instance using DCV Client on MacOS Sequoia (when DCV Session is running)

Pasted public IP of instance (35.90.54.90) into DCV Client. Used 'jason/jason' as account and password.

Note - the installed software all-in is nearly all of the 8GB storage that was the default when provisioning this instance.

```bash
jason@ip-172-31-37-212:~$ df -h .
Filesystem      Size  Used Avail Use% Mounted on
/dev/root       6.8G  5.9G  862M  88% /
```

Logging out ends the DCV session. The user cannot log in unless there is a DCV session available.

## Reference
