import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_cdk_dcv_deploy_server.aws_cdk_dcv_deploy_server_stack import AwsCdkDcvDeployServerStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_cdk_dcv_deploy_server/aws_cdk_dcv_deploy_server_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCdkDcvDeployServerStack(app, "aws-cdk-dcv-deploy-server")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
