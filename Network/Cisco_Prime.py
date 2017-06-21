import urllib.request
import ssl
import base64
import json
import argparse
from datetime import date, timedelta, datetime
import re
import secret

primeurl="https://prime_fqdn/webacs/api/v1/"
authValue=base64.b64encode(bytes("user:password",'utf-8')).decode('utf-8')

def ignoreCertificate():
    context = ssl.create_default_context()
    context.check_hostname=False
    context.verify_mode = ssl.CERT_NONE
    return context

def getDevices():
    routers=[]
    count=0
    req=urllib.request.Request(primeurl+"data/Devices.json?.full=true")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", "Basic "+authValue)
    req.get_method=lambda:'GET'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    for elem in jResp['queryResponse']['entity']:
        routers.append(str(elem['devicesDTO']['deviceName'])+","+str(elem['devicesDTO']['@id']))
    for item in routers:
        print(item)
    print("Found "+str(len(routers))+" routers")

def getRouterInfo(deviceID):
    req=urllib.request.Request(primeurl+"data/InventoryDetails/"+deviceID+".json")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", "Basic "+authValue)
    req.get_method=lambda:'GET'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return jResp

def routerDel(deviceIP):
    req=urllib.request.Request(primeurl+"op/devices/deleteDevices")
    req.add_header("content-type", "application/json")
    req.add_header("Authorization", "Basic "+authValue)
    req.get_method=lambda:'PUT'
    context=ignoreCertificate()
    resp=urllib.request.urlopen(req,context=context)
    jResp=json.loads(resp.read().decode('utf-8'))
    return "ok"
