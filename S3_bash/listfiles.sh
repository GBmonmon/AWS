#!/bin/bash
function get_value {
    key="password"

    if [ $(aws s3 ls | grep $usernameIn | wc -l) != 0 ]; then
        value=$(cat ./passwordVerification/$usernameIn | sed 's/{.*\'${key}'":"*\([0-9a-zA-Z|.|_|-|\/]*\)"*,*.*}/\1/g')
    fi
}

usernameIn=$1
passwordIn=$2

if [ $# != 2 ]; then
    echo 'Usage > ./listfiles.sh username password'
else
    if [ $(aws s3 ls s3://gbmonmon-alluserbucket-1 | grep ${usernameIn} | wc -l ) != 0 ]; then
        aws s3 cp s3://gbmonmon-alluserbucket-1/$usernameIn ./passwordVerification
        get_value
        if [ $passwordIn != $value ]; then
            echo 'wrong password...'
        else
            aws s3 ls s3://${usernameIn}
        fi
        rm ./passwordVerification/*
        echo 'Delete all the file in passwordVerification'
    else
        echo 'The account does not exist...'
        rm ./passwordVerification/*
        echo 'Delete all the file in passwordVerification'
    fi

fi
