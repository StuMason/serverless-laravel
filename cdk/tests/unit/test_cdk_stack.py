import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk.cdk_stack import CdkStack


def test_oidc_setup():
    pass
    # app = core.App()
    # stack = CdkStack(app, "cdk")
    # template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
