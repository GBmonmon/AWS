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
            if vpcid == None:
                print('No security group, please pass in vpcid as argument to this method...')
                exit()
            print('No security group, will create security group' + securitygrpname)
            secgrptouse = self.ec2c.create_security_group(GroupName = securitygrpname,
                                                          Description = 'aws class open ssh, http, https',
                                                          VpcId = vpcid)
            secgrpid = secgrptouse['GroupId']
            print('Create security group > ', secgrpid)
            portlist = [22,80,443]
            for port in portlist:
                try:
                    getvpcandsubnet.ec2c.authorize_security_group_ingress(
                        CidrIp='0.0.0.0/0',
                        FromPort=port,
                        GroupId=secgrpid,
                        IpProtocol='tcp',
                        ToPort=port
                    )
                except:
                    print('error opening port: '+ port)
                    exit()
            return secgrpid






    def runTheInstance(self):
        pass



if __name__ = '__main__':
    service = 'ec2'
    region = 'us-west-1'
    inst1 = LaunchInstance(service,region)
    vpcid, subnetid = inst1.getVpcAndSubnet()
    securitygrpid = inst1.securityGroup('aws_gbmonmon1', vpcid)

    print(vpcid, subnetid)
    print('------------')
    print(securitygrpid)
