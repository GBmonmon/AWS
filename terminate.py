import sqlite3
import boto3

def delete_all_running_instances():
    conn = sqlite3.connect('instID_volID.db')
    cur = conn.cursor()

    ec2r = boto3.resource('ec2','us-west-1')
    ec2c = boto3.client('ec2','us-west-1')
    insts = ec2r.instances.filter(Filters = [{'Name':'instance-state-name','Values':['running']}])
    all_instances_id = [ inst for inst in insts]
    for i in all_instances_id:
        inst_id = i.id

        volume_idOBJ = cur.execute('''SELECT volumeIDs.volume_id FROM instanceIDs JOIN volumeIDs
        ON instanceIDs.id = volumeIDs.instanceIDs_id
        WHERE instanceIDs.instance_id = (?)''',(inst_id, ))
        volume_ids = [i[0] for i in volume_idOBJ]

        #1 delete instance itself
        ec2c.terminate_instances(InstanceIds=[inst_id])
        cur.execute('''
        DELETE FROM InstanceIds WHERE instance_id = (?)
        ''',(inst_id,))

        #1 delete its relationship
        for volume_id in volume_ids:
            cur.execute('''
            UPDATE volumeIDs SET instanceIDs_id = NULL WHERE volume_id = (?)
            ''',(volume_id,))
            conn.commit()


delete_all_running_instances()
