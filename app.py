#!/usr/bin/env python3

import json

import aws_cdk as cdk

from aws_cdk_dcv_deploy_server.dcv_infra import DcvInfra
from aws_cdk_dcv_deploy_server.dcv_server import DcvServerLinux

app = cdk.App()

# Load the app configuration from the config.json file
try:
    with open("config.json", "r") as config_file:
        config_data = json.load(config_file)
except Exception as e:
    print(f"Could not read the app configuration file. {e}")
    raise e


# Set CDK environment variables
environment = cdk.Environment(
    account=config_data["accountId"], region=config_data["region"]
)

# Create the DCV Infrastructure Stack for Session Manager and Connection Gateway
dcv_infra_stack = DcvInfra(
    app,
    "DcvInfraStack",
    description="(uksb-1tupboc66) (tag:dcv-simple-infra)",
    config_data=config_data,
    env=environment,
)

# Create a DCV Server Instance, using infrastructure components
dcv_server_linux_rocky9_stack = DcvServerLinux(
    app,
    "DcvServerLinuxStackRocky9",
    description="(uksb-1tupboc66) (tag:dcv-server)",
    config_data=config_data,
    vpc=dcv_infra_stack.vpc,
    role_fleet=dcv_infra_stack.role_dcv_fleet,
    sg_dcv_server=dcv_infra_stack.sg_dcv_server,
    os_name="rocky9-no-gpu",
    env=environment,
)
dcv_server_linux_rocky9_stack.add_dependency(dcv_infra_stack)

# Create a DCV Server Instance, using infrastructure components
dcv_server_linux_ubuntu22_stack = DcvServerLinux(
    app,
    "DcvServerLinuxStackUbuntu22",
    description="(uksb-1tupboc66) (tag:dcv-server)",
    config_data=config_data,
    vpc=dcv_infra_stack.vpc,
    role_fleet=dcv_infra_stack.role_dcv_fleet,
    sg_dcv_server=dcv_infra_stack.sg_dcv_server,
    os_name="ub2022-no-gpu",
    env=environment,
)
dcv_server_linux_ubuntu22_stack.add_dependency(dcv_infra_stack)

# Create a DCV Server Instance, using infrastructure components
dcv_server_linux_ubuntu24_stack = DcvServerLinux(
    app,
    "DcvServerLinuxStackUbuntu24",
    description="(uksb-1tupboc66) (tag:dcv-server)",
    config_data=config_data,
    vpc=dcv_infra_stack.vpc,
    role_fleet=dcv_infra_stack.role_dcv_fleet,
    sg_dcv_server=dcv_infra_stack.sg_dcv_server,
    os_name="ub2024-no-gpu",
    env=environment,
)
dcv_server_linux_ubuntu24_stack.add_dependency(dcv_infra_stack)

# Create a DCV Server Instance, using infrastructure components
dcv_server_linux_al2_stack = DcvServerLinux(
    app,
    "DcvServerLinuxStackAL2",
    description="(uksb-1tupboc66) (tag:dcv-server)",
    config_data=config_data,
    vpc=dcv_infra_stack.vpc,
    role_fleet=dcv_infra_stack.role_dcv_fleet,
    sg_dcv_server=dcv_infra_stack.sg_dcv_server,
    os_name="al2-no-gpu",
    env=environment,
)
dcv_server_linux_al2_stack.add_dependency(dcv_infra_stack)

# Create a DCV Server Instance, using infrastructure components
dcv_server_linux_al2023_stack = DcvServerLinux(
    app,
    "DcvServerLinuxStackAL2023",
    description="(uksb-1tupboc66) (tag:dcv-server)",
    config_data=config_data,
    vpc=dcv_infra_stack.vpc,
    role_fleet=dcv_infra_stack.role_dcv_fleet,
    sg_dcv_server=dcv_infra_stack.sg_dcv_server,
    os_name="al2023-no-gpu",
    env=environment,
)
dcv_server_linux_al2023_stack.add_dependency(dcv_infra_stack)

# Create a DCV Server Instance, using infrastructure components
dcv_server_linux_suse15_stack = DcvServerLinux(
    app,
    "DcvServerLinuxStackSUSE15",
    description="(uksb-1tupboc66) (tag:dcv-server)",
    config_data=config_data,
    vpc=dcv_infra_stack.vpc,
    role_fleet=dcv_infra_stack.role_dcv_fleet,
    sg_dcv_server=dcv_infra_stack.sg_dcv_server,
    os_name="suse15-no-gpu",
    env=environment,
)
dcv_server_linux_suse15_stack.add_dependency(dcv_infra_stack)

app.synth()
