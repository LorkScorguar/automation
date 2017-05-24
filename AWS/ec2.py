"""
Module to manipulate ec2 resources
"""
#EC2 Volumes
def getOldUnusedVols():
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
                res.append(vol['VolumeId'])
    return res

#EC2 Instances
def getUserInstances(user):
    """Count number of instances for specific user"""
    nb = 0
    instances = EC2R.instances.filter(Filters=[{'Name':'tag:Owner', 'Values':[user]}])
    for instance in instances:
        nb += 1
        if VERBOSE:
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

def listInstances():
    """list all ec2 instances"""
    nb = 0
    for instance in EC2R.instances.all():
        if VERBOSE:
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
            server = str(instance.id)+":"+str(instance.instance_type)+","+\
                     str(instance.state['Name'])
        print(server)
    print("Found "+str(nb)+" instances")

def countInstanceByType():
    """Count instances by flavors"""
    instancesByType = {}
    for instance in EC2R.instances.all():
        try:
            instancesByType[instance.instance_type] += 1
        except:
            instancesByType[instance.instance_type] = 1
    for k, v in instancesByType.items():
        print(k+":"+str(v))

#ELB
def listElb():
    """List all ELB"""
    res = []
    delb = ELBC.describe_load_balancers()
    for elb in delb['LoadBalancerDescriptions']:
        if VERBOSE:
            instances = ""
            for instance in elb['Instances']:
                instances += ","+instance['InstanceId']
            instances = instances[1:]
            res.append(elb['LoadBalancerName']+";"+','.join(elb['Subnets'])+\
                       ";"+','.join(elb['AvailabilityZones'])+";"+instances)
        else:
            res.append(elb['LoadBalancerName']+";"+','.join(elb['Subnets']))
    return res
