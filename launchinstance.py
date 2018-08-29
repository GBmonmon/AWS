import os
import time
import sys
import boto3
import botocore
import botocore.exceptions
from botocore.exceptions import ClientError
import json
class LaunchInstance:


    def __init__(self, service, region):
        self.service = service
        self.region = region
        self.ec2c = boto3.client(self.service, self.region)

    def getVpcAndSubnet(self):
        resp = self.ec2c.describe_subnets()
        vpcid = resp['Subnets'][0]['VpcId']
        subnetlist = self.ec2c.describe_subnets(Filters = [{'Name':'vpc-id','Values':[vpcid]}])
        subnetid = subnetlist['Subnets'][0]['SubnetId']
        return vpcid,subnetid


    def securityGroup(self,securitygrpname = 'aws_gbmonmon1',vpcid = None):
        try:
            securitygrpFilter = [
                {
                    'Name':'group-name',
                    'Values':[securitygrpname]
                }
            ]
            secgroups = self.ec2c.describe_security_groups(Filters = securitygrpFilter)
            secgrptouse = secgroups['SecurityGroups'][0]['GroupId']
            return secgrptouse
        except:
            if vpcid == None: print('No security group, please pass in vpcid as argument to this method...')
            print('No security group, will create security group' + securitygrpname)
            secgrptouse = self.ec2c.create_security_group(GroupName = securitygrpname,
                                                          escription = 'aws class open ssh, http, https',
                                                          VpcId = vpcid)
            print(secgrptouse,'hahaha----------')
            secgrpid = secgrptouse['GroupId']





    def runTheInstance(self):
        pass



service = 'ec2'
region = 'us-west-1'
inst1 = LaunchInstance(service,region)
vpcid, subnetid = inst1.getVpcAndSubnet()
securitygrpid = inst1.securityGroup('aws_gbmonmon11', vpcid)

print(vpcid, subnetid)
print('------------')
print(securitygrpid)
