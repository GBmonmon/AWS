#!/bin/bash
function createbucket(){
    local bucketname=$1
    local bucketname=$(echo ${bucketname} | tr [:upper:] [:lower:])
    if [ $(ls | grep error | wc -l) == 0 ]; then
        mkdir error
    fi
    aws s3 mb s3://${bucketname} 2> ./error/${bucketname}
    if [ $(cat ./error/${bucketname} | grep error | wc -l) != 0 ]; then
        echo "This name has been used, use another name! Or you can use changepassword.sh"
        message="This name has been used, use another name! Or you can use changepassword.sh"
    fi
}


function createuser(){
    createbucket $1
    if [ $(cat ./error/$1 | grep error | wc -l) == 0 ]; then
        cat <<EOF > $PWD/$1
{"password":$2, "email":$3, "bucketname":$1}
EOF
        aws s3 cp $1 s3://${managebucket}
        rm ./error/* 2> /dev/null
    fi
    rm ./error/* 2> /dev/null
}


if [ $# == 3 ]; then
    managebucket='GBmonmon-alluserbucket-1'
    managebucket=$(echo ${managebucket} | tr '[:upper:]' '[:lower:]')
    doWeHavemanageBucket=$(aws s3 ls | grep ${managebucket} | wc -l)
    if [ ${doWeHavemanageBucket} == 0 ]; then
        aws s3 mb s3://${managebucket} --region us-west-1
    fi

    usernameIn=$1
    passwordIn=$2
    emailIn=$3
    createuser ${usernameIn} ${passwordIn} ${emailIn}
else
    echo "Usage > ./createuser.sh username password email"
fi
