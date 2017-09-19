"""
Server for workbot

Reccurents tasks:
- check if AWS access_key is older than 90 days and replace it if needed
- check ManageIQ to see if there is pending requests
"""
import base64
import datetime
import os
import sys
import threading
import time
sys.path.append("../AWS")
import iam
sys.path.append("../ManageIQ")
import MIQ
import Config

def updateConfig(param,value):
    #save configuration
    save={}
    cfg=open("Config.py","r")
    for line in cfg:
        parm=line.strip().split("=")[0]
        val=line.strip().split("=")[1]
        save[parm]=val
    cfg.close()
    #do the change and write file
    save[param]='"'+value+'"'
    cfg=open("Config.py","w")
    for k,v in save.items():
        cfg.write(str(k)+"="+str(v)+"\n")
    cfg.close()

def setProxy():
    os.environ['http_proxy']=Config.http_proxy
    os.environ['https_proxy']=Config.https_proxy
    os.environ['HTTP_PROXY']=Config.http_proxy
    os.environ['HTTPS_PROXY']=Config.https_proxy

def checkMIQ(authValue,clconfig):
    url=clconfig['url']
    platform="Miq "+clconfig['name']
    nb,res=MIQ.checkPendingRequests(authValue,url)
    if nb > 0:
        title="["+platform+"] Awaiting Validations: "+str(nb)
        print(title)
        print(res)
        print("\n")
        while nb > 0:
            choice = input("Enter action to do (d or a +requestID): ")
            requestID = choice[1:]
            if choice[0] == "d":
                action = "deny"
            elif choice[0] == "a":
                action = "approve"
            resp = MIQ.updateApproval(authValue,url,requestID,action)
            print(resp)
            nb-=1
    else:
        print("["+platform+"] Nothing awaiting you")

def checkAWS(user):
    today = datetime.datetime.now(datetime.timezone.utc)
    days90 = today-datetime.timedelta(days=90)
    dres = iam.checkKeyForUser(False,user)
    for k,v in dres.items():
        for ac in v:
            if ac['createdDate']<days90:
                age=(today-ac['createdDate']).days
                print("Access key "+ac['accessKeyId']+" for user "+k+" is old ("+str(age)+" days)")
                ak,sak=iam.generateKey(False,user)
                updateConfig("aws_access_key",ak)
                updateConfig("aws_secret_key",sak)
                iam.deleteKey(False,user,Config.aws_access_key)

def recurring(id, e, stop):
    while True:
        if stop():
            break
        #AWS
        #checkAWS(Config.aws_user)
        #ManageIQ
        authValue="Basic "+base64.b64encode(bytes(Config.cluser+":"+Config.clpassword,'utf-8')).decode('utf-8')
        checkMIQ(authValue,Config.clurlppr)
        checkMIQ(authValue,Config.clurlprd)
        e.wait(timeout=600)



if __name__ == '__main__':
    print("Welcome")
    quitter=False
    e=threading.Event()
    a=threading.Thread(None,recurring,"recurring",args=(id, e, lambda: quitter))
    a.start()
    while not quitter:
        inp=input(">")
        if inp=="quit":
            quitter=True
            e.set()
            a.join()
        else:
            try:
                res=eval(inp)
            except:
                if inp!="":
                    res="Received: "+str(inp)
        print(res)
    print("Bye")
