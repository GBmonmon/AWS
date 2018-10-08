#!/bin/bash
read -p "Enter the username name: " usernameIn
read -p "Enter the old password: " passwordIn

if [ $usernameIn == 1 ]; then
    usernameIn='gbmonmont1'
    echo $usernameIn
fi
if [ $passwordIn == 1 ]; then
    passwordIn='test'
fi


if [ $(ls | grep passwordVerification | wc -l) == 0 ]; then
    mkdir passwordVerification
    echo 'create passwordVerification folder'
fi

aws s3 cp s3://gbmonmon-alluserbucket-1/${usernameIn} ./passwordVerification 2>> /dev/null

function get_value {
    key="password"

    if [ $(aws s3 ls | grep $usernameIn | wc -l) != 0 ]; then
        value=$(cat ./passwordVerification/$usernameIn | sed 's/{.*\'${key}'":"*\([0-9a-zA-Z|.|_|-|\/]*\)"*,*.*}/\1/g')
    fi
}
get_value
if [ $(aws s3 ls | grep $usernameIn | wc -l) != 0 ]; then
    if [ $passwordIn == $value ]; then
        read -p 'You enter the right password, now enter your new password: ' newpassword
        cat ./passwordVerification/${usernameIn} | sed s/${value}/${newpassword}/ > ./${usernameIn}
        aws s3 cp ${usernameIn} s3://gbmonmon-alluserbucket-1
        if [ $(ls ./passwordVerification | grep gbmonmont | wc -l ) != 0 ]; then
            rm ./passwordVerification/*
            echo 'Delete all the file in passwordVerification'
        fi
    else
        if [ $(ls ./passwordVerification | grep gbmonmont | wc -l ) != 0 ]; then
            rm ./passwordVerification/*
            echo 'Delete all the file in passwordVerification'
        fi
        echo wrong password...
    fi
else
    echo 'There is not such account!'
fi
