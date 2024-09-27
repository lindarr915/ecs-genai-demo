from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr_assets as ecr_assets,
)


class EcsGenaiDemoStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Build Docker image
        docker_image = ecr_assets.DockerImageAsset(self, "DockerImage",
            directory="./app",
            file="Dockerfile_stable_diffusion",
            platform=ecr_assets.Platform.LINUX_AMD64
        )

        # Add ECS task definition
        task_definition = ecs.Ec2TaskDefinition(self, "TaskDef")
        container = task_definition.add_container("WebContainer",
            image=ecs.ContainerImage.from_docker_image_asset(docker_image),
            memory_limit_mib=8192,
            # use FireLens to send logs to CloudWatch
            logging=ecs.LogDriver.aws_logs(stream_prefix="ecs-genai-demo")
        )   
        
        container.add_port_mappings(ecs.PortMapping(container_port=8000))

        vpc = ec2.Vpc(self, "MyVPC", max_azs=2)
        
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)
        
        cluster.add_capacity("DefaultAutoScalingGroupCapacity",
            instance_type=ec2.InstanceType("g5.xlarge"),
            desired_capacity=2,
            machine_image=ecs.EcsOptimizedImage.amazon_linux2023(ecs.AmiHardwareType.GPU)
            
        )
        
        ecs_patterns.ApplicationLoadBalancedEc2Service(self, "MyEC2Service",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            public_load_balancer=True
        )

        # The ECS cluster with a load balancer-based application has been created above

        # Add Load Balancer Endpoint as CloudFormation output

