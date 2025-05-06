import os

import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_kms as kms
from aws_cdk import CfnOutput, Stack
from constructs import Construct


class DcvServerLinux(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc,
        role_fleet,
        sg_dcv_server,
        os_name: str,
        config_data: dict,
        **kwargs,
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC is passed in as a parameter

        # Create references for target subnet
        # Retrieve a public Subnet from the VPC, using the configured Availability Zone parameter
        subnet_target = ec2.SubnetSelection(
            subnets=vpc.select_subnets(
                availability_zones=[config_data["network"]["subnetAZ"]],
                subnet_type=ec2.SubnetType.PUBLIC,
            ).subnets
        )

        # IAM Fleet Role Configuration from Infrastructure stack, passed as parameter

        # DCV Server Security Group from Infrastructure stack, passed as parameter

        ### DCV Server AMI
        dcv_server_ami = ec2.GenericLinuxImage(
            {self.region: config_data["linuxServer"][os_name]["amiId"]}
        )

        # Get KMS Key from Alias/Key Name
        kms_arn = f"arn:aws:kms:{self.region}:{self.account}:alias/{config_data['kmsKeyName']}"
        kms_key = kms.Key.from_key_arn(self, "kms-key", kms_arn)

        # Add the user data script to custom string
        linux_server_user_data_file = open(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "scripts",
                config_data["linuxServer"][os_name]["userData"],
            ),
            "r",
            encoding="utf-8",
        )
        linux_server_user_data_content = linux_server_user_data_file.read()
        linux_server_user_data = ec2.UserData.custom(linux_server_user_data_content)

        # Create a reference to the SSH Key Pair name given in the config.json file
        key_pair = ec2.KeyPair.from_key_pair_attributes(
            self, "DCVKeyPair", key_pair_name=config_data["sshKeypairName"]
        )

        # Create the Linux DCV Server EC2 instance
        linux_server_instance = ec2.Instance(
            self,
            "DcvServerInstance",
            vpc=vpc,
            vpc_subnets=subnet_target,
            instance_type=ec2.InstanceType(
                instance_type_identifier=config_data["linuxServer"][os_name][
                    "instanceType"
                ]
            ),
            machine_image=dcv_server_ami,
            security_group=sg_dcv_server,
            key_pair=key_pair,
            user_data=linux_server_user_data,
            role=role_fleet,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        8, encrypted=True, kms_key=kms_key
                    ),
                )
            ],
        )

        CfnOutput(
            self,
            "ServerInstanceURL",
            value=f"Server was created with public DNS at https://{linux_server_instance.instance_public_dns_name}",
        )
