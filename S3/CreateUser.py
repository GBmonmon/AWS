import datetime
import boto3
import os.path
import sys
import random
import string
import json

def generator(size = 7):
    asci = string.ascii_lowercase + string.digits
    id = ''.join([random.choice(asci) for i in range(size)])
    print(id)


# return False if bucketName is not in s3
def doesBucketExist(bucketName):
    s3 = boto3.client('s3', 'us-west-1')
    response = s3.list_buckets()
    allBucketNames = [doc['Name'] for doc in response['Buckets'] ]
    if bucketName not in allBucketNames: return False


def createBucket(bucketUserName):
    bucketUserName = bucketUserName.lower()
    s3 = boto3.client('s3','us-west-1')
    if doesBucketExist(bucketUserName) == False:
        s3.create_bucket(Bucket = bucketUserName, CreateBucketConfiguration = {'LocationConstraint':'us-west-1'})
    else:
        if bucketUserName != 'gbmonmon-alluserbucket':
            print('User name has been used, pls change another one...')
            print('If you want to change the password, type changePassword.py')

def createUser(Username, password, email):
    data = { 'Important_data':[{'account':Username,'password':password, 'email':email}], 'Created_time':datetime.datetime.today().isoformat() }
    Username = str(Username).lower()
    filename = Username
    if os.path.isfile(filename): print('The file has already existed...!')
    else:
        with open(filename, 'w') as fh:
            json.dump(data, fh)

    createBucket(bucketUserName = Username)
    uploadPasswordEmail(filename = Username, bucketname = 'gbmonmon-allUserBucket', key = Username)

def uploadPasswordEmail(filename, bucketname, key):
    s3 = boto3.client('s3','us-west-1')
    s3.upload_file(filename, 'gbmonmon-alluserbucket', key)


if __name__ == '__main__':
    try:
        username, password, email = sys.argv[1:]
        manageUserBucket = 'gbmonmon-allUserBucket'
        if not doesBucketExist(manageUserBucket):
            createBucket(manageUserBucket)
        createUser(username, password, email)
    except:
        print('usage > python CreateUser.py username password email')
