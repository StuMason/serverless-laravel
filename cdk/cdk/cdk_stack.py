from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_lambda as lambda_
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from aws_cdk.aws_apigatewayv2_alpha import HttpApi
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # vpc = ec2.Vpc(self, "VPC", max_azs=3, nat_gateways=1)

        laravel_web = lambda_.DockerImageFunction(self, "docker_laravel",
            code=lambda_.DockerImageCode.from_image_asset("../codebase"),
            memory_size=1024,
            timeout=Duration.seconds(120),
            # vpc=vpc,
        )

        web_integration = HttpLambdaIntegration("laravel_web_integration", laravel_web)

        endpoint = HttpApi(self, "api_service",
            default_integration=web_integration
        )

        CfnOutput(self, "api_url", value=endpoint.url)


                



