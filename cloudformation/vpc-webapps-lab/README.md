# CloudFormation Lab

## Package
Package command processes stack defined in provided template. It uploads local artifacts, such as source code
for an AWS Lambda function or nested ClodFormation stacks, to an S3 bucket. The command returns a copy
of your template, replacing references to local artifacts with the S3 location where the command uploaded the artifacts.

```commandline
aws cloudformation package --template-file root.yaml \
    --output-template-file root-resolved.yaml \
    --s3-bucket soa-cloudformation-lab-dnipser \
    --s3-prefix soa-lab
```

## Deploy
Deploys the specified template by creating and then executing a change set. If there is no stack defined with such name,
command will create a new stack, otherwise it will generate and apply a change set.
```commandline
aws cloudformation deploy --template-file root-resolved.yaml \
    --stack-name soa-lab \
    --s3-bucket soa-cloudformation-lab-dnipser \
    --s3-prefix soa-lab \
    --capabilities CAPABILITY_IAM
```
### Resolving template parameters using SSM
Some parameters such as IP address allowed to SSH to instances, EC2 AMI's can be externalized to SSM
and resolved automatically during template creation/update. Those parameters are declared with type
`AWS::SSM::Parameter::Value<String>` and have default values stored in SSM Parameter Store.
Following commands can be used to create parameters in Systems Manager Parameter Store
```commandline
aws ssm put-parameter --name SSHSourceIP --type String --value "<IP value>"
aws ssm put-parameter --name SSHKeyName --type String --value "<key name>" 
```
Once parameter is declared it can be referenced in template


## Delete stack
```commandline
aws cloudformation delete-stack --stack-name soa-lab
```
