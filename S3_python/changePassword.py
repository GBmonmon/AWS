import boto3
import datetime
import json
import os.path


def readPasswordFromObject(bucketname, keyname, region = 'us-west-1'):
    s3 = boto3.resource('s3', region)
    bucket = s3.Bucket(bucketname)
    key = bucket.Object(keyname)
    resp = key.get(keyname)
    content = resp['Body'].read().decode()
    try:
        j = json.loads(content)
        password = j['Important_data'][0]['password']
        email = j['Important_data'][0]['email']
        return password, email
    except:
        print('Not a proper json format, pls check it...')
   # password = j['Important_data'][0]['password']
   # email = j['Important_data'][0]['email']
    #return password, email





def updatePassword(accountIn, passwordIn):
    s3 = boto3.resource('s3','us-west-1')
    s3_client = boto3.client('s3','us-west-1')
    try:
        passwd, email = readPasswordFromObject(bucketname = 'gbmonmon-alluserbucket', keyname = accountIn)
        if passwordIn == passwd:
            newpassword = input('Type in your new password > ')
            with open(accountIn, 'w') as fh:
                data = { "Important_data":[{"account":accountIn,"password":newpassword, "email":email}], "Created_time":datetime.datetime.today().isoformat() }
                json.dump(data, fh)
                # pros in python that str() would use single quote and json and not load it with single quote.

                #obj.put(Body= str(data).encode() )
            s3.Object(accountIn, accountIn).delete()
            s3_client.upload_file(accountIn, 'gbmonmon-alluserbucket', accountIn)
        else:
            print('Wrong password, try again.')
    except:
        print('there is no such account!')

if __name__ == '__main__':
    accountIn = input('Your account name > ')
    passwordIn = input('Your old password > ')
    updatePassword(accountIn = accountIn, passwordIn = passwordIn)
