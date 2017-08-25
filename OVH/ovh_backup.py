import argparse
import json
import os
import sys
import ovh

AK=""
AS=""
CK=""
pcc=""


def getCK():
    client = ovh.Client(endpoint='ovh-eu',
                        application_key=AK,
                        application_secret=AS)

    # Request RO, /me API access
    ck = client.new_consumer_key_request()
    ck.add_rules(ovh.API_READ_ONLY, "/me")
    ck.add_recursive_rules(ovh.API_READ_WRITE, "/dedicatedCloud")

    # Request token
    validation = ck.request()

    print ("Please visit %s to authenticate" % validation['validationUrl'])
    input("and press Enter to continue...")

    # Print nice welcome message
    print ("Welcome", client.get('/me')['firstname'])
    print ("Btw, your 'consumerKey' is '%s'" % validation['consumerKey'])
    global CK
    CK=validation['consumerKey']

def getVMID(client,dcID,vmName):
    res=0
    result = client.get('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm')
    for vm in result:
        result2 = client.get('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm/'+str(vm))
        if result2['name']==vmName:
            res=result2['vmId']
            break
    return res

def getVMName(client,dcID,vmID):
    result = client.get('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm/'+str(vmID))
    return result['name']

def viewBackup(client,dcID,vmID):
    try:
        result = client.get('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm/'+str(vmID)+'/backupJob')
    except:
        print("There was an error")
        sys.exit(1)
    return result

def enableBackup(client,dcID,vmID):
    try:
        result = client.post('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm/'+str(vmID)+'/backupJob/enable',
                             backupDays=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        print(result)
    except:
        print("There was an error")
        sys.exit(1)

def disableBackup(client,dcID,vmID):
    try:
        result = client.post('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm/'+str(vmID)+'/backupJob/disable')
        print(result)
    except:
        print("There was an error")
        sys.exit(1)

def editBackup(client,dcID,vmID):
    try:
        result = client.post('/dedicatedCloud/'+pcc+'/datacenter/'+str(dcID)+'/vm/'+str(vmID)+'/backupJob',
                             backupDays=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        print(result)
    except:
        print("There was an error")
        sys.exit(1)

def viewTasks(client):
    result = client.get('/dedicatedCloud/'+pcc+'/task')
    print(result)

def viewTask(client,taskID):
    result = client.get('/dedicatedCloud/'+pcc+'/task/'+str(taskID))
    print(result)

def listDCs(client):
    result = client.get('/dedicatedCloud/'+pcc+'/datacenter')
    return result

def listVMs(client):
    ldc = listDCs(client)
    dvms={}
    for dc in ldc:
        dvms[dc]=client.get('/dedicatedCloud/'+pcc+'/datacenter/'+str(dc)+'/vm')
    return dvms

def checkBackups(client):
    dvms=listVMs(client)
    dbackups={}
    for k,v in dvms.items():
        for vm in v:
            try:
                jResp=viewBackup(client,k,vm)
                if jResp['vmName'] is not None:
                    dbackups[jResp['vmName']]=jResp['state']
                else:
                    vmName=getVMName(client,k,vm)
                    dbackups[vmName]=jResp['state']
            except:
                dbackups[vm]="error"
    return dbackups

def generateBackupCsv(client):
    dbackups=checkBackups(client)
    csv=open("ovh-backups.csv","w")
    for k,v in dbackups.items():
        if v=="delivered":
            csv.write(k+"\n")
    csv.close()


if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Tools around OVH API")
    parser.add_argument('-bc','--backup-check', action='store_true', default=False, help='Get Backup status for all vms')
    parser.add_argument('-bcsv','--backup-csv', action='store_true', default=False, help='Create a csv containing all backuped machines')
    parser.add_argument('-bd','--backup-disable', action='store', dest='databd', metavar='vm,datacenter', default=False, help='Disable backups on vm')
    parser.add_argument('-be','--backup-enable', action='store', dest='databe', metavar='vm,datacenter', default=False, help='Enable backups on vm')
    parser.add_argument('-bv','--backup-view', action='store', dest='databv', metavar='vm,datacenter', default=False, help='View backups on vm')
    parser.add_argument('-gc','--getCK', action='store_true', default=False, help='Get Customer Key')
    parser.add_argument('--tasks-view', action='store_true', default=False, help='View Tasks on pcc')
    parser.add_argument('-tv','--task-view', action='store', dest='taskID', metavar='taskID', default=False, help='View Tasks on pcc')
    dargs=parser.parse_args()
    client = ovh.Client(endpoint='ovh-eu',
                        application_key=AK,
                        application_secret=AS,
                        consumer_key=CK)
    if dargs.backup_check:
        dbackups=checkBackups(client)
        for k,v in dbackups.items():
            print(str(k)+":"+str(v))
    elif dargs.backup_csv:
        generateBackupCsv(client)
        print("CSV generated")
    elif dargs.databd:
        vmid=dargs.databd.split(",")[0]
        vmDC=dargs.databd.split(",")[1]
        vmID=vmid.split("-")[1]
        dcID=vmDC.split("datacenter")[1]
        disableBackup(client,dcID,vmID)
    elif dargs.databe:
        vmid=dargs.databe.split(",")[0]
        vmDC=dargs.databe.split(",")[1]
        vmID=vmid.split("-")[1]
        dcID=vmDC.split("datacenter")[1]
        enableBackup(client,dcID,vmID)
    elif dargs.databv:
        vmid=dargs.databv.split(",")[0]
        vmDC=dargs.databv.split(",")[1]
        vmID=vmid.split("-")[1]
        dcID=vmDC.split("datacenter")[1]
        r=viewBackup(client,dcID,vmID)
        print(r)
    elif dargs.getCK:
        getCK()
    elif dargs.tasks_view:
        viewTasks(client)
    elif dargs.taskID:
        viewTask(client,dargs.taskID)
    else:
        parser.print_help()
