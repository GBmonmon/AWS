import boto3
import os.path
import sys
import json
from changePassword import readPasswordFromObject
from ListFile import listfile

try:
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    usernameIn, passwordIn, filekeyIn_s3, pathIn_machine = sys.argv[1:]
    #usernameIn = 'gbmonmonlove2'; passwordIn = 'test'; pathIn_machine = '/Users/Jerry/Desktop/test.png'; filekeyIn_s3 = 'whatYouUpload/'+pathIn_machine.split('/')[-1];
    #------------------
    try:
        oldpassword, oldemail = readPasswordFromObject('gbmonmon-alluserbucket',usernameIn)
        try:
            if oldpassword == passwordIn:
                s3_client = boto3.client('s3','us-west-1')
                lstOFobj = listfile(usernameIn,passwordIn)
                if filekeyIn_s3 in lstOFobj:
                    answer = input('Do you wanna replace the existing file? Type > (yes, no)\nYour answer: ')
                    answer = answer.lower()
                    if answer == 'yes':
                        s3_client.upload_file(pathIn_machine, usernameIn, filekeyIn_s3)
                        print('Replace the file...')
                    else:
                        print('You did not upload the file!')
                else:
                    s3_client.upload_file(pathIn_machine, usernameIn, filekeyIn_s3)

            else:
                print('wrong password!')
        except:
            print('No such files, check the file\'s name and path!')
    except:
        print('wrong account!')
except:
    print('Usage > python UploadFile.py username password file-key path-to-file-to-upload')
