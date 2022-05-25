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

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        oidc_arn = f"arn:aws:iam::{Stack.of(self).account}:oidc-provider/token.actions.githubusercontent.com"

        provider = iam.OpenIdConnectProvider.from_open_id_connect_provider_arn(
            self, 
            'github_provider', 
            oidc_arn
        )

        principle = iam.OpenIdConnectPrincipal(provider).with_conditions(
            conditions={
                "StringLike": {
                    'token.actions.githubusercontent.com:sub':
                        f'repo:StuMason/serverless-laravel:*'
                }
            }
        )

        principle.add_to_principal_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["sts:AssumeRoleWithWebIdentity"],
                resources=["*"]
            )
        )

        iam.Role(self, "deployment_role",
            assumed_by=principle,
            role_name=f"serverless-laravel-deploy-{stage}",
            max_session_duration=Duration.seconds(3600),
            inline_policies={
                "DeploymentPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=['sts:AssumeRole'],
                            resources=[f'arn:aws:iam::{self.account}:role/cdk-*'],
                            effect=iam.Effect.ALLOW
                        )
                    ]
                )
            }
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


                



