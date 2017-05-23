"""
Must do the following:
- EC2:Instances
+ count number of instances by types
+ count instances by user
+ list all ec2 instances with info

- EC2:Volumes
+ retrieve old unused volumes

- ELB
+ list all elb

- RDS
+ list all RDS db

- ALL
- Get Trusted Advisor infos

- OTHER
+ Generate list of AWS instance type with description
"""

import boto3
import os
import re
import urllib.request
import ssl
from collections import OrderedDict
import datetime
import argparse

import secret

os.environ["HTTP_PROXY"] = secret.getProxy()
os.environ["HTTPS_PROXY"] = secret.getProxy()

access_key_id, secret_access_key = secret.getAccess()
region = secret.getRegion()

ec2r=boto3.resource(service_name='ec2',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,region_name=region)
ec2c=boto3.client(service_name='ec2',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,region_name=region)

rdsc=boto3.client(service_name='rds',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,region_name=region)

elbc=boto3.client(service_name='elb',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,region_name=region)

supportc=boto3.client(service_name='support',aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,region_name="us-east-1")

#EC2 Volumes
def getOldUnusedVols():
    res = []
    ec2volumes = ec2c.describe_volumes(Filters=[
    {
        'Name': 'status',
        'Values': [
            'available',
        ],
    }]).get('Volumes',[])

    today = datetime.datetime.now(datetime.timezone.utc)
    days30 = today-datetime.timedelta(days=30)
    for vol in ec2volumes:
        if not 'Tags' in vol:
            if vol['CreateTime']<days30:
                res.append(vol['VolumeId'])
    return res

#EC2 Instances
def getUserInstances(user):
    nb = 0
    instances = ec2r.instances.filter(
    Filters = [{'Name':'tag:Owner', 'Values':[user]}])
    for instance in instances:
        nb += 1
        if verbose:
            server = str(instance.id)+";"+str(instance.instance_type)+";"+str(instance.state['Name'])+";"+str(instance.private_ip_address)+";"
            try:
                for tag in instance.tags:
                    if tag['Key']=='Description':
                        server+=tag['Value']+";"
                    if tag['Key']=='Owner':
                        server+=tag['Value']+";"
                    if tag['Key']=='ManagedBy':
                        server+=tag['Value']+";"
            except:
                continue
        else:
            server = str(instance.id)+";"+str(instance.instance_type)+";"+str(instance.state['Name'])
        print(server)
    print("Found "+str(nb)+" instances")

def listInstances():
    nb = 0
    for instance in ec2r.instances.all():
        if verbose:
            server = str(instance.id)+":"+str(instance.instance_type)+","+str(instance.state['Name'])+";"+str(instance.private_ip_address)+";"
            nb += 1
            try:
                for tag in instance.tags:
                    if tag['Key']=='Description':
                        server+=tag['Value']+":"
                    if tag['Key']=='Owner':
                        server+=tag['Value']+":"
                    if tag['Key']=='ManagedBy':
                        server+=tag['Value']+":"
            except:
                continue
        else:
            server = str(instance.id)+":"+str(instance.instance_type)+","+str(instance.state['Name'])
        print(server)
    print("Found "+str(nb)+" instances")

def countInstanceByType():
    instancesByType = {}
    for instance in ec2r.instances.all():
        try:
            instancesByType[instance.instance_type]+=1
        except:
            instancesByType[instance.instance_type]=1
    for k,v in instancesByType.items():
        print(k+":"+str(v))

#ELB
def listElb():
    res = []
    delb = elbc.describe_load_balancers()
    for elb in delb['LoadBalancerDescriptions']:
        if verbose:
            instances = ""
            for instance in elb['Instances']:
                instances += ","+instance['InstanceId']
            instances = instances[1:]
            res.append(elb['LoadBalancerName']+";"+','.join(elb['Subnets'])+";"+','.join(elb['AvailabilityZones'])+";"+instances)
        else:
            res.append(elb['LoadBalancerName']+";"+','.join(elb['Subnets']))
    return res

#ELB
def listRds():
    res = []
    drds = rdsc.describe_db_instances()
    for rds in drds['DBInstances']:
        if verbose:
            res.append(rds['DBInstanceIdentifier']+";"+rds['Engine']+";"+rds['DBInstanceStatus']+";"+rds['EngineVersion']+";"+rds['DBSubnetGroup']['DBSubnetGroupName'])
        else:
            res.append(rds['DBInstanceIdentifier']+";"+rds['Engine']+";"+rds['DBInstanceStatus'])
    return res

