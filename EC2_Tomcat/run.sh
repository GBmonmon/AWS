#!/bin/bash
bol=true
while [ $bol == true ]; do
  echo "Available region: [us-west-1, us-east-1]"
  read -p "Which region to use for launching this instance: " region
  if [ "$region" == "us-west-1" ]; then
    python st34.py "aws_gbmonmon1" "key-us-west-1.pem" .
    bol=false
  elif [ "$region" == "us-east-1" ]; then
    python st34.py "aws_gbmonmon1" "key-us-east-1.pem" .
    bol=false
  else
    continue
  fi
done
