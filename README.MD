# Fetch Rewards Assessment  

This is the coding exercise that was given to me for Fetch Rewards.

## Description

Main.py will take a YAML formatted config for an EC2 instance and create said instance for the users AWS subscription.
The functions created are intended to be versitile as well to create an instance programatically as well.

## Getting Started

The first step to make this run is you (The user) must have an AWS subscription.

You must also set up the AWS CLI on your box. Intructions can be found here https://docs.aws.amazon.com/polly/latest/dg/setup-aws-cli.html.

Once complete ensure that boto3 is installed and set up on your box. Documentation can be found here https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html.

After completing those steps, we are pretty close to running the program; we just have to make a few tweaks to the config.
  - Open EC2Config.yaml and replace user1 and user2 SSH keys. These keys are the public must be made prior in the EC2 console, and then converted to the public key via ssh keygen. 
    -  Docs on this step: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
    -  IT IS IMPORTANT THAT YOU DO NOT OMMIT THE SSH-RSA TAG FROM THE EDIT TO THE CONFIG.
    -  This is an example: ssh-rsa AB3nzExample
  
### Dependencies

* AWS Account
* AWS CLI
* Boto3
* Python 3

### Installing

The files must be downloaded or cloned from this repo. IT IS IMPORTANT THAT YOU DO NOT CHANGE THE FOLDER STRUCTURE, AS EVERYTHING SHOULD BE IN THE SAME FOLDER.

### Executing program

* This can be ran via a Python3 call whether that be in an IDE like VSCode or on the command line.

1. Open Command Prompt or your system's Command Line equivalent
2. Navigate to the folder holding all files.
3. Run following command
```
Python3 Main.py
```

### Known Issues:
According to the prompt, XVDA should be ext4, but it is xfs. AWS has XFS as the default filesystem for an EC2 instance. I couldn't find a way to do this s.t. the volume is ext4.
In the real world, I would create AMI's that have a default filesystem of ext4 and store my custom AMIs in a seperate KeyValue formatted file s.t. I can call those AMI IDs. My background
is in Azure professionally, but I am extremely driven to be the best possible DevOps Engineer.