#ALL
def getAdvise():
    totalSavings = 0
    dreport = {}
    dcategory = {}
    jResp = supportc.describe_trusted_advisor_checks(language="en")
    for check in jResp["checks"]:
        jResp2 = supportc.describe_trusted_advisor_check_result(checkId=str(check['id']),language="en")
        if 'categorySpecificSummary' in jResp2['result'] and 'costOptimizing' in jResp2['result']['categorySpecificSummary']:
            ditem = {'id':check['id'],'name':check['name'],'savings':jResp2['result']['categorySpecificSummary']['costOptimizing']['estimatedMonthlySavings']}
            totalSavings +=jResp2['result']['categorySpecificSummary']['costOptimizing']['estimatedMonthlySavings']
        else:
            ditem = {'id':check['id'],'name':check['name']}
        try:
            dcategory[jResp2['result']['status']].append(ditem)
        except:
            dcategory[jResp2['result']['status']]=[ditem]
        dreport[check['category']]=dcategory
    if verbose:
        for k,v in dreport.items():
            for k1,v1 in v.items():
                for it in v1:
                    if 'savings' in it:
                        print(k+":"+k1+":"+it['name']+";"+str(it['savings']))
                    else:
                        print(k+":"+k1+":"+it['name'])
    else:
        for k,v in dreport.items():
            for k1,v1 in v.items():
                if k1 == 'error':
                    for it in v1:
                        if 'savings' in it:
                            print(k+":"+k1+":"+it['name']+";"+str(it['savings']))
                        else:
                            print(k+":"+k1+":"+it['name'])
    return "You can save up to "+str(totalSavings)+"$"

#OTHER
def ignoreCertificate():
    context = ssl.create_default_context()
    context.check_hostname=False
    context.verify_mode = ssl.CERT_NONE
    return context

def getInstanceTypes():
    dict={}
    #m3.medium -- 1 vCPU, 3.75 GiB RAM -- General purpose
    desc={"t":"General Purpose","m":"General Purpose","c":"Compute Optimized","x":"Memory Optimized","r":"Memory Optimized","p":"GPU Compute","g":"GPU Instances","f":"FPGA Instances","i":"Storage Optimized","d":"Storage Optimized"}
    url="https://aws.amazon.com/ec2/instance-types/"
    req=urllib.request.Request(url)
    req.get_method=lambda:'GET'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    data=resp.read().decode('utf-8')
    data=data.split("<h2 id=\"instance-type-matrix\">")[1]
    data=data.split("""</table>
         </div>
        </div>
        <div class="aws-text-box section">""")[0]
    array=data.split("<tr>")
    del array[0]
    del array[0]
    for item in array:
        #remove annoying characters
        item=item.replace("<br />","")
        item=item.replace("</p>","")
        try:
            n=item.split("</td>")[0]
            name=re.compile("<td.*>").split(n)[1].strip()
            arr=item.split("</td>")
            mem=re.compile("<td.*>").split(arr[2])[1].strip()
            cpu=re.compile("<td.*>").split(arr[1])[1].strip()
            description=desc[name[0]]
            dict[name.replace(".","_")]=str(name)+" -- "+str(cpu)+" vCPU, "+str(mem)+" GiB RAM -- "+description
        except:
            print(item)
    res=OrderedDict(sorted(dict.items(),key=lambda t: t[0]))
    return res

if __name__ == '__main__':
    global verbose
    verbose=False
    parser=argparse.ArgumentParser(description="Provide AWS informations using sdk and web site")
    parser.add_argument('-cbt','--count-by-type', action='store_true', default=False, help='Count ec2 instances for each flavor')
    parser.add_argument('-cbu','--count-by-user', action='store', dest='user', default=False, help='Count ec2 instances for specified user')
    parser.add_argument('-gf','--get-flavors', action='store_true', default=False, help='Get list of all available flavors')
    parser.add_argument('-le','--list-elb', action='store_true', default=False, help='List all ELB')
    parser.add_argument('-li','--list-ec2instances', action='store_true', default=False, help='List all ec2 instances')
    parser.add_argument('-lr','--list-rds', action='store_true', default=False, help='List all RDS instances')
    parser.add_argument('-ta','--trusted-advisor', action='store_true', default=False, help='Get advice from Trusted Advisor service')
    parser.add_argument('-ov','--old-volumes', action='store_true', default=False, help='Get a list of volumes that are older than 30 days and unused')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Output will be more verbose')
    dargs=parser.parse_args()
    try:
        if dargs.verbose:
            verbose=True
        if dargs.count_by_type:
            countInstanceByType()
        elif dargs.user:
            getUserInstances(dargs.user)
        elif dargs.get_flavors:
            res=getInstanceTypes()
            for k,v in res.items():
                print(k+":"+v)
        elif dargs.list_elb:
            res=listElb()
            print('\n'.join(res))
        elif dargs.list_ec2instances:
            listInstances()
        elif dargs.list_rds:
            res=listRds()
            print('\n'.join(res))
        elif dargs.trusted_advisor:
            res=getAdvise()
            print(res)
        elif dargs.old_volumes:
            res=getOldUnusedVols()
            print('\n'.join(res))
        else:
            parser.print_help()
    except:
        parser.print_help()
