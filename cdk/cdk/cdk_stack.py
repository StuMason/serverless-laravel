from aws_cdk import (
    Duration,
    Stack,
    CfnOutput,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_lambda as lambda_,
    aws_rds as rds
)
from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpLambdaIntegration
from aws_cdk.aws_apigatewayv2_alpha import HttpApi
from constructs import Construct
from cdk.github_connection import GithubConnection

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        GithubConnection(self, 
            "github_connection", 
            github_org="StuMason", 
            github_repo="serverless-laravel"
        )

        # vpc = ec2.Vpc(self, "vpc", max_azs=3, nat_gateways=1)

        # lambda_to_proxy_group = ec2.SecurityGroup(self, 'Lambda to RDS Proxy Connection', vpc=vpc)

        # db_connection_group = ec2.SecurityGroup(self, 'Proxy to DB Connection', vpc=vpc)
        # db_connection_group.add_ingress_rule(db_connection_group,ec2.Port.tcp(3306), 'allow db connection')
        # db_connection_group.add_ingress_rule(lambda_to_proxy_group, ec2.Port.tcp(3306), 'allow lambda connection')

        # secret = secretsmanager.Secret.from_secret_name_v2(self, "rds_secret", "rds")

        # credents = rds.Credentials.from_secret(secret)

        # db = rds.DatabaseInstance(self, "db",
        #     engine=rds.DatabaseInstanceEngine.MYSQL,
        #     instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.SMALL),
        #     vpc=vpc,
        #     credentials=credents, 
        #     security_groups=[db_connection_group],
        #     database_name="serverless_laravel"
        # )

        # proxy = db.add_proxy("proxy",
        #     borrow_timeout=Duration.seconds(30),
        #     secrets=[db.secret],
        #     vpc=vpc,
        #     security_groups=[db_connection_group],
        #     require_tls=False
        # )

        laravel_web = lambda_.DockerImageFunction(self, "laravel",
            code=lambda_.DockerImageCode.from_image_asset("../codebase"),
            memory_size=1024,
            timeout=Duration.seconds(120),
            # vpc=vpc,
            # environment={
            #     "DB_HOST": proxy.endpoint,
            #     "DB_USERNAME": "admin",
            #     "DB_PASSWORD": "password"
            # },
            # security_groups=[lambda_to_proxy_group]
        )

        web_integration = HttpLambdaIntegration("laravel_web_integration", laravel_web)

        endpoint = HttpApi(self, "api_service",
            default_integration=web_integration
        )

        CfnOutput(self, "api_url", value=endpoint.url)


                



