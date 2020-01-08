# CodeDeploy Lab

## Prerequisites
- EC2 instance with public IP address. This instance will serve as a deployment target of sample web application and also will run CodeDeploy agent. The instance should have tag 'Name' with the value 'cda-codedeploy-lab' and IAM role allowing to list and fetch data from S3  
- IAM role allowing CodeDeploy to install application on target instance. Role ARN (e.g. arn:aws:iam::196612613364:role/cda-codedeploy-lab) should be passed to CodeDeploy CLI as required argument during creation of deployment group.

## Install CodeDeploy agent on target EC2 instance:
Update packages on the target instance and install required dependencies.
```bash
sudo yum update
sudo yum install ruby
sudo yum install wget
```

Install and start CodeDeploy agent
```bash
cd /home/ec2-user
wget https://aws-codedeploy-eu-central-1.s3.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto
sudo service codedeploy-agent status
```

## Create S3 bucket used for storing application binaries
```bash
aws s3 mb s3://cda-codedeploy-bucket198203
```

## Create application archive and load it into CodeDeploy:
```bash
aws deploy create-application --application-name sample-app
aws deploy push --application-name sample-app --s3-location s3://cda-codedeploy-bucket198203/sample-app.zip --description "This is a first revision of the sample application" --ignore-hidden-files
```

## Create deployment group for the application
```bash
aws deploy create-deployment-group --application-name sample-app --deployment-config-name CodeDeployDefault.AllAtOnce --deployment-group-name sample-app-group --ec2-tag-filters Key=Name,Value=cda-codedeploy-lab,Type=KEY_AND_VALUE --service-role-arn arn:aws:iam::196612613364:role/cda-codedeploy-lab
```

## Create new deployment using application package uploaded to S3 
```bash
aws deploy create-deployment --application-name sample-app --deployment-group-name sample-app-group --s3-locatiobucket=cda-codedeploy-bucket198203,key=sample-app.zip,bupdleType=zip
```
