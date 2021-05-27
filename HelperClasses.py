import base64
from io import SEEK_CUR
from botocore import retryhandler
import boto3

#I was using this for debugging. AWS doesn't seem to suppoer fs_setup but this was an effor to get xvda ext4.
DD = """#cloud-config
disk_setup:
  /dev/xvda:
    layout: true
    overwrite: true
    table_type: 'mbr'
  /dev/xvdf:
    layout: true
    overwrite: true
    table_type: 'gpt'


mounts:
  - [xvda, /,"ext4","defaults,nofail", "0", "0"]
  - [xvdf, /data,"xfs","defaults,nofail", "0", "0"]

#setup the file system on the device
fs_setup:
  - label: None
    filesystem: 'ext4'
    device: '/dev/xvda'
  - label: data
    filesystem: 'xfs'
    device: '/dev/xvdf'

runcmd:
  - mkdir /data

cloud_final_modules:
- [users-groups,always]
users:
  - name: user1
    groups: [ wheel ]
    sudo: [ "ALL=(ALL) NOPASSWD:ALL" ]
    shell: /bin/bash
    ssh-authorized-keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCRLakdFmNzl0EsfSEr5DWgPqk6QB2timG2z7/nWY7mtzBk0/k43KxJVwS8w9w0DzhWEnZ0dkBcpK21fmC7CStQS3Lp6rqnItcdxT0o2MmL1j+am8jlPQgSKbPs6RGCE5GKQOckdxEU+1S3PztE59Jkv0lApHqF3XhwKgvYmls6MUy8zSN0lnHY4uY/FqNJt2BcVp/B5XwC8LWoQiiig2qyy7XnK3IDVygtY2OYdR12XYWHZgtartj8dzHK7QoRfDq9kbPVWtHKLSEuTZMyh2CFUiC89YHfn1V/iJjO/ePcFCehbM4CT9Yh9GGph0WwHdcS8/gSG9ltIAqRYtWTWeVt
  - name: user2
    groups: [ wheel ]
    sudo: [ "ALL=(ALL) NOPASSWD:ALL" ]
    shell: /bin/bash
    ssh-authorized-keys:
      - ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCo+ByZ5911ZKd4lTLlDpk6G5bwecBcZSRZIeXFsdd9suaBMNJNYIuEQDDkAiFJfuW7bxCxGRmBwz3Y+sZpAVcPAnXN94p1xm+lGUwLNkL6GOESiJEqDKIkvEVYfyG4VrIp74C10Kc1HPVpNeJPdu9g/wECn9IDKC32bi1MizHTLqi5tdNI8Q+M+0H1Gqp1447j9G4ixVfYGM05hhUA1+nHCss1EO2nfuQEUXkOQXVpm6sNKojQOzS12y3S9mwl8mNRvaeecEmkggko8zU/WIsfpbhaSOaSrKs3uZSlYNGNt/gtCza5AVdjoVj9QcLkcD9mU8CjWJkcjG6F7EPrrvM1"""



class User:
    UserName = ""
    SSHKey = ""

    def __init__(self, userName ="GenericUser", sshKey = None):
        self.UserName = userName
        self.SSHKey = sshKey

class Volume:
    DeviceName = ""
    Size = 0
    Type = ""
    MountPath = ""

    def __init__(self, deviceName ="dev/xvda", deviceSize = 5, deviceType="ext4",mountPath="/"):
        self.DeviceName = deviceName
        self.Size = deviceSize
        self.Type = deviceType
        self.MountPath = mountPath

class EC2Instance:
    Users = []
    Volumes = []
    InstanceType = ""
    AMIType = ""
    Architecture = ""
    RootDeviceType = ""
    VirtualiztionType = ""
    MinCount = 1
    MaxCount = 1
    BaseKeyName = ""
    botoClient = None
    
    def __init__(self, ec2Users =[User()], ec2Volumes = [Volume()], instanceType="t2.micro", amazonInstanceType = "amzn2", systemArchitecture = "x86_64", rootDeviceType = "ebs", vmType = "hvm",minimumCount = 1, maximumCount=1, baseKeyName = ""):
        self.Users = ec2Users
        self.Volumes = ec2Volumes
        self.InstanceType = instanceType
        self.AMIType = amazonInstanceType
        self.Architecture = systemArchitecture
        self.RootDeviceType = rootDeviceType
        self.VirtualiztionType = vmType
        self.MinCount = minimumCount 
        self.MaxCount = maximumCount
        self.BaseKeyName = baseKeyName
        self.botoClient = boto3.client("ec2")

    
    def GetAMIID(self):
        try:
            response = self.botoClient.describe_images(
                Filters=[
                    {
                        'Name': 'name',
                        'Values': [
                            f'*{self.AMIType}-ami-{self.VirtualiztionType}-*-{self.Architecture}-{self.RootDeviceType}',
                        ]
                    },
                    {
                        'Name': 'architecture',
                        'Values': [
                            f'{self.Architecture}'
                        ]
                    },
                    {
                        'Name': 'root-device-type',
                        'Values': [
                            f'{self.RootDeviceType}'
                        ]
                    },
                    {
                        'Name': 'virtualization-type',
                        'Values': [
                            f'{self.VirtualiztionType}'
                        ]
                    },
                ],
                Owners=[
                    'amazon'
                ]
            )
        except Exception as exc:
            print("Invalid AMI entry. This relies on AMIType,VirtualizationType,Architecture,and RootDeviceType from config. Exception:" + exc)
        
        AMIs = response.get('Images')
        AMIs.sort(key = lambda x:x['CreationDate'],reverse = True)
        return(AMIs[0].get('ImageId'))


   
    def CreateFirstRunScript(self):
        #Initiate
        FirstRunCommands = ["#cloud-config\n"]
        BootCommands = ["bootcmd:"]
        UserBlock = []

        #Setting up volumes
        for volume in self.Volumes:
            BootCommands.append(f"""
  - mkfs -t {volume.Type} {volume.DeviceName}
  - mkdir -p {volume.MountPath}
  - mount {volume.DeviceName} {volume.MountPath}""")

        if(len(self.Users) >= 1):
            UserBlock.append("""
cloud_final_modules:
- [users-groups,always]
users:""")
        #Initiate user block        
        for user in self.Users:
            UserBlock.append(f"""
  - name: {user.UserName}
    groups: [ wheel ]
    sudo: [ "ALL=(ALL) NOPASSWD:ALL" ]
    shell: /bin/bash
    ssh-authorized-keys: 
      - ssh-rsa {user.SSHKey}""")
        FirstRunCommands = FirstRunCommands + BootCommands + UserBlock
        return  ''.join(FirstRunCommands)

            
    def CreatInstance(self):
        print("Attempting to create new EC2 instance with current EC2 object.")
        BlockDeviceMapping=[]
        for volume in self.Volumes:
            BlockDeviceMapping.append(
                {
                    "DeviceName": volume.DeviceName,
                    "Ebs":{
                        "DeleteOnTermination" : True,
                        "VolumeSize" : volume.Size
                    }
                }
            )
        if(self.BaseKeyName == None):
            self.BaseKeyName = ""
        try:
            response = self.botoClient.run_instances(
                BlockDeviceMappings = BlockDeviceMapping,
                ImageId = self.GetAMIID(),
                InstanceType = self.InstanceType,
                MinCount = self.MinCount,        
                MaxCount = self.MaxCount,
                UserData = self.CreateFirstRunScript(),
                KeyName = self.BaseKeyName,
            )
        except Exception as exc:
            print("Something went wrong when trying to create instance. Exception:" + exc)
        return response


