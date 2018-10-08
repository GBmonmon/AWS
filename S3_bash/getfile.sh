#!/bin/bash
#user-name password file-key path-to-save-file-to
function get_value {
    key="password"

    if [ $(aws s3 ls | grep ${usernameIn} | wc -l) != 0 ]; then
        value=$(cat ./passwordVerification/$usernameIn | sed 's/{.*\'${key}'":"*\([0-9a-zA-Z|.|_|-|\/]*\)"*,*.*}/\1/g')
    fi
}

usernameIn=$1
passwordIn=$2
fileKey=$3
pathToSaveFileTo=$4

if [ ${pathToSaveFileTo: -1} != '/' ]; then
    lastch='/'
    pathToSaveFileTo=$pathToSaveFileTo$lastch
fi


if [ $# != 4 ]; then
    echo 'Usage > ./getfile username password file-key path-to-save-file-to'
else
    if [ $(aws s3 ls | grep ${usernameIn} | wc -l ) == 0 ]; then
        echo 'The account does not exist...'
    else

        aws s3 cp s3://gbmonmon-alluserbucket-1/${usernameIn} $PWD/passwordVerification
        get_value

        if [ $passwordIn == $value ]; then

            if [ $(ls -l ${pathToSaveFileTo} | grep ${fileKey} | wc -l) == 0 ]; then
                aws s3 cp s3://$usernameIn/$fileKey $pathToSaveFileTo$fileKey
            else

                detailFile=$(ls -l ${pathToSaveFileTo} | grep ${fileKey})
                if [ ${detailFile:0:1} == '-' ]; then
                    echo 'Conflicted file name, add .copy as suffix to local conficted file...'
                    suffix='.copy'
                    currfiles=$(ls ${pathToSaveFileTo} | grep ${fileKey})
                    for currfile in ${currfiles}; do
                        mv $pathToSaveFileTo$currfile $pathToSaveFileTo$currfile$suffix
                    done
                    aws s3 cp s3://$usernameIn/$fileKey $pathToSaveFileTo$fileKey

                fi
            fi


        else
            echo 'Wrong password...'
        fi
        rm ./passwordVerification/*
        echo 'Delete all the file in passwordVerification'
    fi

fi
