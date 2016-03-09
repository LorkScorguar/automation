"""
A simple script to show what can we do with OO 10 API
It allows you to:
- get OO version
- verify Content Pack version between multiple Centrals
- verify System Properties and System Account values in Central if they should be override
- purge OO database
- get OO database statistics
- get audit records
- launch flow
- get monthly statistics for flows

written by Florent Pied
"""

import json
import urllib.request
import base64
import os
import getpass
import datetime
import math
import re
import ssl

global centrals
centrals=["CENTRAL1;https://<ip>:<port>/oo/rest/<apiVersion>/"]

def auth():
    user=input("Enter your username: ")
    password=getpass.getpass("Enter password for " +user+": ")
    authValue=base64.b64encode(bytes(user+":"+password,'utf-8')).decode('utf-8')
    return "Basic "+authValue

def ignoreCertificate():
    context = ssl.create_default_context()
    context.check_hostname=False
    context.verify_mode = ssl.CERT_NONE
    return context

def chooseCentral():
    central=0
    global centrals
    print("For which platform do you want to check version?")
    for it in range(len(centrals)):
        tmp=centrals[it].split(";")
        print(str(it)+"-"+tmp[0])
    choice=input(">")
    central=centrals[int(choice)].split(";")[1]
    return central

def getVersion(authValue,oourl):#simply get OO Version
    req=urllib.request.Request(oourl+"version")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp['version']

def getCP(authValue,oourl):#return a dict containing all CP+their version
    req=urllib.request.Request(oourl+"content-packs")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context).read().decode('utf-8')
    jResp=json.loads(resp)
    dcp={}
    for cp in jResp:
        dcp[cp['name']]=cp['version']
    return dcp

def getSA(authValue,oourl,SAname):#get All System Accounts
    req=urllib.request.Request(oourl+"config-items/system-accounts/"+SAname)
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context).read().decode('utf-8')
    jResp=json.loads(resp)
    return jResp

def getSP(authValue,oourl,SPname):#get All System Properties
    req=urllib.request.Request(oourl+"config-items/system-properties/"+SPname)
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context).read().decode('utf-8')
    jResp=json.loads(resp)
    return jResp

def purgeDBExec(authValue,oourl,ts):#purge database execution events
    req=urllib.request.Request(oourl+"debugger-events?endedBefore="+str(ts))
    req.get_method=lambda:'DELETE'
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp

def purgeDBExecData(authValue,oourl,ts):#purge database execution data(inputs,outputs)
    req=urllib.request.Request(oourl+"executions?endedBefore="+str(ts)+"&purgeItems=steps,flowInputs,flowOutputs")
    req.get_method=lambda:'DELETE'
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp

def purgeDBStep(authValue,oourl,ts):#delete stepLog data
    req=urllib.request.Request(oourl+"steps-log?endedBefore="+str(ts))
    req.get_method=lambda:'DELETE'
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp

def getDBStats(authValue,oourl):#get database statistics
    req=urllib.request.Request(oourl+"db-statistics")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    print(jResp)
    return jResp

def getAuditRecord(authValue,oourl):
    req=urllib.request.Request(oourl+"audit/records")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    for item in jResp:
        d=datetime.datetime.fromtimestamp(int(str(item['time'])[:-3]))
        if item['type']=="RunTriggered":
            data=json.loads(item['data'])
            print("["+str(d)+"]"+"("+str(item['subject'])+")"+str(item['group'])+":"+str(item['type'])+"("+str(data['uuid'])+")")
        elif item['type']=='ContentUploadToDeploymentProcess':
            data=json.loads(item['data'])
            print("["+str(d)+"]"+"("+str(item['subject'])+")"+str(item['group'])+":"+str(item['type'])+"("+str(data['fileName'])+")")
        else:
            print("["+str(d)+"]"+"("+str(item['subject'])+")"+str(item['group'])+":"+str(item['type']))
    return "ok"

def launchFlow(authValue,oourl,flowID,inputs,runName):
    tmp=inputs.split(",")
    jinputs={}
    for item in tmp:
        t=item.split(":")
        jinputs[t[0]]=t[1]
    flow={"uuid":flowID,"runName":runName,"inputs":jinputs}
    req=urllib.request.Request(oourl+"executions")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,json.dumps(flow).encode('utf-8'),context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    print(jResp)
    return 'ok'

