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

        vpc = ec2.Vpc(self, "VPC", max_azs=3, nat_gateways=1)

        laravel_web = lambda_.Function(self, "laravel_web",
            runtime=lambda_.Runtime.PROVIDED_AL2,
            handler="public/index.php",
            code=lambda_.Code.from_asset("../codebase"),
            vpc=vpc,
            layers=[
                lambda_.LayerVersion.from_layer_version_arn(
                    self, 
                    "bref_php_layer",
                    "arn:aws:lambda:eu-west-2:209497400698:layer:php-81-fpm:19"
                )
            ],
            timeout=Duration.seconds(120),
            environment={"APP_STORAGE": "/tmp","APP_ENV": "production"}
        )

        web_integration = HttpLambdaIntegration("laravel_web_integration", laravel_web)

        endpoint = HttpApi(self, "api_service",
            default_integration=web_integration
        )

        CfnOutput(self, "api_url", value=endpoint.url)


                



