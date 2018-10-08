import boto3
import sys
from changePassword import readPasswordFromObject

try:
    usernameIn, passwordIn, key_value_s3In = sys.argv[1:]
    #usernameIn = 'gbmonmonlove2'; passwordIn = 'test'; key_value_s3In = 'whatYouUpload/test.png'
    s3 = boto3.client('s3','us-west-1')

    try:
        currpassword, curremail = readPasswordFromObject('gbmonmon-alluserbucket', usernameIn)
        if passwordIn == currpassword:
            try:
                response = s3.delete_object(Bucket = usernameIn, Key = key_value_s3In)
                print(response)
            except:
                print('wrong key-value on s3, pls check it...')
        else:
            print('wrong password...')
    except:
        print('wrong username...')
except:
    print('Usage > python DeleteFile.py username password key-value-s3')