def getStatsForFlow(authValue,oourl,flowUUID,ts,month):
    nbFlow=0
    nb=1000
    duration=0
    i=1
    file=open("monthlyStats-"+month+".csv","a")
    while nb==1000:
        req=urllib.request.Request(oourl+"executions?startedAfter="+str(ts)+"&pageSize=1000&pageNum="+str(i)+"&flowUuid="+flowUUID)
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        nb=len(jResp)
        nbFlow+=nb
        i+=1
        duration=datetime.timedelta(0)
        medium=datetime.timedelta(0)
        if nb > 0:
            for item in jResp:
                try:
                    end=datetime.datetime.fromtimestamp(int(str(item['endTime'])[:-3]))
                    start=datetime.datetime.fromtimestamp(int(str(item['startTime'])[:-3]))
                    duration=(end-start)
                    medium+=(end-start)
                except:
                    continue
                n=item['flowPath'].split("/")
                name=n[len(n)-1][:-4]
                file.write(name+";"+str(item['executionId'])+";"+str(duration.seconds)+"\n")
            medium=medium/len(jResp)
        medium=medium.seconds*0.0166
    file.close()
    return nbFlow,duration

def getStats(authValue,oourl,month):
    dflows={"flow1":"flow1Uuid"}
    nbFlows=0
    duration=0
    timestamp=(datetime.datetime(2016,int(month),1)-datetime.datetime(1970,1,1))/datetime.timedelta(seconds=1)
    ts=math.floor(timestamp)*1000
    nbFlows,duration=getStatsForFlow(authValue,oourl,"",ts)
    print(str(nbFlows)+" flows were launched this month, duration is about "+str(duration))
    for k,v in dflows.items():
        nbFlows,duration=getStatsForFlow(authValue,oourl,v,ts,month)
        print(str(nbFlows)+" "+str(k)+" flows were launched this month, duration is about "+str(duration)+" minutes")
    return 'ok'

def generateDefaultSP(authValue):#generate System Properties value list
    global centrals
    oodev=centrals[0].split(";")[1]
    path=input("Enter path to System Propeties folder for a specific project:")
    #path="C:\\Users\\test\\.oo\\Workspace\\MonContentPack\\Content\\Configuration\\System Properties" #this is a sample
    allSP=[]
    for file in os.listdir(path):
        allSP.append(file.split(".")[0])
    allSPValue={}
    for sp in allSP:
        try:
            jResp=getSP(authValue,oodev,sp)
            allSPValue[sp]=jResp['defaultValue']
        except:
            allSPValue[sp]='Not Defined'
    file=open("spDev.json","w")
    json.dump(allSPValue,file)
    file.close()


def verifySPDEV(authValue):#Check if all System Properties value are equal to the default value
    global centrals
    oodev=centrals[0].split(";")[1]
    commonSP=json.load(open("spDev.json",'r'))
    i=0
    for k,v in commonSP.items():
        try:
            jResp=getSP(authValue,oodev,k)
            if jResp['value']!=v:
                i+=1
                print("[DEV]"+jResp['name']+" don't have correct value")
        except:
            print("[DEV]Got a problem when verifying "+k)
    if i==0:
        print("[DEV]All System Properties have the correct value")

def verifySPHOMOSTD(authValue):#Check if all System Properties value are equal to the value they should have in HOMO (verify override)
    global centrals
    oohomostd=centrals[3].split(";")[1]
    commonSP=json.load(open("spHOMOSTD.json",'r'))
    i=0
    for k,v in commonSP.items():
        try:
            jResp=getSP(authValue,oohomostd,k)
            if jResp['value']!=v:
                i+=1
                print("[HOMO]"+jResp['name']+" don't have correct value")
        except:
            print("[HOMO]Got a problem when verifying "+k)
    if i==0:
        print("[HOMO]All System Properties have the correct value")

