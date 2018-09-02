import sqlite3
from launchinstance import LaunchInstance
import boto3
import time
import os

def create_InstanceIdTable():
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS instanceIDs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instance_id text NOT NULL UNIQUE
        )
    ''')


def create_VolumeIdTable():
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS volumeIDs(
            volume_id text,
            instanceIDs_id INTEGER,
            FOREIGN KEY (instanceIDs_id) REFERENCES instanceIDs(id)
        )
    ''')



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
        instanceIdToUse = input('Which running instance id do you want the volumns to attach to?<copy and paste the id>\navailableID:%s > '%(all_instances_id))
    else: print('Type yes or no...')
    try:
        resp = instance1.ec2c.describe_instances(InstanceIds=[instanceIdToUse])
        azone = resp['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone'] ##!!!
        #!!! instanceIdToUse, azone
    except:
        print('wrong instanceID...')

    resp_volume = instance1.ec2c.create_volume(AvailabilityZone=azone, Size=2)
    print(resp_volume)

    volume_id = resp_volume['VolumeId']
    volume_state = resp_volume.get('State')

    bVolumeReady = False
    if (volume_state != 'creating'):
        bVolumeReady = True

    while not bVolumeReady:
        resp_volume = instance1.ec2c.describe_volumes(VolumeIds=[volume_id])
        volume_state = resp_volume['Volumes'][0]['State']
        print('volume state = ' + volume_state)
        if (volume_state == 'available'):
            bVolumeReady = True
        else:
            print('Volume is not ready')
            time.sleep(2)
    resp = instance1.ec2c.attach_volume(Device = '/dev/sdf', Instance=instanceIdToUse, volume=volume_id)
    print('attached volume to EC2 instance')

    print('important >>>',volume_id,instanceIdToUse)

    create_InstanceIdTable()
    create_VolumeIdTable()
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()


    PK_from_instanceIDs = [ i for i in cur.execute('SELECT id FROM instanceIDs WHERE instance_id = (?)',(instanceIdToUse,) )]
    if not PK_from_instanceIDs:
        cur.execute('INSERT INTO instanceIDs(instance_id) VALUES(?)',(instanceIdToUse,))
        conn.commit()
        print('insert instance_id(%s) to table instanceIDs...'%(instanceIdToUse))
    PK_from_instanceIDs = [ i for i in cur.execute('SELECT id FROM instanceIDs WHERE instance_id = (?)',(instanceIdToUse,) )]
    PK_from_instanceIDs = PK_from_instanceIDs[0][0]
    cur.execute('INSERT INTO volumeIDs(volume_id, instanceIDs_id) VALUES(?,?)',(volume_id,PK_from_instanceIDs))
    print('insert volume_id(%s), foreignkey(%s) to table volumeIDs...'%(volume_id,PK_from_instanceIDs))
    conn.commit()
