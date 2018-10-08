#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 11:29:08 2018

@author: kathynorman, revisions Jeff Miller
"""
import os, sys, time, timeit, inspect, subprocess

# path required for boto3
#sys.path.append('/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages')


import boto3
import botocore

import subprocess

import paramiko
import urllib.request
import urllib.error

def getsecuritygrpID(client):
    secgrpname = 'aws_gbmonmon1'
    try:
        secgrpfilter = [
            {
                'Name': 'group-name', 'Values':[secgrpname]
            }
        ]
        secgroups = client.describe_security_groups(Filters = secgrpfilter )
        #print(secgroups)
        secgrptouse = secgroups['SecurityGroups'][0]
        secgrpid = secgrptouse['GroupId']
        return secgrpid

    except:
        resp = client.describe_subnets()
        vpcid = resp['Subnets'][0]['VpcId']
        subnetlist = client.describe_subnets(Filters = [{'Name':'vpc-id','Values':[vpcid] }])
        subnetid = subnetlist['Subnets'][0]['SubnetId']

        print('No security group, will create security group' + secgrpname)
        secgrptouse = client.create_security_group(GroupName = secgrpname,
                                                   Description = 'aws class open ssh, http, https',
                                                   VpcId = vpcid)
        secgrpid = secgrptouse['GroupId']
        print('Create security group > ', secgrpid)
        portlist = [22,80,443,8080]
        for port in portlist:
            try:
                client.authorize_security_group_ingress(
                    CidrIp='0.0.0.0/0',
                    FromPort=port,
                    GroupId=secgrpid,
                    IpProtocol='tcp',
                    ToPort=port
                )
            except:
                print('error opening port: '+ port)
                exit()
        return secgrpid


def waitForStatus(status, client, instance, delay, max_attempts):
 
#   waitForStatus can have 3 conditions:
#   1.) the status is invalid. This is an unrecoverable error, and the program terminates
#   2.) the wait fails because the status has not change to the expected status
#   3.) the wait succeeds, and the instance is now the specific status

    try:
           waiter = client.get_waiter(status)

    except ValueError as e:
           print(inspect.stack()[0][3] + " wait status error:" + str(e))  
           print("terminating program")
           sys.exit()
           
    
    print("Default waiter delay in seconds: " + str(waiter.config.delay) )
    print("Default waiter max attempts: " + str(waiter.config.max_attempts)) 
    print("Default maximum waiter wait time in minutes: "+ str((waiter.config.delay+waiter.config.max_attempts)/60))
    waiter.config.delay = delay
    waiter.config.max_attempts = max_attempts
    print( "Reset waiter delay in seconds: " + str(waiter.config.delay) )
    print( "Reset waiter max attempts: " + str(waiter.config.max_attempts) ) 
    print("Each wait is <= " + str(delay*max_attempts) + " seconds" )        
    
    maxLoops = 12
    start_time = timeit.default_timer()   
    print("loop <= " + str(maxLoops) + " times, each time issuing a wait for " + status + ", with a maximum wait time of " + str(delay * max_attempts) + " seconds")
    instid = instance['InstanceId']
    for loop in range (1,maxLoops): 
        print ("loop # " + str(loop) + " for instance " + instid + "," + status)

        try:   
                waiter.wait(InstanceIds=[instid])
                print("wait success for: "+ str(instid))
                break

        except botocore.exceptions.WaiterError as e:
                print("wait error " + str( e ))
                waiter = client.get_waiter(status)  # must reset the waiter for each wait
                waiter.config.delay = delay
                waiter.config.max_attempts = max_attempts
                pass   

    elapsed = timeit.default_timer() - start_time
    print("time for wait: " + str(elapsed/60)+ " minutes")
        
    return
    

def startinstance(ami_instance, securitygroupid, securitykey, keylocation, count, delete):

    print('Python version:' + ".".join(map(str, sys.version_info[:3])))
    print('Boto3 version:' + boto3.__version__)
    print('Paramiko version:' +  paramiko.__version__)
   
    """ 
    executing with the following parameters set in main
    ami_instance = 'ami-824c4ee2'
    securitygroup = '...'
    securitykey = '...'
    keylocation = '...'
    count = number of instances
    """
    instance_type = 't2.micro'
    os.chdir(keylocation)  # require path for pem file
    if securitykey == 'key-us-west-1': region = 'us-west-1'
    if securitykey == 'key-us-east-1': region = 'us-east-1'
    #bol = True
    #countwhile = 0
    #while bol:
    #    if countwhile >30: print('Try too many time...')
    #    print('available region: [us-west-1, us-east-1]')
    #    region = input('Type in the region for this instance: ')
    #    region = region.lower()
    #    if region == 'us-west-1' or region == 'us-east-1':
    #        bol = False
    #        break
    #    elif count > 30: print('Try too many times...')
    #    else:
    #        print('Type in us-west-1 or us-east-1: ')
    #        countwhile+=1
    #        continue
    with open("/Users/Jerry/.aws/config","w") as fh:
        output = 'json'
        st = """[default]\nregion = {0}\noutput = {1}
        """.format(region, output)
        fh.write(st)


    #  boto3 setup
    #ec2 = boto3.resource('ec2', region_name=region)
    # client is used to wait for instance status
    client = boto3.client('ec2',region_name=region)
#   get subnet, will just use the first subnet within the first vpc
 
#   NOTE: we should verify the vpc actually has a subnet. For example
#   in class your instructor created a VPC, but did not associated a subnet with it
#   this happened to be the first vpc that came back. SInce there was not subnet
#   we did not have a valid subnetid, so the instance did not run

    resp = client.describe_vpcs()
    vpcidtouse = resp['Vpcs'][0]['VpcId']
    subnetlist = client.describe_subnets(Filters=[{'Name':'vpc-id', 'Values':[vpcidtouse]}])
    subnetid = subnetlist['Subnets'][0]['SubnetId']
    secgrpid = getsecuritygrpID(client = client)
    secgrpidlist = [secgrpid]  
    if region == 'us-east-1': 
        ami_instance = 'ami-0ff8a91507f77f867'
        if securitykey != 'key-us-east-1':
            print('You need to have a key-pair file for us-east-1...')
            exit()
    if region == 'us-west-1' and securitykey != 'key-us-west-1':
        print('You need to have a key-pair file for us-west-1...')
        exit()
    resp = client.run_instances(ImageId=ami_instance,
                                    InstanceType=instance_type,
                                    KeyName=securitykey,
                                    SecurityGroupIds = secgrpidlist,
                                    SubnetId=subnetid,
                                    MinCount=1,
                                    MaxCount=count)
        
    instList = resp["Instances"]
    instanceCount = len(instList)
    instanceIds = [ ]
    dnsNames = [ ]
    ipAddrs = [ ]
    noValue = '  '
    # start of loop to process created instances   
    loopCnt = 0;    
    for instance in instList:
        instid = instance['InstanceId']
        instanceIds.append(instid)  #save the instance Ids for deletion
        dnsNames.append(noValue)
        ipAddrs.append(noValue)

        print("---------------------------- #"+ str(loopCnt) + " ----------------------------")
        print ("Invoking wait for instance " + instid)

        waitForStatus('instance_running', client, instance, 25, 2)
   
        print('The following instance has been started: ' + instid + ' waiting for public DNS name')
        haveDNS = False
        maxDNSTries = 16
        sleepTime = 2
        while haveDNS == False and maxDNSTries > 0:
            time.sleep(sleepTime)
            rz=client.describe_instance_status(InstanceIds=[instid])
    
            if not bool(rz):
                continue
            if len(rz["InstanceStatuses"]) == 0:
                continue

            inststate = rz["InstanceStatuses"][0]["InstanceState"]
            state=inststate["Name"]
            if state != 'running':
                continue
            
            rz1 = client.describe_instances(InstanceIds=[instid])
            if len(rz1["Reservations"]) == 0:
                continue

            instanceInfo = rz1["Reservations"][0]["Instances"][0]
            dns_name = instanceInfo['PublicDnsName']
            ip_address = instanceInfo['PublicIpAddress']
            maxDNSTries -= 1
            if dns_name and ip_address:
                break
           
        if not dns_name:
            print('cannot get DNS Name for instance:' + instid)
            return

        dnsNames.append(dns_name)
        ipAddrs.append(ip_address)
        print(instid + ' paramiko ssh connect to ' + dns_name + ' ip:' + ip_address)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

       
        tries = 1
        maxtries = 5
        sshloop = True
        while(sshloop):    # note this loop is not necessary, as the instance network is plumbed
            try:          # however I keep it in, as  this is the first time we are reaching out to the instance
                            # this code will reveal any network issues unrelated to the aws instance
                #ssh.connect(dns_name,username='ec2-user', key_filename=securitykey+'.pem')
                ssh.connect(ip_address,username='ec2-user', key_filename=securitykey+'.pem')
                sshloop = False
                print(str(ip_address) +  ' ssh connection successful')
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                print(instid + "tries: " + str(tries) + " " + str(e.errors) +  ' ssh attempted')
                time.sleep(10)
                tries += 1
                if tries == maxtries:
                    raise
   
 
        # do tomcat6 install and start server
        #      this is a AWS Linux server, install pending updates
        print('updating yum on ' + str(ip_address))
        stdin, stdout, stderr = ssh.exec_command("sudo yum -y update")
        stdin.flush()
       
        print('installing tomcat on ' + str(ip_address))
        stdin, stdout, stderr = ssh.exec_command("sudo yum -y install tomcat8 tomcat8-webapps")
        stdin.flush()
        data = stdout.read().splitlines()
        if data[-1].decode() == 'Complete!':
            print(ip_address + ' tomcat install successful on ' + str(ip_address))
        else:
            print(str(ip_address) + ' tomcat did NOT install')
            return

   
        print('starting tomcat on ' + str(ip_address))
        stdin, stdout, stderr = ssh.exec_command("sudo service tomcat8 start")
        stdin.flush()
        data = stdout.read().splitlines()
        #data is binary so convert to a string
        if 'OK' in data[-1].decode():
            print('tomcat start successful on ' + str(ip_address))
        else:
            print('could NOT start tomcat on ' + str(ip_address))
            return
   
        print('getting tomcat status from ' + str(ip_address))
        stdin, stdout, stderr = ssh.exec_command("sudo service tomcat8 status")
        stdin.flush()
        data = stdout.read().splitlines()
        if 'running' in data[-1].decode():
            print('confirmed tomcat service is running on' + str(ip_address))
        else:
            print('could not determine if tomcat is running on ' + str(ip_address))

        print("testing Tomcat, connecting to http://" + str(ip_address) + ":8080")
        tries = 1
        maxtries = 5
        urlloop = True
        while(urlloop):
            try:       
                urloutput = urllib.request.urlopen("http://"+ip_address+":8080").read()
                urlloop = False
            except:
                print(str(instid) + " " + str(tries)  + ' urlopen attempted')
                time.sleep(10)
                tries += 1
                if tries == maxtries:
                    print('ERROR: hit maxtries:' + str(maxtries) + ' urlopen ' + "http://" +ip_address + ":8080")
                    raise
                     
                 
        print("Successful connection to http://" + str(ip_address) +":8080")
        if 'Congratulations!' in urloutput.decode():
            print( str(ip_address) +  " successful connection to Tomcat")
        else:
            print("Connection to Tomcat failed, for instance " + str(ip_address)) 
        
        
        # end of loop for processing created instances
        print('closing ssh connection to ', str(ip_address))
        ssh.close
    
    delete = True
    time.sleep(60)
    print('Stop program for the screen shot...')
    if delete : 
            response=client.terminate_instances(InstanceIds=instanceIds) #JSON is returned
            print('The following instances have been queued for termination: ', instanceIds)
    return     

def usage():
    print('usage: python st34.py securityGroup sshKeyName sshKeyFolder')


def verifyparameters(keylocation,securitykey,securitygroup):
    print('verifying parameters')
    if os.path.isdir(keylocation) == False:
        print('cannot find key location folder:' + keylocation)
        return False, None

    fullpath = os.path.join(keylocation, securitykey)
    if os.path.exists(fullpath) == False:
        print('cannot find keyfile:' + fullpath)
        print('current folder is:' + os.getcwd())
        return False, None

    try:
        rg = subprocess.check_output(['./verifysecgrp.sh', securitygroup])
        rg = rg.rstrip()
        securitygroupid = rg
    except:
        print('error verifying security group ' + securitygroup)
        return False, None


    return True, securitygroupid.decode('UTF-8')





if  __name__ =='__main__':
    if len(sys.argv) != 4:
        usage()
        exit(1)
      
    count = 1
    #'ami-824c4ee2'
    ami_instance = 'ami-824c4ee2'
    securitygroup = sys.argv[1]
    securitykey = sys.argv[2]
    keylocation = sys.argv[3]
    print(securitygroup, securitykey, keylocation)
    rtn, securitygroupid = verifyparameters(keylocation, securitykey,securitygroup)
    if rtn  == False:
        exit(1)

    delete = False
    #print(securitykey[:-4],'----------') get rid of suffix
    startinstance(ami_instance, securitygroupid, securitykey[:-4], keylocation, count, delete)
    exit(0)
    
#----------------------------
main()

       
   
