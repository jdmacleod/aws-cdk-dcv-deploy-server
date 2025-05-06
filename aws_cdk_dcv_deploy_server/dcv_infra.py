# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
from aws_cdk import Stack
from constructs import Construct


# The NICE DCV INFRA stack - simplified for single DCV workstation support
class DcvInfra(Stack):
    """Class to deploy Simplified DCV infrastructure components"""

    def __init__(
        self, scope: Construct, construct_id: str, config_data: dict, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Check if a VPC and subnets were provided in the config.json file
        if (
            config_data["network"]["vpcId"]
            and config_data["network"]["publicASubnetId"]
            and config_data["network"]["publicBSubnetId"]
            and config_data["network"]["privateASubnetId"]
            and config_data["network"]["privateBSubnetId"]
        ):
            # Create reference for VPC
            self.vpc = ec2.Vpc.from_lookup(
                self, "VPC", vpc_id=config_data["network"]["vpcId"]
            )
            # Create references for private and public subnets
            # using subnet_ids pulled from config.json
            # refs removed - not used in this simplified example

        else:
            # Create new VPC, subnets, and NAT Gateway
            self.vpc = ec2.Vpc(
                self,
                "VPC",
                nat_gateways=1,
                max_azs=2,
                subnet_configuration=[
                    ec2.SubnetConfiguration(
                        name="public-subnet",
                        subnet_type=ec2.SubnetType.PUBLIC,
                        cidr_mask=24,
                    ),
                    ec2.SubnetConfiguration(
                        name="private-subnet",
                        subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                        cidr_mask=24,
                    ),
                ],
            )
            # Create references for private and public subnets
            # using availability zones described above
            # refs removed - not used in this simplified example

        # IAM DCV Fleet Role Configuration
        self.role_dcv_fleet = iam.Role(
            self,
            "DCVFleetRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name="dcv-fleet-role",
        )

        # Permission to get NICE DCV License for DCV fleet role
        self.role_dcv_fleet.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject"],
                resources=[f"arn:aws:s3:::dcv-license.{self.region}/*"],
            )
        )

        # Instance Management via AWS SSM Console for DCV fleet role
        self.role_dcv_fleet.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        iam.CfnInstanceProfile(
            self,
            "DCVServerInstanceProfile",
            instance_profile_name="dcv-server-profile",
            roles=[self.role_dcv_fleet.role_name],
        )

        # DCV server fleet Security Group configuration
        self.sg_dcv_server = ec2.SecurityGroup(
            self,
            "DCVServerSecurityGroup",
            vpc=self.vpc,
            description="SG default ports for Direct DCV Access",
            allow_all_outbound=True,  # Egress all
            disable_inline_rules=True,
        )

        self.sg_dcv_server.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8443),
            "allow TCP DCV access from public internet",
        )
        self.sg_dcv_server.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.udp(8443),
            "allow UDP DCV access from public internet",
        )
