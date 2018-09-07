import sqlite3
import os
import boto3
import random
import time
import createvolume

def createSnapshotTable():
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Snapshot(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   description text,
                   snapshot_id INTEGER
                   )''')

def createAttachmentTable():
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS Attachment(
                   volumeIDs_id INTEGER,
                   snapshot_id INTEGER,
                   content text,
                   PRIMARY KEY (volumeIDs_id, Snapshot_id)
                   )''')


if __name__ == '__main__':

    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()
    curObj = cur.execute('''
    SELECT volumeIDs.volume_id FROM volumeIDs
    ''')
    lst_volume_id = [i[0] for i in curObj]
    #instance_id = lst[0][1]

    region='us-west-1'
    ec2c = boto3.client('ec2', region_name=region)

    iz = random.randint(1,9999999)
    description = 'gbmonmon-'+str(iz)

    volume_id = input('Enter which volume to use, available volume:%s > '%lst_volume_id)
    volume_PK_OBJ = cur.execute('''SELECT volumeIDs.id FROM volumeIDs
    WHERE volumeIDs.volume_id = (?) ''',(volume_id,))
    volume_PK = [ i[0] for i in volume_PK_OBJ]
    volume_PK = volume_PK[0]


    resp = ec2c.create_snapshot(Description=description, VolumeId=volume_id)
    snapshot_id = resp.get('SnapshotId')
    print('Created snapshot id=%s, description=%s' % (snapshot_id, description))

    createSnapshotTable()
    cur.execute('''
    INSERT INTO Snapshot(snapshot_id, description) VALUES(?,?)
    ''',(snapshot_id,description))
    conn.commit()

    snapshotObj = cur.execute('''
        SELECT id FROM Snapshot WHERE snapshot_id = (?)
    ''',(snapshot_id,))#!!!!
    snapshot_PK = [ i for i in snapshotObj]
    snapshot_PK = snapshot_PK[0][0]



    createAttachmentTable()  # many to many relationship between Snapshot and VolumeIds tables
    snapshotContent = input('Enter the content of snapshot: ')
    cur.execute('''
    INSERT INTO Attachment(volumeIDs_id, Snapshot_id, content) VALUES(?,?,?)
    ''',(volume_PK,snapshot_PK,snapshotContent))
    conn.commit()



    '''
    resp=ec2c.describe_instances(InstanceIds=[instance_id])
    instidfrom_ec2 = resp['Reservations'][0]['Instances'][0]['InstanceId']
    print('instidfrom_ec2=' + instidfrom_ec2 + ' instanceidfrom_file=' + instance_id)
    '''

    '''Let's not terminate the instance we create a new python program for terminating the instance'''
    ##ec2c.terminate_instances(InstanceIds=[instance_id])
    ##print("terminated instance")

    # when delete a instance, associated records and relationships should be deleted as well.
    ##cur.execute('''
    ##DELETE FROM InstanceIds WHERE instance_id = (?)
    ##''',(instance_id,))
    ##cur.execute('''
    ##UPDATE volumeIDs SET instanceIDs_id = NULL WHERE volume_id = (?)
    ##''',(volume_id,))
    ##conn.commit()
