import os

from aws_cdk import (
    CfnOutput,
    Stack,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk.aws_s3_assets import Asset
from constructs import Construct

vpc_id = "MY-VPC-ID"  # Use an existing VPC
ec2_type = "g4dn.xlarge"  # g4dn.xlarge is recommended instance type for this DCV AMI
key_name = "ec2-key-pair"  # the name of the Key Pair
dcv_linux_ami = ec2.GenericLinuxImage(
    {
        "us-west-2": "ami-017d0c53440a48b8b",  # The Marketplace NiceDCV Amazon Linux 2 instance AMI
    }
)

dirname = os.path.dirname(__file__)


class AwsCdkDcvDeployServerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC - using VPC id defined above
        vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id)

        # AMI
        # use defined AMI above

        # Instance Role and SSM Managed Policy
        role = iam.Role(
            self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )

        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        # Instance
        instance = ec2.Instance(
            self,
            "DCVInstance",
            instance_type=ec2.InstanceType(instance_type_identifier=ec2_type),
            instance_name="DCV-managed-instance-01",
            machine_image=dcv_linux_ami,
            vpc=vpc,
            role=role,
        )

        # Script in S3 as Asset
        asset = Asset(
            self, "Asset", path=os.path.join(dirname, "..", "scripts", "configure.sh")
        )
        local_path = instance.user_data.add_s3_download_command(
            bucket=asset.bucket, bucket_key=asset.s3_object_key
        )

        # Userdata executes script from S3
        instance.user_data.add_execute_file_command(file_path=local_path)
        asset.grant_read(instance.role)

        CfnOutput(self, "Output", value=instance.instance_public_ip)
