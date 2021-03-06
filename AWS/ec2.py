"""
Module to manipulate ec2 resources

TODO
"""
import datetime
import re
import os
import json
import ssl
import urllib.request
import boto3
import secret

ACCESS_KEY_ID, SECRET_ACCESS_KEY = secret.getAccess()
REGION = secret.getRegion()

os.environ["HTTP_PROXY"] = secret.getProxy()
os.environ["HTTPS_PROXY"] = secret.getProxy()

EC2R = boto3.resource(service_name='ec2', aws_access_key_id=ACCESS_KEY_ID,
                      aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)
EC2C = boto3.client(service_name='ec2', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)
ELBC = boto3.client(service_name='elb', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)

SUPPORTC = boto3.client(service_name='support', aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY, region_name="us-east-1")

DRY = True

aws_region = {"ap-northeast-1": "Asia Pacific (Tokyo)",
              "ap-northeast-2": "Asia Pacific (Seoul)",
              "ap-south-1": "Asia Pacific (Mumbai)",
              "ap-southeast-1": "Asia Pacific (Singapore)",
              "ap-southeast-2": "Asia Pacific (Sydney)",
              "eu-west-1":"EU (Ireland)",
              "eu-west-2": "EU (Londres)",
              "eu-central-1": "EU (Frankfurt)",
              "govcloud-us": "AWS GovCloud (US)",
              "us-east-1": "US East (N. Virginia)",
              "us-east-2": "US East (Ohio)",
              "us-west-1": "US West (N. California)",
              "us-west-2": "US West (Oregon)",
              }
price_code = {"ondemand": "JRTCKXETXF",
              "reserved1yno": "4NA7Y494T4",
              "reserved1ypa": "HU7G6KETJZ",
              "reserved1yto": "6QCMYABX3D",
              "reserved3yno": "BPH4J8HBKS",
              "reserved3ypa": "38NPMPTW36",
              "reserved3yto": "NQ3QZPMQV9"}

