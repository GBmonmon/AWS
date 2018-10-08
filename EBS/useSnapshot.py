import sqlite3
import os
import time
import boto3
from launchinstance import LaunchInstance
import string
import random

conn = sqlite3.connect('instID_volID.db')
cur = conn.cursor()
bol = True
while bol:
    print('Choose 1 or 2')
    ans = input('''Use the snapshot by 1. creating a new instance
                    2. using the existing instance
your choice: ''')
    if ans == '1':
        snapObj = cur.execute('''
        SELECT Snapshot.description, Snapshot.snapshot_id, Attachment.content
        FROM Snapshot JOIN volumeIDs JOIN Attachment
        ON Attachment.volumeIDs_id = VolumeIds.id
        AND Attachment.Snapshot_id = Snapshot.id
        ''')
        listOFSnapshot = [i for i in snapObj]
        content = [ listOFSnapshot[i][2] for i in range(len(listOFSnapshot))]
        snapShotcontent = input('Which Snapshot content you wanna use: %s: '%(content))

        snapToUseObj = cur.execute('''
        SELECT Snapshot.description, Snapshot.snapshot_id, Attachment.content
        FROM Snapshot JOIN volumeIDs JOIN Attachment
        ON Attachment.volumeIDs_id = VolumeIds.id
        AND Attachment.Snapshot_id = Snapshot.id WHERE Attachment.content = (?)
        ''',(snapShotcontent,))
        snapToUse = [i for i in snapToUseObj]

        snapIdToUse = snapToUse[0][1]
        print("using snapshot-id:" + snapIdToUse)

        #lauch a new instance
        instance1 = LaunchInstance('ec2','us-west-1')
        vpcid, subnetid = instance1.getVpcAndSubnet()
        securitygrpid = instance1.securityGroup('aws_gbmonmon1', vpcid)
        inst1 = instance1.launch_instance(SecurityGroupIds=securitygrpid,SubnetId=subnetid)


        instid = inst1['InstanceId']
        azone=inst1['Placement']['AvailabilityZone']

        ec2c = boto3.client('ec2','us-west-1')
        resp=ec2c.create_volume(AvailabilityZone=azone,SnapshotId=snapIdToUse) #???
        volume_id = resp['VolumeId']
        print('created volume " + volume_id +  " in availability-zone ' + azone + ' from snapshot=' + snapIdToUse)

        bVolumeReady = False
        while not bVolumeReady:
            resp = ec2c.describe_volumes(VolumeIds=[volume_id])
            volume_state = resp['Volumes'][0]['State']
            print('volume state = ' + volume_state)
            if (volume_state == 'available'):
                bVolumeReady = True
            else:
                print('Volume is not ready')
                time.sleep(20)
        device = '/dev/sdf'
        resp = ec2c.attach_volume(Device=device, InstanceId=instid,VolumeId=volume_id)
        print('attached volume(%s) to EC2 instance(%s)'%(volume_id, instid ))

        cur.execute('''
        INSERT INTO InstanceIds(instance_id) VALUES(?)
        ''',(instid,))
        conn.commit()

        selectInstPK = cur.execute('SELECT id FROM instanceIDs WHERE instance_id = (?)',(instid,))
        instPK = [ _ for _ in selectInstPK]
        instPK = instPK[0][0]

        cur.execute('INSERT INTO VolumeIDs(volume_id, instanceIDs_id, device) VALUES(?,?,?)',(volume_id,instPK,device))
        conn.commit()
        VolumeOBJ = cur.execute('''SELECT VolumeIDs.id FROM VolumeIDs JOIN instanceIDs
                     ON volumeIDs.instanceIDs_id = instanceIDs.id
                     WHERE VolumeIDs.volume_id = ? AND instanceIDs.id = ?''',(volume_id,instPK))
        VolumePK = [ i[0] for i in VolumeOBJ]
        VolumePK = VolumePK[0]

        snapshotOBJ = cur.execute('''SELECT Snapshot.id FROM VolumeIDs JOIN Attachment JOIN Snapshot
                     ON volumeIDs.id = Attachment.volumeIDs_id AND Snapshot.id = Attachment.snapshot_id
                     WHERE Snapshot.snapshot_id = (?)''',(snapIdToUse,))
        snapshotPK = [ i[0] for i in snapshotOBJ]
        snapshotPK = snapshotPK[0]

        cur.execute('INSERT INTO Attachment(volumeIDs_id, snapshot_id, content) VALUES (?,?,?)',(VolumePK,snapshotPK,snapShotcontent))
        conn.commit()
        bol = False
    elif ans == '2':
        ec2c = boto3.client('ec2','us-west-1')
        allinstidOBJ = cur.execute('SELECT instance_id FROM InstanceIDs')
        allinstid = [ _[0] for _ in allinstidOBJ]
        print('Available instance: ',allinstid)
        instanceIdToUse = input('InstanceId to use: ')

        snapObj = cur.execute('''
        SELECT Snapshot.description, Snapshot.snapshot_id, Attachment.content
        FROM Snapshot JOIN volumeIDs JOIN Attachment
        ON Attachment.volumeIDs_id = VolumeIds.id
        AND Attachment.Snapshot_id = Snapshot.id
        ''')
        listOFSnapshot = [i for i in snapObj]
        content = [ listOFSnapshot[i][2] for i in range(len(listOFSnapshot))]
        snapShotcontent = input('Which Snapshot content you wanna use: %s: '%(content))

        snapToUseObj = cur.execute('''
        SELECT Snapshot.description, Snapshot.snapshot_id, Attachment.content
        FROM Snapshot JOIN volumeIDs JOIN Attachment
        ON Attachment.volumeIDs_id = VolumeIds.id
        AND Attachment.Snapshot_id = Snapshot.id WHERE Attachment.content = (?)
        ''',(snapShotcontent,))
        snapToUse = [i for i in snapToUseObj]

        snapIdToUse = snapToUse[0][1]
        print("using snapshot-id:" + snapIdToUse)
        azone = ec2c.describe_instances(InstanceIds =[instanceIdToUse])['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone']
        resp=ec2c.create_volume(AvailabilityZone=azone,SnapshotId=snapIdToUse) #???
        volume_id = resp['VolumeId']
        print('created volume " + volume_id +  " in availability-zone ' + azone + ' from snapshot=' + snapIdToUse)

        bVolumeReady = False
        while not bVolumeReady:
            resp = ec2c.describe_volumes(VolumeIds=[volume_id])
            volume_state = resp['Volumes'][0]['State']
            print('volume state = ' + volume_state)
            if (volume_state == 'available'):
                bVolumeReady = True
            else:
                print('Volume is not ready')
                time.sleep(20)

        digits = string.ascii_lowercase[5:16] # 'f~p' according to aws
        lastdigit = random.choice(digits)
        device = '/dev/sd'+str(lastdigit)
        using_deviceOBJ = cur.execute('SELECT device FROM instanceIDs JOIN volumeIDs ON instanceIDs.id = volumeIDs.instanceIDs_id')
        using_device = [ _[0] for _ in using_deviceOBJ]
        if len(using_device) >= 11: # 'f~p' according to aws meaning you cannot have more than 11 devices
            exit()

        while device in using_device:
            lastdigit = random.choice(digits)
            device = '/dev/sd'+str(lastdigit)
            if device not in using_device:
                break

        resp = ec2c.attach_volume(Device=device, InstanceId=instanceIdToUse,VolumeId=volume_id)
        print('attached volume(%s) to EC2 instance(%s)'%(volume_id, instanceIdToUse ))

        instanceOBJ = cur.execute('''SELECT instanceIDs.id FROM instanceIDs
                      WHERE instanceIDs.instance_id = (?) ''',(instanceIdToUse,))
        instancePK = [_[0] for _ in instanceOBJ]
        instancePK = instancePK[0]


        cur.execute('''INSERT INTO volumeIDs(volume_id, instanceIDs_id, device) VALUES(?,?,?)''',(volume_id,instancePK,device))
        conn.commit()
        volumeOBJ = cur.execute('''SELECT volumeIDs.id FROM volumeIDs
        JOIN instanceIDs ON instanceIDs.id = volumeIDs.instanceIDs_id
        WHERE volume_id = (?)''',(volume_id,))
        volume_PK = [ _[0] for _ in volumeOBJ ]

        volume_PK = volume_PK[0]


        snapshotOBJ=cur.execute('''SELECT Snapshot.id FROM Snapshot JOIN volumeIDs JOIN Attachment
                       ON volumeIDs.id = Attachment.volumeIDs_id AND Snapshot.id = Attachment.snapshot_id
                       WHERE Snapshot.snapshot_id = (?)''',(snapIdToUse,))
        snapshot_PK = [ i[0] for i in snapshotOBJ ]
        snapshot_PK = snapshot_PK[0]


        cur.execute('''INSERT INTO Attachment(volumeIDs_id, snapshot_id, content) VALUES(?,?,?)''',(volume_PK,snapshot_PK,snapShotcontent))
        conn.commit()
        bol = False
