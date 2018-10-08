import boto3
import os.path
import sys
import json
from changePassword import readPasswordFromObject


#usernameIn = 'gbmonmonlove2'; passwordIn = 'test'
#--------
def listfile(usernameIn, passwordIn):

    s3_client = boto3.client('s3', 'us-west-1')
    buckets = s3_client.list_objects(Bucket=usernameIn)
    all_obj = list()
    if 'Contents' not in buckets:
        print('No object in here...')
    else:
        for doc in buckets['Contents']:
            obj = doc['Key']
            all_obj.append(obj)
    return all_obj


if __name__ == '__main__':
    usernameIn, passwordIn = sys.argv[1:]
    try:
        currpassword, curremail = readPasswordFromObject('gbmonmon-alluserbucket',usernameIn)
        if passwordIn == currpassword:
            lstoflobject = listfile(usernameIn,passwordIn)
            if not lstoflobject:
                pass
            else:
                number=1
                for i in lstoflobject:
                    print('%s. %s'%(number,i))
                    number +=1
        else:
            print('wrong password...')
    except:
        print('no sucn account...')
