import yaml
import HelperClasses
import boto3


botoClient = boto3.client("ec2")

def ConvertYamlToEC2(yamlPath : str) -> HelperClasses.EC2Instance:
     #Load the config
    with open(yamlPath, 'r') as config:
        try:
            ec2Config = (yaml.safe_load(config)).get('server')
        except yaml.YAMLError as exc:
            print("Incompatible config file, possibly missing server field. Exception:" + exc)
    configUsers = []
    configVolumes = []
    InstanceType = ec2Config.get('instance_type','t2.micro')
    AMIType = ec2Config.get('ami_type','amzn2')
    Architecture = ec2Config.get('architecture','x86_64')
    RootDeviceType = ec2Config.get('root_device_type','ebs')
    VirtualiztionType = ec2Config.get('virtualization_type','hvm')
    MinCount = ec2Config.get('min_count',1)
    MaxCount = ec2Config.get('max_count',1)
    KeyName = ec2Config.get('base_key_name',"")
    if 'users' in ec2Config:
        for user in ec2Config.get('users'):
            try:
                configUsers.append(HelperClasses.User(user.get('login'),user.get('ssh_key')))
            except Exception as exc:
                print("Incompatible format for a given user. Exception: "+exc)
    
    if 'volumes' in ec2Config:
        for volume in ec2Config.get('volumes'):
            try:
                configVolumes.append(HelperClasses.Volume(volume.get('device'),volume.get('size_gb'),volume.get('type'),volume.get('mount')))
            except Exception as exc:
                print("Incompatible format for a given volume. Exception: "+ exc)
    
    try:
        finalEC2Instance = HelperClasses.EC2Instance(configUsers,configVolumes,InstanceType,AMIType,Architecture,RootDeviceType,VirtualiztionType,MinCount,MaxCount,KeyName)
    except Exception as exc:
        print("Invalid parameters given to EC2Instance constructor. Exception" + exc)
    
    return finalEC2Instance