def ignoreCertificate():
    """Simple function to ignore ssl certificate verification"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

#EC2 Volumes
def getVolDetails(verbose,region,volid):
    """Get details for a specific volume"""
    res = {}
    ec2volumes = EC2C.describe_volumes(VolumeIds=[volid])
    if verbose:
        res[vol['VolumeId']] = str(vol['CreateTime'])+";"+str(vol['Size'])+";"+str(vol['VolumeType'])
    else:
        res[vol['VolumeId']] = str(vol['CreateTime'])
    return res

def getVolumePrices(region):
    """Method to get volume prices"""
    url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
    req = urllib.request.Request(url)
    req.get_method = lambda: 'GET'
    resp = urllib.request.urlopen(req, context=ignoreCertificate())
    jResp = json.loads(resp.read().decode('utf-8'))
    dvolumes = {}
    for k, v in jResp['products'].items():
        if v['productFamily'] == 'Storage'\
           and v['attributes']['location'] == aws_region[region]:
           if k in jResp['terms']['OnDemand']:
               price = jResp['terms']['OnDemand'][k][k+"."+price_code['ondemand']]['priceDimensions'][k+"."+price_code['ondemand']+".6YS6EN2CT7"]['pricePerUnit']['USD']
               try:
                   vtype = v['attributes']['usagetype'].split(".")[1]
               except:
                   vtype="standard"
               dvolumes[vtype] = price
    return dvolumes

def getOldUnusedVols(verbose,region):
    """Get List of volumes that are available and 30 days old at least"""
    res = {}
    savings = 0
    dvolumes = getVolumePrices(region)
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
                    res[vol['VolumeId']] = str(vol['CreateTime'])+";"+str(vol['Size'])+";"+str(vol['VolumeType'])
                else:
                    res[vol['VolumeId']] = str(vol['CreateTime'])
                savings += float(vol['Size'] * float(dvolumes[vol['VolumeType']]))
    return savings, res

def cleanupOldUnusedVols(verbose):
    """Delete old unused volumes"""
    _, dvol = getOldUnusedVols(False)
    for k, v in dvol.items():
        resp = EC2C.delete_volume(
        DryRun = DRY,
        VolumeId = k
        )
        if verbose:
            print("Volume with id: "+k+" deleted")
    print("Delete "+str(len(lvol.keys()))+" volumes")

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
    lserver = {}
    dami = {}
    jResp = EC2C.describe_instances()
    for reserv in jResp['Reservations']:
        for instance in reserv['Instances']:
            try:
                ip = instance['PrivateIpAddress']
            except:
                ip = ""
            if 'Platform' in instance and instance['Platform'] == 'windows':
                platform = "windows"
            else:
                #keep track of already requested ami
                if instance['ImageId'] in dami:
                    ami = dami[instance['ImageId']]
                else:
                    ami = getAmi(False,instance['ImageId'])
                    for k, v in ami.items():
                        dami[k] = v
                platform = "linux"
                try:
                    lserver[instance['InstanceId']] = {'flavor': instance['InstanceType'],\
                                                      'status': instance['State']['Name'],\
                                                      'platform': platform,\
                                                      'private_ip': ip,\
                                                      'LaunchTime': instance['BlockDeviceMappings'][0]['Ebs']['AttachTime']}
                except:
                    lserver[instance['InstanceId']] = {'flavor': instance['InstanceType'],\
                                                      'status': instance['State']['Name'],\
                                                      'platform': platform,\
                                                      'private_ip': ip,\
                                                      'LaunchTime': instance['LaunchTime']}
                nb += 1
            if verbose:
                try:
                    for tag in instance['Tags']:
                        if tag['Key'] == 'Description':
                            lserver[instance['InstanceId']].update({'Description':tag['Value']})
                        if tag['Key'] == 'Owner':
                            lserver[instance['InstanceId']].update({'Owner':tag['Value']})
                        if tag['Key'] == 'ManagedBy':
                            lserver[instance['InstanceId']].update({'ManagedBy':tag['Value']})
                except:
                    continue
            else:
                nb += 1
                try:
                    lserver[instance['InstanceId']] = {'flavor': instance['InstanceType'],\
                                                      'status': instance['State']['Name'],\
                                                      'platform': platform,\
                                                      'private_ip': ip,\
                                                      'LaunchTime': instance['BlockDeviceMappings'][0]['Ebs']['AttachTime']}
                except:
                    lserver[instance['InstanceId']] = {'flavor': instance['InstanceType'],\
                                                      'status': instance['State']['Name'],\
                                                      'platform': platform,\
                                                      'private_ip': ip,\
                                                      'LaunchTime': instance['LaunchTime']}
    return lserver

def getUserInstances(verbose,user):
    """Count number of instances for specific user"""
    nb = 0
    res = ""
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
        res += str(server)+"\n"
    res += "Found "+str(nb)+" instances"
    return res

def countInstanceByType(verbose,dinstances):
    """Count instances by flavors"""
    instancesByType = {}
    for instanceId, details in dinstances.items():
        try:
            instancesByType[details['flavor']] += 1
        except:
            instancesByType[details['flavor']] = 1
    return instancesByType

def countInstanceByTypeByOS(verbose,dinstances):
    """Count instances by flavors and by OS"""
    instancesByType = {}
    for instanceId, details in dinstances.items():
        try:
            instancesByType[details['flavor']+";"+details['platform']] += 1
        except:
            instancesByType[details['flavor']+";"+details['platform']] = 1
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

def getInstanceTypes(region):
    """Method to get instance flavor with specs and price
    Note that price is for shared instance without included license"""
    url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
    req = urllib.request.Request(url)
    req.get_method = lambda: 'GET'
    resp = urllib.request.urlopen(req, context=ignoreCertificate())
    jResp = json.loads(resp.read().decode('utf-8'))
    dinstances = {}
    for k, v in jResp['products'].items():
        if v['productFamily'] == 'Compute Instance'\
           and v['attributes']['location'] == aws_region[region]\
           and v['attributes']['tenancy'] == 'Shared'\
           and (v['attributes']['licenseModel'] == 'Bring your own license'\
           or v['attributes']['licenseModel'] == 'No License required'):
            ondemand = 0
            reserved1yno = 0
            reserved1ypa = 0
            reserved1yto = 0
            ncpu = v['attributes']['vcpu']
            nram = v['attributes']['memory']
            flavor = v['attributes']['instanceType']
            family = v['attributes']['instanceFamily']
            if k in jResp['terms']['OnDemand']:
                ondemand = jResp['terms']['OnDemand'][k][k+"."+price_code['ondemand']]['priceDimensions'][k+"."+price_code['ondemand']+".6YS6EN2CT7"]['pricePerUnit']['USD']
            if k in jResp['terms']['Reserved']:
                reserved1yno = jResp['terms']['Reserved'][k][k+"."+price_code['reserved1yno']]['priceDimensions'][k+"."+price_code['reserved1yno']+".6YS6EN2CT7"]['pricePerUnit']['USD']
                reserved1ypa = jResp['terms']['Reserved'][k][k+"."+price_code['reserved1ypa']]['priceDimensions'][k+"."+price_code['reserved1ypa']+".6YS6EN2CT7"]['pricePerUnit']['USD']
                reserved1yto = jResp['terms']['Reserved'][k][k+"."+price_code['reserved1yto']]['priceDimensions'][k+"."+price_code['reserved1yto']+".6YS6EN2CT7"]['pricePerUnit']['USD']
            os = v['attributes']['operatingSystem'].lower()
            if flavor not in dinstances.keys():
                dinstances[flavor+";"+os] = {'cpu': ncpu,
                                      'ram': nram,
                                      'family': family,
                                      'ondemand': ondemand,
                                      'reserved1yno': reserved1yno,
                                      'reserved1ypa': reserved1ypa,
                                      'reserved1yto': reserved1yto}
    return dinstances

def optimizeReservation(verbose,region):
    """Try to optimize reservations
    + check if reservation are fully used/partially or not at all
    + check if reservation is needed for a flavor due to instances usage (based on 6months)
    - provide price drop estimate"""
    print("WARNING: As it's not possible to get OS through AWS API, All "\
          "Linux are reported as Linux (no RedHat, Suse, etc)\n"\
          "This issue will be address in a future update\n\n")
    shouldReserved = {}
    dreserved = getReservedInstances(False)
    dinstances = listInstances(False)
    dflavors = getInstanceTypes(region)
    count_by_type_os = countInstanceByTypeByOS(False, dinstances)
    resp = ""
    for typos, nb in count_by_type_os.items():
        if typos in dreserved:
            if int(count_by_type_os[typos]) - int(dreserved[typos]) >= 0:
                count_by_type_os[typos] = int(count_by_type_os[typos]) - int(dreserved[typos])
                resp += "Reservation fully used for "+typos+"\n"
            else:
                print("Reservation not fully used for "+typos+": "+dreserved[typos]+"reserved but only "+count_by_type_os[typos]+" instances")
    for typos, nb in dreserved.items():
        if typos not in count_by_type_os:
            resp += "Reservation is not used for "+typos+"\n"
    #Provide tips for better reservations
    #Begin by removing instances that have reservation
    for instanceId in list(dinstances):
        if dinstances[instanceId]['flavor'] in dreserved:
            if int(dreserved[dinstances[instanceId]['flavor']]) > 0:
                dreserved[dinstances[instanceId]['flavor']] -= 1
                del dinstances[instanceId]
    today = datetime.datetime.now(datetime.timezone.utc)
    months6 = today-datetime.timedelta(days=180)
    for k, v in dinstances.items():
        if v['LaunchTime'] < months6:
            try:
                shouldReserved[v['flavor']+";"+v['platform']] += 1
            except:
                shouldReserved[v['flavor']+";"+v['platform']] = 1
    resp += "\nBased on instances older than 6 months, you should buy following reservations:\n"
    saveno, savepa = 0, 0
    for k, v in shouldReserved.items():
        resp += k+":"+str(v)+"\n"
        saveno += (float(dflavors[k]['ondemand']) - float(dflavors[k]['reserved1yno'])) * v
        savepa += (float(dflavors[k]['ondemand']) - float(dflavors[k]['reserved1ypa'])) * v
    resp += "You can save up to "+str(saveno)+"$/hour with no upfront reservation\n"
    resp += "You can save up to "+str(savepa)+"$/hour with partial upfront reservation\n"
    if verbose:
        resp += "\nInstances below doesn't have reservation:\n"
        for k, v in count_by_type_os.items():
            resp += k+":"+str(v)+"\n"
    return saveno, resp

def upgradableFlavor(verbose,region):
    dinstances = listInstances(False)
    cbt = countInstanceByTypeByOS(False,dinstances)
    dflavors = getInstanceTypes(region)
    save = 0
    dMaxGenFlavors = {}
    shouldUpgrade = []
    instanceUpgrade = {}
    resp = ""
    #get max gen for each flavor
    for k, v in dflavors.items():
        if k[1].isdigit():
            if k[0] not in dMaxGenFlavors.keys():
                dMaxGenFlavors[k[0]] = k[1]
            else:
                if k[1] > dMaxGenFlavors[k[0]]:
                    del dMaxGenFlavors[k[0]]
                    dMaxGenFlavors[k[0]] = k[1]
        else:
            if k[:2] not in dMaxGenFlavors.keys():
                dMaxGenFlavors[k[:2]] = k[2]
            else:
                if k[1] > dMaxGenFlavors[k[:2]]:
                    del dMaxGenFlavors[k[:2]]
                    dMaxGenFlavors[k[:2]] = k[2]
    for k, v in cbt.items():#ajouter gestion des instances commencant par 2 lettres
        if k[1] < dMaxGenFlavors[k[0]]:
            try:
                newFlavor = k.replace(k[1],dMaxGenFlavors[k[0]])
                save += (float(dflavors[k]['ondemand']) - float(dflavors[newFlavor]['ondemand'])) * v
                if k not in shouldUpgrade:
                    shouldUpgrade.append(k.split(";")[0])
                if verbose:
                    resp += k+" can be upgraded to "+newFlavor+"\n"
            except:
                resp += k+" cant be upgraded\n"
    resp += "By upgrading old flavor to new one you can save up to: "+str(save)+"$/hour\n"
    for k, v in dinstances.items():
        if v['flavor'] in shouldUpgrade:
            instanceUpgrade[k] = { "from": v['flavor'],
                                   "to": v['flavor'].replace(v['flavor'][1],dMaxGenFlavors[v['flavor'][0]])
                                 }
    return save, instanceUpgrade, resp

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
                    linstances = getElbInstance(False,elb['metadata'][1])
                    if len(linstances) == 0:#if no instances
                        lIdleElb.append(elb['metadata'][1])
                        totalSavings += float(elb['metadata'][3][1:])
                    for instance in linstances:#search if instance still exist
                        haveInstance = True
                        try:
                            dinstance = getInstance(False,instance['InstanceId'])
                            haveInstance = True
                        except Exception as e:
                            if re.search('InvalidInstanceID.NotFound', str(e)):
                                haveInstance = False
                        if not haveInstance:
                            lIdleElb.append(elb['metadata'][1])
                            totalSavings += float(elb['metadata'][3][1:])
    resp = "You can save up to "+str(totalSavings)+"$"
    return totalSavings, lIdleElb, resp

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
