import sqlite3
from launchinstance import LaunchInstance
import boto3



if __name__ == '__main__':
    service = 'ec2'
    region = 'us-west-1'
    instance1 = LaunchInstance(service,region)
    vpcid, subnetid = instance1.getVpcAndSubnet()
    securitygrpid = instance1.securityGroup('aws_gbmonmon1', vpcid)
    answer = input('Do you want to launch a new instance? <yes> or <no>: ')
    answer = answer.lower()
    if answer == 'yes':
        inst =  instance1.launch_instance(SecurityGroupIds=securitygrpid,SubnetId=subnetid)
        instanceIdToUse=inst['InstanceId']
    elif answer == 'no' or ' ':
        insts = instance1.ec2r.instances.filter(Filters = [{'Name':'instance-state-name','Values':['running']}])
        #print(inst['Reservations'][0]['Instances'][0]['InstanceId'])
        #instances = inst['Reservations'][0]['Instances']
        all_instances_id = [ inst for inst in insts]
        instanceIdToUse = input('Which running instance id do you want to attach the volumns?<copy and paste the id>\navailableID:%s > '%(all_instances_id))
    else: print('Type yes or no...')
    try:
        resp = instance1.ec2c.describe_instances(InstanceIds=[instanceIdToUse])
        azone = resp['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone'] ##!!!
        #!!! instanceIdToUse, azone
        print(azone)
    except:
        print('wrong instanceID...')
