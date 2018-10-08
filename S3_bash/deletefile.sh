#!/bin/bash
function get_value {
  key="password"

  if [ $(aws s3 ls | grep $usernameIn | wc -l) != 0 ]; then
      value=$(cat ./passwordVerification/$usernameIn | sed 's/{.*\'${key}'":"*\([0-9a-zA-Z|.|_|-|\/]*\)"*,*.*}/\1/g')
  fi
}

usernameIn=$1
passwordIn=$2
fileKey=$3

if [ $# != 3 ]; then
  echo 'Usage > ./deletefile.sh username password file-key'
else
  aws s3 cp s3://gbmonmon-alluserbucket-1/${usernameIn} ./passwordVerification/${usernameIn}
  get_value
  if [ $passwordIn == $value ]; then
    aws s3 rm s3://$usernameIn/$fileKey
  rm ./passwordVerification/*
  echo "delete all the files in passwordVerification for security purpose..."
  fi
fi
