#!/bin/bash
#user-name password file-key path-to-file-to-upload
function get_value {
    key="password"

    if [ $(aws s3 ls | grep $usernameIn | wc -l) != 0 ]; then
        value=$(cat ./passwordVerification/$usernameIn | sed 's/{.*\'${key}'":"*\([0-9a-zA-Z|.|_|-|\/]*\)"*,*.*}/\1/g')
    fi
}

usernameIn=$1
passwordIn=$2
fileKeyIn=$3
pathToFileToUpload=$4

if [ $# != 4  ]; then
    echo "Usage > ./uploadfile.sh username password file-key path-to-file-to-upload "
else

    if [ $(aws s3 ls | grep $usernameIn | wc -l) == 0 ]; then
        echo 'No such account...'

    else
        aws s3 cp s3://gbmonmon-alluserbucket-1/${usernameIn} ./passwordVerification
        get_value
        if [ $value == $passwordIn ]; then
            # parse the path
            allobj=$(aws s3 ls s3://${usernameIn})
            defaultIFS=$IFS
            IFS='/'
            arrayForFileName=()
            for i in "${pathToFileToUpload}"; do #???????
                arrayForFileName+=($i)
            done
            indexOfLastEle=$((${#arrayForFileName[*]}-1))
            filename=${arrayForFileName[${indexOfLastEle}]}

            #------------------------------------
            IFS=' '
            for i in ${allobj}; do
                if [[ $i = *${fileKeyIn}* ]]; then
                    findItOrNot='find'
                    break
                else
                    findItOrNot='no'
                fi
            done

            IFS=${defaultIFS}
            if [ $findItOrNot == 'find' ]; then
                read -p 'Do you want to replace the existing file? <yes> or <no>... ' answer
                answer=$(echo $answer | tr '[:upper:]' '[:lower:]')
                if [ $answer == 'yes' ]; then
                    echo $pathToFileToUpload
                    aws s3 cp ${pathToFileToUpload} s3://${usernameIn}/${fileKeyIn}
                elif [ $answer == 'no' ]; then
                    echo 'you did not upload the file...'
                else
                    echo 'Please type in yes or no!'
                fi
            else
                aws s3 cp ${pathToFileToUpload} s3://${usernameIn}/${fileKeyIn}
            fi
            rm ./passwordVerification/*
            echo 'Delete all the file in passwordVerification'
        else
            echo 'wrong password'
            rm ./passwordVerification/*
            echo 'Delete all the file in passwordVerification'
        fi
    fi
fi