def verifySPPRODSTD(authValue):#Check if all System Properties value are equal to the value they should have in PROD (verify override)
    global centrals
    ooprodstd=centrals[7].split(";")[1]
    commonSP=json.load(open("spPRODSTD.json",'r'))
    i=0
    for k,v in commonSP.items():
        try:
            jResp=getSP(authValue,ooprodstd,k)
            if jResp['value']!=v:
                i+=1
                print("[PROD]"+jResp['name']+" don't have correct value")
        except:
            print("[PROD]Got a problem when verifying "+k)
    if i==0:
        print("[PROD]All System Properties have the correct value")

def verifyCP(authValue):#check if all CP have the same version in DEV, HOMO and PROD
    global centrals
    oodev=centrals[0].split(";")[1]
    oohomostd=centrals[3].split(";")[1]
    ooprodstd=centrals[7].split(";")[1]
    try:
        dcpdev=getCP(authValue,oodev)
    except:
        dcpdev={}
    try:
        dcphomostd=getCP(authValue,oohomostd)
    except:
        dcphomostd={}
    try:
        dcpprodstd=getCP(authValue,ooprodstd)
    except:
        dcpprodstd={}
    if dcpdev!={} and dcphomostd!={} and dcpprodstd!={}:
        for k,v in dcpdev.items():
            for k2,v2 in dcphomostd.items():
                for k3,v3 in dcpprodstd.items():
                    if k==k2==k3:
                        if v!=v2 or v!=v3 or v2!=v3:
                            print(k+" version is different DEV("+v+") HOMO("+v2+") PROD("+v3+")")

def run():
    authValue=auth()
    choice=input("What do you want?\n1-Verify Content Pack version\n2-Verify System Properties\n3-Get OO Version\n4-Purge Database\n5-Get Database Stats\n6-Get Audit Records\n7-Launch Flow\n8-Get Monthly Flows\n>")
    result=""
    if choice=="1":
        verifyCP(authValue)
    elif choice=="2":
        central=input("For which platform do you want to check System Properties?\n1-DEV\n2-HOMO STD\n3-PROD STD\n4-All STD\n")
        if central=="1":
            generateDefaultSP(authValue)
            verifySPDEV(authValue)
        elif central=="2":
            verifySPHOMOSTD(authValue)
        elif central=="3":
            verifySPPRODSTD(authValue)
        elif central=="4":
            generateDefaultSP(authValue)
            verifySPDEV(authValue)
            verifySPHOMOSTD(authValue)
            verifySPPRODSTD(authValue)
        else:
            result="I don't understand"
    elif choice=="3":
        central=chooseCentral()
        result=getVersion(authValue,central)
    elif choice=="4":
        nbe=100
        nbed=100
        nbs=100
        nbeDeleted=0
        nbedDeleted=0
        nbsDeleted=0
        d=datetime.datetime.today()-datetime.timedelta(days=7)
        timestamp=(d-datetime.datetime(1970,1,1))/datetime.timedelta(seconds=1)
        ts=math.floor(timestamp)*1000
        central=chooseCentral()
        while nbe == 100:
            nbe=purgeDBExec(authValue,central,ts)
            nbeDeleted+=nbe
        while nbed == 100:
            nbed=purgeDBExecData(authValue,central,ts)
            nbedDeleted+=nbed
        while nbs == 100:
            nbs=purgeDBStep(authValue,central,ts)
            nbsDeleted+=nbs
        result="Delete "+str(nbeDeleted)+" Executions\nDelete "+str(nbedDeleted)+" Executions Data\nDelete "+str(nbsDeleted)+" Steps Data"
    elif choice=="5":
        central=chooseCentral()
        result=getDBStats(authValue,central)
    elif choice=="6":
        central=chooseCentral()
        result=getAuditRecord(authValue,central)
    elif choice=="7":
        central=chooseCentral()
        flowID=input("Enter flow ID:")
        inputs=input("Enter inputs for flow:")
        runName="test"
        result=launchFlow(authValue,central,flowID,inputs,runName)
        result=""
    elif choice=="8":
        central=chooseCentral()
        month=int(input("Enter month[1-12]: "))
        getStats(authValue,central,month)
    else:
            result="I don't understand"
    print(result)

if __name__== '__main__':
    run()
