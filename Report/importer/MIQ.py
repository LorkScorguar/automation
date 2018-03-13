#This script is used to create database from ManageIQ API
dbRun="../database/allRun.csv"
dbUser="../database/allUsers.csv"

import base64
import datetime
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
    file.write("user,group\n")
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

def getRun(authValue,miqurl):
    total=1
    nb=0
    file=open(dbRun,"w")
    file.write("id,uuid,name,startDate,endDate,status,user,message\n")
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
            if 'source_id' in resource.keys():
                uuid=resource['source_id']
            else:
                uuid=0
            if resource['status']=="Error":
                status="error"
            else:
                status="success"
            if resource['status']!="Ok":
                message=re.sub(".*Message ","",resource['message'])
            else:
                message=resource['message']
            file.write(str(resource['id'])+","+str(uuid)+","+str(resource['description'])+","+str(stampeddate.strftime('%Y-%m-%d %H:%M:%S'))+","+str(enddate)+","+str(status)+","+str(resource['userid'])+","+str(message)+"\n")
    file.close()
    return 'ok'

getUsers(authValue,miqurl)
getRun(authValue,miqurl)
