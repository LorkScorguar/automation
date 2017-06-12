"""
Module to manipulate RDS instances
"""


import secret
import os
import boto3

ACCESS_KEY_ID, SECRET_ACCESS_KEY = secret.getAccess()
REGION = secret.getRegion()
os.environ["HTTP_PROXY"] = secret.getProxy()
os.environ["HTTPS_PROXY"] = secret.getProxy()

RDSC = boto3.client(service_name='rds', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)

SUPPORTC = boto3.client(service_name='support', aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY, region_name="us-east-1")

def listRds(verbose):
    """List all RDS instances"""
    res = []
    drds = RDSC.describe_db_instances()
    for rds in drds['DBInstances']:
        if verbose:
            res.append(rds['DBInstanceIdentifier']+";"+rds['Engine']+";"+\
                       rds['DBInstanceStatus']+";"+rds['EngineVersion']+";"+\
                       rds['DBSubnetGroup']['DBSubnetGroupName'])
        else:
            res.append(rds['DBInstanceIdentifier']+";"+rds['Engine']+";"+\
                       rds['DBInstanceStatus'])
    return res

def getIdleRDS(verbose):
    """Get list of Idle RDS instances"""
    lrds = []
    jResp = SUPPORTC.describe_trusted_advisor_checks(language="en")
    for it in jResp['checks']:
        if it['category'] == 'cost_optimizing' and it['name'] == 'Amazon RDS Idle DB Instances':
            jResp2 = SUPPORTC.describe_trusted_advisor_check_result(checkId=str(it['id']),
                                                                    language="en")
            totalSavings = jResp2['result']['categorySpecificSummary']['costOptimizing']['estimatedMonthlySavings']
            for rds in jResp2['result']['flaggedResources']:
                if '14+' in rds['metadata']:
                    if verbose:
                        lrds.append(';'.join(rds['metadata']))
                    else:
                        lrds.append(rds['metadata'][1])
    resp = "You can save up to "+str(totalSavings)+"$"
    return totalSavings, lrds, resp

def deleteRDS(verbose,instanceId):
    """Delete a RDS instance"""
    RDSC.delete_db_instance(DBInstanceIdentifier=instanceId)
    if verbose:
        print("Instance with name: "+str(instanceId)+" deleted")

def cleanupRDS(verbose):
    """Delete all Idle RDS instances"""
    lrds = getIdleRDS(False)
    for rds in lrds:
        deleteRDS(verbose,rds)
