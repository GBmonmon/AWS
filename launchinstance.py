import os
import time
import sys
import boto3
import botocore
import botocore.exceptions
from botocore.exceptions import ClientError
import json
import sqlite3
class LaunchInstance:

    def __init__(self, service, region):
        self.service = service
        self.region = region
        self.ec2c = boto3.client(self.service, self.region)
        self.ec2r = boto3.resource(self.service, self.region)

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
                    self.ec2c.authorize_security_group_ingress(
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






    def launch_instance(self,ImageId='ami-824c4ee2',
                        InstanceType='t2.micro',
                        KeyName='first_key_pair',
                        SecurityGroupIds='sg-32ce954a',
                        SubnetId=None,
                        MaxCount=1,
                        MinCount=1):
        conn = sqlite3.connect('instID_volID.db')
        cur = conn.cursor()

        try:
            SecurityGroupIds=[SecurityGroupIds]
            numinstances = 1
            resp = self.ec2c.run_instances(
                ImageId=ImageId,
                InstanceType=InstanceType,
                KeyName=KeyName,
                SecurityGroupIds=SecurityGroupIds,
                SubnetId=SubnetId,
                MaxCount=numinstances,
                MinCount=numinstances)
        except:
            print("exception:", sys.exc_info()[0])
            raise

        print('waiting for instance')
        inst=resp["Instances"][0]
        instid=inst["InstanceId"]
        print('Waiting for instance to enter running state')
        bIsRunning = False

        wait = '#'
        while bIsRunning == False:
            rz=self.ec2c.describe_instance_status(InstanceIds=[instid])
            #call can return before all data is available
            print(wait)
            if wait: wait+='#'
            time.sleep(4)  # avoid to many request from describe_instance_status
            if not bool(rz):
                #sys.stdout.write('.')
                continue
            if len(rz["InstanceStatuses"]) == 0:
                #sys.stdout.write('.')
                continue
            #print('----------------')
            instance_id = rz['InstanceStatuses'][0]['InstanceId']
            #print('----------------')
            inststate=rz["InstanceStatuses"][0]["InstanceState"]
            print(json.dumps(inststate,indent=2,separators=(',',':')))
            state=inststate["Name"]
            if state == 'running':
                bIsRunning = True

            #else:
                #sys.stdout.write('.')
                #
        self.create_InstanceIdTable()
        record = cur.execute('SELECT * FROM instanceIDs WHERE id = (?)',(instance_id,))
        record = [ i for i in record]
        if not record:
            cur.execute('INSERT INTO instanceIDs(instance_id) VALUES(?)',(instance_id,))
            conn.commit()
        print('EC2 instance is running')
        return inst


    def create_InstanceIdTable(self):
        conn = sqlite3.connect('instID_volID.db')
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS instanceIDs(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instance_id text
            )
        ''')




if __name__ == '__main__':
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()
    service = 'ec2'
    region = 'us-west-1'
    inst1 = LaunchInstance(service,region)
    vpcid, subnetid = inst1.getVpcAndSubnet()
    securitygrpid = inst1.securityGroup('aws_gbmonmon1', vpcid)
    #print(vpcid, subnetid)
    #print('------------')
    #print(securitygrpid)
    inst1.launch_instance(SecurityGroupIds=securitygrpid,SubnetId=subnetid)
