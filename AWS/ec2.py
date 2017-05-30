"""
Module to manipulate ec2 resources
"""
import datetime
import re
import boto3
import secret

ACCESS_KEY_ID, SECRET_ACCESS_KEY = secret.getAccess()
REGION = secret.getRegion()

EC2R = boto3.resource(service_name='ec2', aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)
EC2C = boto3.client(service_name='ec2', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)
ELBC = boto3.client(service_name='elb', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)

SUPPORTC = boto3.client(service_name='support', aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY, region_name="us-east-1")

DRY = True

#EC2 Volumes
def getOldUnusedVols(verbose):
    """Get List of volumes that are available and 30 days old at least"""
    res = []
    ec2volumes = EC2C.describe_volumes(Filters=[
        {
            'Name': 'status',
            'Values': [
                'available',
            ],
        }]).get('Volumes', [])

    today = datetime.datetime.now(datetime.timezone.utc)
    days30 = today-datetime.timedelta(days=30)
    for vol in ec2volumes:
        if not 'Tags' in vol:
            if vol['CreateTime'] < days30:
                if verbose:
                    res.append(vol['VolumeId']+";"+str(vol['CreateTime']))
                else:
                    res.append(vol['VolumeId'])
    return res

def cleanupOldUnusedVols(verbose):
    """Delete old unused volumes"""
    lvol = getOldUnusedVols(False)
    for vol in lvol:
        resp = EC2C.delete_volume(
        DryRun = DRY,
        VolumeId = vol
        )
        if verbose:
            print("Volume with id: "+vol+" deleted")
    print("Delete "+str(len(lvol))+" volumes")

#EC2 Instances
def getAmi(verbose,amiId):
    """Simple function to get ami details"""
    dami = {}
    jResp = EC2C.describe_images(ImageIds=[amiId])
    if len(jResp['Images']) > 0:
        if 'Platform' in jResp['Images'][0]:
            platform = jResp['Images'][0]['Platform']
        else:
            platform = ""
        if verbose:
            dami[amiId] = jResp['Images'][0]['Name']+";"+\
                          platform+";"+\
                          jResp['Images'][0]['Architecture']+";"+\
                          jResp['Images'][0]['ImageType']+";"+\
                          jResp['Images'][0]['VirtualizationType']
        else:
            dami[amiId] = jResp['Images'][0]['Name']+";"+\
                          platform
    else:
        dami[amiId] = "Unknown;Unknown"
    return dami

def getInstance(verbose,instanceId):
    """Simple function to get informations for an instance"""
    dinstance = EC2C.describe_instances(InstanceIds=[instanceId])
    return dinstance

def listInstances(verbose):
    """list all ec2 instances"""
    nb = 0
    lserver = []
    for instance in EC2R.instances.all():
        if verbose:
            lserver.append(str(instance.id)+":"+\
                           str(instance.instance_type)+","+\
                           str(instance.state['Name'])+";"+\
                           str(instance.private_ip_address)+";")
            nb += 1
            try:
                for tag in instance.tags:
                    if tag['Key'] == 'Description':
                        server += tag['Value']+":"
                    if tag['Key'] == 'Owner':
                        server += tag['Value']+":"
                    if tag['Key'] == 'ManagedBy':
                        server += tag['Value']+":"
            except:
                continue
        else:
            nb += 1
            lserver.append(str(instance.id)+":"+\
                           str(instance.instance_type)+","+\
                           str(instance.state['Name']))
    return lserver

def getUserInstances(verbose,user):
    """Count number of instances for specific user"""
    nb = 0
    instances = EC2R.instances.filter(Filters=[{'Name':'tag:Owner', 'Values':[user]}])
    for instance in instances:
        nb += 1
        if verbose:
            server = str(instance.id)+";"+str(instance.instance_type)+";"+\
                     str(instance.state['Name'])+";"+str(instance.private_ip_address)+";"
            try:
                for tag in instance.tags:
                    if tag['Key'] == 'Description':
                        server += tag['Value']+";"
                    if tag['Key'] == 'Owner':
                        server += tag['Value']+";"
                    if tag['Key'] == 'ManagedBy':
                        server += tag['Value']+";"
            except:
                continue
        else:
            server = str(instance.id)+";"+str(instance.instance_type)+";"+\
                     str(instance.state['Name'])
        print(server)
    print("Found "+str(nb)+" instances")

def countInstanceByType(verbose):
    """Count instances by flavors"""
    instancesByType = {}
    for instance in EC2R.instances.all():
        try:
            instancesByType[instance.instance_type] += 1
        except:
            instancesByType[instance.instance_type] = 1
    return instancesByType

def countInstanceByTypeByOS(verbose):
    """Count instances by flavors and by OS"""
    instancesByType = {}
    dami = {}
    jResp = EC2C.describe_instances()
    for reserv in jResp['Reservations']:
        for instance in reserv['Instances']:
            if 'Platform' in instance and instance['Platform'] == 'windows':
                try:
                    instancesByType[instance['InstanceType']+";"+instance['Platform']] += 1
                except:
                    instancesByType[instance['InstanceType']+";"+instance['Platform']] = 1
            else:
                #keep track of already requested ami
                if instance['ImageId'] in dami:
                    ami = dami[instance['ImageId']]
                else:
                    ami = getAmi(False,instance['ImageId'])
                    for k, v in ami.items():
                        dami[k] = v
                try:
                    instancesByType[instance['InstanceType']+";linux"] += 1
                except:
                    instancesByType[instance['InstanceType']+";linux"] = 1
    return instancesByType

