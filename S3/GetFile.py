import boto3
import shutil
import sys
import os.path
from changePassword import readPasswordFromObject
import json
import random
import string


def generator(size = 4):
    aci = string.ascii_lowercase+string.digits
    ran = ''.join([random.choice(aci) for i in range(size)])
    return ran



try:

    usernameIn, passwordIn, file_key_s3In, machine_pathIn = sys.argv[1:]
    #usernameIn = 'gbmonmonlove2'; passwordIn = 'test'; file_key_s3In = 'whatYouUpload/test.png'; machine_pathIn = '/Users/Jerry/Desktop/downloads/'
    #-----------
    currpath = os.getcwd()


    currpassword, curremail = readPasswordFromObject('gbmonmon-alluserbucket',usernameIn)
    if currpassword == passwordIn:
        s3 = boto3.resource('s3', 'us-west-1')

        if not machine_pathIn.endswith('/'): machine_pathIn = machine_pathIn+'/'

        fileFromS3 = file_key_s3In.split('/')[-1]
        if os.path.isdir(currpath+fileFromS3):
            print('It is a dir, no actions taken...')
        elif os.path.isfile(fileFromS3):
            savefilename = fileFromS3 + generator() + '.bak'
            shutil.move(fileFromS3, savefilename)

        if fileFromS3 == usernameIn: print('You can not download the file storing password and email')
        else:
            s3.Bucket(usernameIn).download_file(file_key_s3In, fileFromS3)
            if os.path.isfile(machine_pathIn + fileFromS3):
                savefilename = fileFromS3 + generator() + '.bak'
                print('Add a suffix \".bask\" to avoid the name conflict with newly downloaded file.')
                shutil.move(machine_pathIn+fileFromS3, machine_pathIn + savefilename)
            shutil.move(currpath + '/' + fileFromS3, machine_pathIn + fileFromS3)
            print('Download the file \"%s\" in \"%s\"'%(fileFromS3, machine_pathIn))

    else: print('wrong password...')
except:
    print('Usage > python GetFile.py username password file-key path-to-save-file-to')
