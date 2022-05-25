#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack

app = cdk.App()
CdkStack(app, "cdk-serverless-laravel-staging", 
    env={'region': 'eu-west-2'},
    stage='staging'
)
app.synth()
