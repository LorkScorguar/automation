"""
Module to manipulate RDS instances
"""
def listRds():
    """List all RDS instances"""
    res = []
    drds = RDSC.describe_db_instances()
    for rds in drds['DBInstances']:
        if VERBOSE:
            res.append(rds['DBInstanceIdentifier']+";"+rds['Engine']+";"+\
                       rds['DBInstanceStatus']+";"+rds['EngineVersion']+";"+\
                       rds['DBSubnetGroup']['DBSubnetGroupName'])
        else:
            res.append(rds['DBInstanceIdentifier']+";"+rds['Engine']+";"+\
                       rds['DBInstanceStatus'])
    return res
