#This script is used to create database from ManageIQ API
dbRun="../database/allRun.csv"
dbUser="../database/allUsers.csv"

import base64
import json
import ssl
import urllib.request

import secret

user,password=secret.getCLDev()
authValue="Basic "+base64.b64encode(bytes(user+":"+password,'utf-8')).decode('utf-8')
miqurl=secret.getCLURLDEV()

def ignoreCertificate():
    context = ssl.create_default_context()
    context.check_hostname=False
    context.verify_mode = ssl.CERT_NONE
    return context

def getUsers(authValue,miqurl):
    total=1
    nb=0
    vmid=0
    file=open(dbUser,"w")
    while nb < total:
        req=urllib.request.Request(miqurl+"/users?expand=resources&attributes=id,name,userid,current_group&limit=100&offset="+str(nb))
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        req.get_method=lambda:'GET'
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        total=jResp['count']
        for item in jResp['resources']:
            #user,group
            file.write(item['userid']+","+str(item['current_group']['description'])+"\n")
        nb=nb+jResp['subcount']
    file.close()
    return 'ok'

def getRun():
    total=1
    nb=0
    file=open(dbRun,"w")
    while nb < total:
        req=urllib.request.Request(miqurl+"/requests?expand=resources&attributes=stamped_on&limit=100&offset="+str(nb))
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        total=jResp['count']
        nb=nb+jResp['subcount']
        for resource in jResp['resources']:
            startdate=datetime.datetime.strptime(resource['created_on'],'%Y-%m-%dT%H:%M:%SZ')
            enddate=datetime.datetime.strptime(resource['updated_on'],'%Y-%m-%dT%H:%M:%SZ')
            try:
                stampeddate=datetime.datetime.strptime(resource['stamped_on'],'%Y-%m-%dT%H:%M:%S.%fZ')
            except:
                stampeddate=startdate
            #id,uuid,name,startDate,endDate,status,user,message
            file.write(str(resource['id'])+","+str(resource['source_id'])+","+str(resource['description'])+","+str(stampeddate)+","+str(enddate)+","+str(resource['status'])+","+str(resource['userid'])+","+str(resource['message'])+"\n")
    file.close()
    return 'ok'

getUsers(authValue,miqurl)
getRun(authValue,miqurl)
