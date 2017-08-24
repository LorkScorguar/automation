"""
Module to interact with IAM

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


IAMC = boto3.client(service_name='iam', aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=SECRET_ACCESS_KEY, region_name=REGION)


DRY = True

def getUsers(verbose,region):
    """Get List of users"""
    res = []
    jResp=IAMC.list_users()
    for user in jResp['Users']:
        res.append(user['UserName'])
    return res

def checkKeyForUser(verbose,region,user):
    """Get list of access_key for a user"""
    res = {}
    jResp=IAMC.list_access_keys(
        UserName=user
    )
    for ac in jResp['AccessKeyMetadata']:
        if user in res:
            res[user].append({"accessKeyId":ac['AccessKeyId'],"createdDate":ac['CreateDate']})
        else:
            res[user]=[{"accessKeyId":ac['AccessKeyId'],"createdDate":ac['CreateDate']}]
    return res

def checkKeys(verbose,region,user=""):
    """Get List of access_key older than 90days"""
    res = {}
    lusers=getUsers(verbose,region)
    for user in lusers:
        res[user]=checkKeyForUser(verbose,region,user)[user]
        break
    today = datetime.datetime.now(datetime.timezone.utc)
    days90 = today-datetime.timedelta(days=90)
    for k,v in res.items():
        for ac in v:
            if ac['createdDate']<days90:
                age=(today-ac['createdDate']).days
                print("Access key "+ac['accessKeyId']+" for user "+k+" is old ("+str(age)+" days)")

checkKeys(False,REGION)
