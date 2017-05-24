"""
Module to manipulate ec2 resources
"""
import datetime
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
def getInstance(verbose,instanceId):
    """Simple function to get informations for an instance"""
    dinstance = EC2C.describe_instances(InstanceIds=[instanceId])
    return dinstance

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

def listInstances(verbose):
    """list all ec2 instances"""
    nb = 0
    for instance in EC2R.instances.all():
        if verbose:
            server = str(instance.id)+":"+str(instance.instance_type)+","+\
                     str(instance.state['Name'])+";"+str(instance.private_ip_address)+";"
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
            server = str(instance.id)+":"+str(instance.instance_type)+","+\
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
    for k, v in instancesByType.items():
        print(k+":"+str(v))

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