def startInstance(instanceID):
    """Simple method to start an instance"""
    response = client.start_instances(
    DryRun=DRY,
    InstanceIds=[
        instanceID,
    ],
    )

def stopInstance(instanceID):
    """Simple method to stop an instance"""
    response = client.stop_instances(
    DryRun=DRY,
    InstanceIds=[
        instanceID,
    ],
    Force=True
    )

def getReservedInstances(verbose):
    """Function to get reserved instances"""
    lres = {}
    jResp = EC2C.describe_reserved_instances()
    for reserved in jResp['ReservedInstances']:
        if reserved['State'] == 'active':
            if verbose:
                lres[reserved['InstanceType']] = str(reserved['Start'])+";"+\
                                                 str(reserved['End'])+";"+\
                                                 str(reserved['InstanceCount'])+";"+\
                                                 reserved['ProductDescription']+";"+\
                                                 str(reserved['UsagePrice'])
            else:
                if re.search("win", reserved['ProductDescription'], re.IGNORECASE):
                    os = "windows"
                elif re.search("red hat", reserved['ProductDescription'], re.IGNORECASE):
                    os = "redhat"
                elif re.search("suse", reserved['ProductDescription'], re.IGNORECASE):
                    os = "suse"
                else:
                    os = "linux"
                lres[reserved['InstanceType']+";"+os] = str(reserved['InstanceCount'])
    return lres

def optimizeReservation():
    """Try to optimize reservations
    + check if reservation are fully used/partially or not at all
    - check if reservation is needed for a flavor due to instances usage
    - provide price drop estimate"""
    dreserved = getReservedInstances(False)
    count_by_type_os = countInstanceByTypeByOS(False)
    for typos, nb in count_by_type_os.items():
        if typos in dreserved:
            if int(count_by_type_os[typos]) - int(dreserved[typos]) >= 0:
                count_by_type_os[typos] = int(count_by_type_os[typos]) - int(dreserved[typos])
                print("Reservation fully used for "+typos)
            else:
                print("Reservation not fully used for "+typos+": "+dreserved[typos]+"reserved but only "+count_by_type_os[typos]+" instances")
    for typos, nb in dreserved.items():
        if typos not in count_by_type_os:
            print("Reservation is not used for "+typos)
    print("\nInstances below doesn't have reservation:")
    for k, v in count_by_type_os.items():
        print(k+":"+str(v))

#ELB
def listElb(verbose):
    """List all ELB"""
    res = []
    delb = ELBC.describe_load_balancers()
    for elb in delb['LoadBalancerDescriptions']:
        if verbose:
            instances = ""
            for instance in elb['Instances']:
                instances += ","+instance['InstanceId']
            instances = instances[1:]
            res.append(elb['LoadBalancerName']+";"+','.join(elb['Subnets'])+\
                       ";"+','.join(elb['AvailabilityZones'])+";"+instances)
        else:
            res.append(elb['LoadBalancerName']+";"+','.join(elb['Subnets']))
    return res

def getElbInstance(verbose,elbName):
    """Return list of instances behind an elb"""
    linstances = []
    delb = ELBC.describe_load_balancers(
        LoadBalancerNames = [elbName]
    )
    linstances = delb['LoadBalancerDescriptions'][0]['Instances']
    return linstances

def getIdleELB(verbose):
    """Get list of Idle ELB"""
    lIdleElb = []
    totalSavings = 0
    jResp = SUPPORTC.describe_trusted_advisor_checks(language="en")
    for it in jResp['checks']:
        if it['category'] == 'cost_optimizing' and it['name'] == 'Idle Load Balancers':
            jResp2 = SUPPORTC.describe_trusted_advisor_check_result(checkId=str(it['id']),
                                                                    language="en")
            for elb in jResp2['result']['flaggedResources']:
                if 'No active back-end instances' in elb['metadata']:
                    linstances = ec2.getElbInstance(False,elb['metadata'][1])
                    if len(linstances) == 0:#if no instances
                        lIdleElb.append(elb['metadata'][1])
                        totalSavings += float(elb['metadata'][3][1:])
                    for instance in linstances:#search if instance still exist
                        haveInstance = True
                        try:
                            dinstance = ec2.getInstance(False,instance['InstanceId'])
                            haveInstance = True
                        except Exception as e:
                            if re.search('InvalidInstanceID.NotFound', str(e)):
                                haveInstance = False
                        if not haveInstance:
                            lIdleElb.append(elb['metadata'][1])
                            totalSavings += float(elb['metadata'][3][1:])
    print("You can save up to "+str(totalSavings)+"$")
    return lIdleElb

def deleteELB(verbose,elbName):
    """Delete a RDS instance"""
    ELBC.delete_load_balancer(LoadBalancerName=elbName)
    if verbose:
        print("ELB with name: "+str(elbName)+" deleted")

def cleanupELB(verbose):
    """Delete all Idle ELB"""
    lelb = getIdleELB(False)
    for elb in lelb:
        deleteELB(verbose,elb)
