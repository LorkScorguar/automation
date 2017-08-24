"""
This script allow you to:
 + update Automate Domain using git
 + call ManageIQ function
 + check if a service exist
 + create a service
 + get Miq Version
 + list VMs
 + tag vm
 + set vm's ownership
 + approve/deny request
"""

import urllib.request
import http.client
import base64
import getpass
import ssl
import xml.etree.ElementTree as ET
import ipaddress
import json
import string
import re
import time
import sys
import argparse


def auth():
    """Get auth infos and generate base64 string"""
    user=input("Enter your username: ")
    password=getpass.getpass("Enter password for " +user+": ")
    authValue=base64.b64encode(bytes(user+":"+password,'utf-8')).decode('utf-8')
    return "Basic "+authValue

def ignoreCertificate():
    """Function to ignore ssl certificate error"""
    context = ssl.create_default_context()
    context.check_hostname=False
    context.verify_mode = ssl.CERT_NONE
    return context

def getServiceTemplateId(authMiq,miqurl):
    dservicesTemplate={}
    req=urllib.request.Request(miqurl+"/service_templates?expand=resources")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authMiq)
    req.get_method=lambda:'GET'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    for item in jResp:
        dservicesTemplate=[item['name']]=item['id']
    return dservicesTemplate

def checkServiceExist(authValue,miqurl,serviceName,serviceType):
    exist=False
    service_id=0
    dservicesTemplate=getServiceTemplateId(authValue,miqurl)
    req=urllib.request.Request(miqurl+"/services?filter[]=service_template_id="+str(dservicesTemplate[serviceType])+"&filter[]=name="+str(serviceName))
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'GET'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    if jResp['subcount']==1:
        exist=True
        service_id=jResp['resources'][0]["id"]
    return exist,service_id

def addService(authValue,miqurl,jinputs):
    """Allow to order a service from the first catalog"""
    jinputs2={"auto_approve":"true","user_name":"admin"}
    data={"action":"order","resource":jinputs,"requester":jinputs2}
    req=urllib.request.Request(miqurl+"/service_catalogs/1/service_templates")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'POST'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,json.dumps(data).encode('utf-8'),context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    service_id=jResp['results'][0]['service_order_id']
    return jResp,service_id

def callFunction(authValue,miqurl,namespace,classe,functionName):
    """Allow you to call a method in automate"""
    jinputs={"namespace":namespace,"class":classe,"instance":functionName}
    jinputs2={"auto_approve":"true","user_name":"admin"}
    data={"version":"1.1","parameters":{"mode":"debug"},"uri_parts":jinputs,"requester":jinputs2}
    req=urllib.request.Request(miqurl+"/automation_requests")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'POST'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,json.dumps(data).encode('utf-8'),context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp

def listVMS(authValue,miqurl):
    total=1
    nb=0
    nbOK=0
    while nb < total:
        req=urllib.request.Request(miqurl+"/vms?expand=resources&attributes=hardware&limit=100&offset="+str(nb))
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        req.get_method=lambda:'GET'
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        total=jResp['count']
        for item in jResp['resources']:
            print(str(item['name'])+" "+str(item['hardware']['cpu_total_cores'])+" "+str(item['hardware']['memory_mb']))
        nb=nb+jResp['subcount']
    return 'ok'

