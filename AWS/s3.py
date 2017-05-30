"""
Module to manipulate ec2 resources
"""
import datetime
import re
import os
import boto3
import secret

ACCESS_KEY_ID, SECRET_ACCESS_KEY = secret.getAccess()
REGION = secret.getRegion()

os.environ["HTTP_PROXY"] = secret.getProxy()
os.environ["HTTPS_PROXY"] = secret.getProxy()

S3C = boto3.client(service_name='s3', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)


DRY = True

def listObjects(verbose, bucket):
    jResp = S3C.list_objects(Bucket=bucket)
    res = {}
    for item in jResp['Contents']:
        if verbose:
            res[item['Key']]+";"+str(item['Size'])+";"+str(item['LastModified'])
        else:
            res[item['Key']]+";"+str(item['Size'])
    return res

def downloadFile(bucket,fileKey):
    fileName = open(fileKey, 'wb')
    S3C.download_fileobj(bucket,fileKey,fileName)
