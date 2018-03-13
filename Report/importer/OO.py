#This script is used to create database from OO API
dbRun="database/allRun.csv"
dbUser="database/allUsers.csv"

import base64
import datetime
import json
import re
import ssl
import urllib.request

import secret

user,password=secret.getOODev()
authValue="Basic "+base64.b64encode(bytes(user+":"+password,'utf-8')).decode('utf-8')
oourl=secret.getOOURLDEV()

def ignoreCertificate():
    context = ssl.create_default_context()
    context.check_hostname=False
    context.verify_mode = ssl.CERT_NONE
    return context

def getUsers(authValue,oourl):
    file=open(dbUser,"w")
    file.write("user,group\n")
    file.write("admin,admin\n")
    file.close()
    return 'ok'

def getStatsForFlow(authValue,oourl):
    nbFlow=0
    nb=1000
    duration=0
    i=1
    file=open(dbRun,"w")
    file.write("id,uuid,name,startDate,endDate,status,user,message\n")
    while nb==1000:
        req=urllib.request.Request(oourl+"executions?&pageSize=1000&pageNum="+str(i))
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        nb=len(jResp)
        nbFlow+=nb
        i+=1
        if nb > 0:
            for item in jResp:
                try:
                    end=datetime.datetime.fromtimestamp(int(str(item['endTime'])[:-3]))
                    start=datetime.datetime.fromtimestamp(int(str(item['startTime'])[:-3]))
                except:
                    continue
                n=item['flowPath'].split("/")
                name=n[len(n)-1][:-4]
                #id,uuid,name,startDate,endDate,status,user,message
                file.write(str(item['executionId'])+","+str(item['uuid'])+","+name+","+str(start)+","+str(end)+","+str(item['status'])+","+str(item['user'])+","+str(item['message'])+"\n")
    file.close()
    return 'ok'
