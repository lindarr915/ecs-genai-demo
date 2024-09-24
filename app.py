#!/usr/bin/env python3

import aws_cdk as cdk

from ecs_genai_demo.ecs_genai_demo_stack import EcsGenaiDemoStack


app = cdk.App()
EcsGenaiDemoStack(app, "EcsGenaiDemoStack")

app.synth()
