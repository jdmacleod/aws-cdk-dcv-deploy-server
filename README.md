
# AWS CDK - Deploy DCV Server

Creates minimal infrastructure for DCV (a VPC, some roles); Deploys a DCV server instance

- Using a specific DCV instance AMI
- Into an existing VPC
- Using a specific hardware profile

## Prerequisites

- [Python](https://www.python.org/) (tested with Python 3.13, but other versions may work.)
- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html)

## Quickstart

```bash
cdk synth
```

```bash
cdk list
DcvInfraStack
DcvServerLinuxStackRocky9
DcvServerLinuxStackUbuntu22
DcvServerLinuxStackUbuntu24
DcvServerLinuxStackAL2
DcvServerLinuxStackAL2023
DcvServerLinuxStackSUSE15
```

```bash
cdk deploy DcvServerLinuxStackRocky9
...
Outputs:
DcvServerLinuxStackRocky9.ServerInstanceURL = Server was created with public DNS at https://ec2-54-214-202-13.us-west-2.compute.amazonaws.com
```

## CDK Server Stacks

name | OS | default user | notes
--- | --- | --- | --- |
Ubuntu22 | Ubuntu 22 | ubuntu | working
Ubuntu24 | Ubuntu 24 | ubuntu | working with ubuntu pro 24 AMI (not working when tried with 24 LTS AMI)
Rocky9 | Rocky 9 | rocky | working
AL2 | Amazon Linux 2 | ec2-user | working
AL2023 | Amazon Linux 2023 | ec2-user | working
SUSE15 | Suse 15 | ec2-user | working

## Reference

<https://docs.aws.amazon.com/dcv/latest/adminguide/setting-up-installing-linux-prereq.html>

<https://repost.aws/articles/ARJtZxRiOURwWI2qSWjl4AaQ/how-do-i-install-gui-graphical-desktop-on-amazon-ec2-instances-running-ubuntu-linux>
