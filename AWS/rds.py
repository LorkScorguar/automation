"""
Module to manipulate RDS instances
"""

import boto3
import secret

ACCESS_KEY_ID, SECRET_ACCESS_KEY = secret.getAccess()
REGION = secret.getRegion()

RDSC = boto3.client(service_name='rds', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)

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
