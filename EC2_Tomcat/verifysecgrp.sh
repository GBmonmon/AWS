#!/bin/bash
if [ -z "$1" ]; then
    exit 1
fi



securitygrp="$1"
res=$(aws ec2 describe-security-groups --filters Name=ip-permission.from-port,Values=22 Name=ip-permission.from-port,Values=443 Name=ip-permission.from-port,Values=80 Name=ip-permission.from-port,Values=8080 --query "SecurityGroups[*].{Name:GroupName,ID:GroupId}" | python -c "import sys,json; print(json.load(sys.stdin)[0]['ID'])")
echo $res

