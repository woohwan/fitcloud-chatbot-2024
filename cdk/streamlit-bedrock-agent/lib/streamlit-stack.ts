import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as ec2 from 'aws-cdk-lib/aws-ec2'
import * as logs from 'aws-cdk-lib/aws-logs'
import * as iam from 'aws-cdk-lib/aws-iam'
import { DockerImageAsset } from 'aws-cdk-lib/aws-ecr-assets'
import { CfnHostedZone, HostedZone } from 'aws-cdk-lib/aws-route53'
// import { log } from 'console';

export class StreamlitStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create a VPC with public subnets only and 2 max azs
    const vpc = new ec2.Vpc(this, 'MyVpc', {
      maxAzs: 2,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'public-subnet',
          subnetType: ec2.SubnetType.PUBLIC
        },
      ],
    });


    // Create an ECS Cluster named "bedrock-ecs-cluster"
    const cluster = new ecs.Cluster(this, 'MyEcsCluster', {
      vpc,
      clusterName: 'bedrock-agent-ecs-cluster',
    });

    // Build and Push Docker image to ECR
    const appImageAsset = new DockerImageAsset(this, 'MyStreamlitAppImage', {
      directory: './lib/docker'
    });

    // Create a new Fargate service with the image from ECR and specify the service name
    const appService = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'MyFargateService', {
      cluster,
      serviceName: 'ecs-bedrock-service',
      taskImageOptions: {
        image: ecs.ContainerImage.fromRegistry(appImageAsset.imageUri),
        containerPort: 8501,
      },
      publicLoadBalancer: true,
      assignPublicIp: true,
      domainName: 'fitcloud.steve-aws.com',
      domainZone: HostedZone.fromHostedZoneAttributes(this, "HostedZone", {
        hostedZoneId: 'Z0582530BV26P4AI9BGR',
        zoneName: 'steve-aws.com'
      })
    })

    const bedrock_iam = new iam.Policy(this, 'BedrockPermissionPolicy', {
      statements: [
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            // Add Bedrock permission here
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream",
            "bedrock:InvokeAgent"
          ],
          resources: [
            "arn:aws:bedrock:us-east-1::foundation-model/*",
            "arn:aws:bedrock:us-east-1:532805286864:agent-alias/IUFLFZG1TW/GDOGYNUEF9",
          ]
        })
      ]
    })

    // Add the Bedrock permission to the task role
    appService.taskDefinition.taskRole?.attachInlinePolicy(bedrock_iam)

    // Grant ECR repository permission for the task execution role
    appImageAsset.repository.grantPullPush(appService.taskDefinition.executionRole!);

    // Grant permission for Cloudwatch logs
    const logGroup = new logs.LogGroup(this, 'MyLogGroup', {
      logGroupName: '/ecs/my-fargate-service',
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    logGroup.grantWrite(appService.taskDefinition.executionRole!)

  }
}