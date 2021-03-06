#This script is used to create database from ManageIQ API
dbRun="../database/allRun.csv"
dbUser="../database/allUsers.csv"

import base64
from collections import OrderedDict
import datetime
import json
import re
import ssl
import urllib.request
import urllib.parse

import secret

user,password=secret.getCLProd()
authValue="Basic "+base64.b64encode(bytes(user+":"+password,'utf-8')).decode('utf-8')
miqurl=secret.getCLURLProd()

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
    file.write("admin,admin\n")
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

def getRunInit(authValue,miqurl):
    allRuns={}
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
            try:
                name=resource['description'].split("[")[1].split("]")[0]
            except:
                if re.search('VM Reconfigure',resource['description']):
                    name=resource['description'].split(" - ")[1].split(":")[0]
                else:
                    name=resource['description']
            allRuns[resource['id']]=str(resource['id'])+","+str(uuid)+","+str(name)+","+str(stampeddate.strftime('%Y-%m-%d %H:%M:%S'))+","+str(enddate)+","+str(status)+","+str(resource['userid'])+","+str(message)+"\n"
    allRunsOrdered=OrderedDict(sorted(allRuns.items()))
    for k,v in allRunsOrdered.items():
        file.write(v)
    file.close()
    return 'ok'

def getRunDaily(authValue,miqurl):
    allRuns={}
    total=1
    nb=0
    yesterday=datetime.datetime.today()-datetime.timedelta(days=1)
    date=yesterday.strftime("%Y-%m-%d")+" 06:00:00"
    file=open(dbRun,"a")
    #file.write("id,uuid,name,startDate,endDate,status,user,message\n")
    param={"expand":"resources","attributes":"stamped_on","limit":100,"filter[]":"created_on>'"+date+"'","offset":nb}
    paramEncoded=urllib.parse.urlencode(param)
    while nb < total:
        req=urllib.request.Request(miqurl+"/requests?"+paramEncoded)
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
            try:
                name=resource['description'].split("[")[1].split("]")[0]
            except:
                if re.search('VM Reconfigure',resource['description']):
                    name=resource['description'].split(" - ")[1].split(":")[0]
                else:
                    name=resource['description']
            allRuns[resource['id']]=str(resource['id'])+","+str(uuid)+","+str(name)+","+str(stampeddate.strftime('%Y-%m-%d %H:%M:%S'))+","+str(enddate)+","+str(status)+","+str(resource['userid'])+","+str(message)+"\n"
    allRunsOrdered=OrderedDict(sorted(allRuns.items()))
    for k,v in allRunsOrdered.items():
        file.write(v)
    file.close()
    return 'ok'

getUsers(authValue,miqurl)
#getRunInit(authValue,miqurl)
getRunDaily(authValue,miqurl)