def updateDomain(authValue,miqurl,domain,branch):
    req=urllib.request.Request(miqurl+"/automate_domains?expand=resources")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context = ignoreCertificate()
    resp = urllib.request.urlopen(req,context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    domainid = 0
    for item in jResp['resources']:
        if item['name'] == domain:
            domainid = item['id']
    req=urllib.request.Request(miqurl+"/automate_domains/"+str(domainid))
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method = lambda:'POST'
    data = {"action": "refresh_from_source", "branch":branch}
    resp = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    response = jResp['message']+" "+str(jResp['success'])
    return response

def updateApproval(authValue,miqurl,requestID,action):
    req = urllib.request.Request(miqurl+"/service_requests/"+requestID)
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'POST'
    context = ignoreCertificate()
    if action == "deny":
        message = "not ok"
    else:
        message = "ok"
    data = {"action": action,
            "reason": message}
    resp = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    if jResp['success'] == True:
        resp = jResp['message']
    else:
        resp = "An error occured:"+jResp['message']
    return resp

def approveDeny(authValue,miqurl):
    req = urllib.request.Request(miqurl+"/service_requests?expand=resources")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context = ignoreCertificate()
    resp = urllib.request.urlopen(req, context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    print("Below Requests are pending approval:")
    nb = 0
    for request in jResp['resources']:
        if request['request_state'] == 'pending' and request['approval_state'] == 'pending_approval':
            print(str(request['id'])+":"+request['description']+":"+request['requester_name'])
            nb =+ 1
    if nb > 0:
        choice = input("Enter action to do (d or a +requestID): ")
        requestID = choice[1:]
        if choice[0] == "d":
            action = "deny"
        elif choice[0] == "a":
            action = "approve"
        if requestID == "0":
            exit(0)
        else:
            resp = updateApproval(authValue,miqurl,requestID,action)
            print(resp)

def checkPendingRequests(authValue,miqurl):
    res=""
    req = urllib.request.Request(miqurl+"/service_requests?expand=resources")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context = ignoreCertificate()
    resp = urllib.request.urlopen(req, context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    nb = 0
    for request in jResp['resources']:
        if request['request_state'] == 'pending' and request['approval_state'] == 'pending_approval':
            res+=str(request['id'])+":"+request['description']
            nb += 1
    return nb,res

def setOwnership(authValue,miqurl,serviceID,username,groupname):
    req = urllib.request.Request(miqurl+"/services/"+serviceID)
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'POST'
    context = ignoreCertificate()
    data = {"action": "set_ownership",
            "resource": {
                "owner" : { "userid" : username},
                "group" : { "description" : groupname}
             }
           }
    resp = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    if jResp['success'] == True:
        resp = jResp['message']
    else:
        resp = "An error occured:"+jResp['message']
    return resp

def setGroup(authValue,miqurl,vmID,groupname):
    req = urllib.request.Request(miqurl+"/vms/"+vmID)
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'POST'
    context = ignoreCertificate()
    data = {"action": "set_ownership",
            "resource": {
                "group" : {"description":groupname}
             }
           }
    resp = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    if jResp['success'] == True:
        resp = jResp['message']
    else:
        resp = "An error occured:"+jResp['message']
    return resp

def wrapperSetOwnership(authValue,miqurl,params):
    serviceID=params.split(",")[0]
    username=params.split(",")[1]
    groupname=params.split(",")[2]
    resp = setOwnership(authValue,miqurl,serviceID,username,groupname)
    return resp

def tagResource(authValue,miqurl,resource_url,itemID,category,tag):
    req = urllib.request.Request(miqurl+"/"+resource_url+"/"+itemID+"/tags")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    req.get_method=lambda:'POST'
    context = ignoreCertificate()
    data = {"action": "assign",
            "resources": [{
                "category" : category,
                "name" : tag
            }]
           }
    resp = urllib.request.urlopen(req, json.dumps(data).encode('utf-8'), context=context)
    jResp = json.loads(resp.read().decode('utf-8'))
    if jResp['results'][0]['success'] == True:
        resp = jResp['results'][0]['message']
    else:
        resp = "An error occured:"+jResp['results'][0]['message']
    return resp

def wrapperTagResource(authValue,miqurl,params):
    resource_type = params.split(",")[0]
    itemID = params.split(",")[1]
    category = params.split(",")[2]
    tag = params.split(",")[3]
    resource_url = ""
    if resource_type == "template":
        resource_url = "service_templates"
    else:
        resource_url = "vms"
    resp = tagServiceTemplate(authValue,miqurl,resource_url,itemID,category,tag)
    return resp

def getUsers(authValue,miqurl):
    """Extract all users in a csv file"""
    total=1
    nb=0
    vmid=0
    file=open("usersextract.csv","w")
    while nb < total:
        req=urllib.request.Request(miqurl+"/users?expand=resources&attributes=id,name,userid&limit=100&offset="+str(nb))
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        req.get_method=lambda:'GET'
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        total=jResp['count']
        for item in jResp['resources']:
            file.write(item['name']+";"+str(item['userid'])+"\n")
        nb=nb+jResp['subcount']
    file.close()
    return "ok"

def getOwner(authValue,miqurl,itemid):
    req=urllib.request.Request(miqurl+"/users/"+str(itemid))
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp['name']

def getTags(authValue,miqurl,itemid):
    req=urllib.request.Request(miqurl+"/vms/"+str(itemid)+"/tags?expand=resources")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    tags=[]
    for item in jResp['resources']:
        tags.append(item['name'])
    return tags

def extractData(authValue,miqurl):
    """Extract all machines with user info and tags"""
    total=1
    nb=0
    file=open("extractData.csv","w")
    while nb < total:
        req=urllib.request.Request(miqurl+"/vms?expand=resources&attributes=id,name,evm_owner_id&limit=100&offset="+str(nb))
        req.add_header("content-type", "application/json")
        req.add_header("Authorization", authValue)
        req.get_method=lambda:'GET'
        context=ignoreCertificate()
        resp=urllib.request.urlopen(req,context=context)
        jResp=json.loads(resp.read().decode('utf-8'))
        total=jResp['count']
        for item in jResp['resources']:
            tags=getTags(authValue,miqurl,item['id'])
            try:
                owner=getOwner(authValue,miqurl,item['evm_owner_id'])
            except:
                owner="no owner"
            file.write(item['name']+";"+owner+";"+','.join(tags)+"\n")
        nb=nb+jResp['subcount']
        print(nb)
    file.close()

###############Sample###############
def getVersion(authValue,miqurl):#simply get ManageIQ API Version
    req=urllib.request.Request(miqurl)
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", authValue)
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp['version']

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Tools around ManageIQ")
    parser.add_argument('-a','--add', action='store', dest='jinputs', default=False, help='Add Service')
    parser.add_argument('-ad','--approve-deny', action='store_true', default=False, help='Review pending request and choose to approve or deny')
    parser.add_argument('-ap','--approve', action='store', dest='requestID_approve', metavar='<requestID>', default=False, help='Allow you to approve requestID')
    parser.add_argument('-f','--function', action='store', dest='functionName', metavar='<NS/Cl/functionName>', default=False, help='Call Automate methods')
    parser.add_argument('-de','--deny', action='store', dest='requestID_deny', metavar='<requestID>', default=False, help='Allow you to deny requestID')
    parser.add_argument('-g','--git', action='store', dest='domain', default=False, help='Update domain as arg using git')
    parser.add_argument('-lv','--list-vms', action='store_true', default=False, help='List all VMs with cpu and mem info')
    parser.add_argument('-so','--set-ownership', action='store', dest='ownergroup', default=False, help='Set Ownership for a service ownergroup=serviceID,owner,group')
    parser.add_argument('-t','--tag', action='store', dest='resourceParams', default=False, help='Tag a resource, resourceParams=type,id,category,tag')
    parser.add_argument('-v','--version', action='store_true', default=False, help='Return ManageIQ Automate Version')
    dargs=parser.parse_args()
    authValue=auth()
    #try:
    if 1:
        branch="origin/master"
        miqurl="https://fqdn/api"
        if dargs.jinputs:
            r,id=addService(authValue,miqurl,dargs.jinputs)
            print(r)
            print("Service id:"+str(id))
        elif dargs.approve_deny:
            approveDeny(authValue,miqurl)
        elif dargs.requestID_approve:
            resp = updateApproval(authValue,miqurl,dargs.requestID_approve,'approve')
            print(resp)
        elif dargs.functionName:
            tmp=dargs.function.split("/")
            functionName=tmp[-1]
            classe=tmp[-2]
            del tmp[-1]
            del tmp[-1]
            namespace='/'.join(tmp)
            r=callFunction(authValue,miqurl,namespace,classe,functionName)
            print(r)
        elif dargs.requestID_deny:
            resp = updateApproval(authValue,miqurl,dargs.requestID_deny,'deny')
            print(resp)
        elif dargs.domain:
            r=updateDomain(authValue,miqurl,dargs.domain,branch)
            print(r)
        elif dargs.list_vms:
            listVMS(authValue,miqurl)
        elif dargs.ownergroup:
            resp  = wrapperSetOwnership(authValue, miqurl, dargs.ownergroup)
            print(resp)
        elif dargs.resourceParams:
            resp  = wrapperTagResource(authValue, miqurl, dargs.resourceParams)
            print(resp)
        elif dargs.version:
            version=getVersion(authValue,miqurl)
            print(version)
        else:
            parser.print_help()
    #except:
    #    parser.print_help()
