import HelperFunctions
    
def main():
    EC2InstanceFromYaml = HelperFunctions.ConvertYamlToEC2("EC2Config.yaml")
    Response = EC2InstanceFromYaml.CreatInstance()
    for Instance in Response.get('Instances'):  
        print(f"Instance Created with InstanceId : {Instance.get('InstanceId')}")
    

if __name__ == "__main__":
    main()