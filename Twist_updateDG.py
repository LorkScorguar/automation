#!/opt/opsware/bin/python
"""
A simple script to populate Device Group swith rules automatically
Avoid the usage of Dynamic Device Group
"""

import sys
sys.path.append('/opt/opsware/pylibs2')
from pytwist import *

def usage():
    msg="""Usage: ./Twist_updateDG.py [deviceGroupRef] [rule]
    -h, --help          Display this help
    [DeviceGroupRef]    Should be a Device Group ID as dsplayed in SA client
    [rule]              A valid rule for a Device Group
    """
    print(msg)
    sys.exit(0)

def getDGContent(dgRef):
    dgContent=[]
    dgContent=dgService.getDevices(dgRef)
    return dgContent

def getNewContent(rule):
    newDGContent=[]
    filterDvc=com.opsware.search.Filter()
    filterDvc.expression = rule
    #filterDvc.expression = 'ServerVO.osVersion contains Linux'
    filterDvc.objectType = 'device'
    newDGContent=serverService.findServerRef(filterDvc)
    return newDGContent

def modifyDG(dgRef,rule):
    dgContent=getDGContent(dgRef)
    newDGContent=getNewContent(rule)
    toAdd=[]
    toRemove=[]
    for dvc in newDGContent:
        if dvc not in dgContent:
            toAdd.append(dvc)
    for dvc in dgContent:
        if dvc not in newDGContent:
            toRemove.append(dvc)
    dgService.removeDevices(dgRef,toRemove)
    dgService.addDevices(dgRef,toAdd)


if __name__ == '__main__':
    if len(sys.argv)!=2:
        if sys.argv[1] == "-help" or sys.argv[1] == "-h":
            usage()
        else:
            global ts
            global dgService
            global serverService
            ts=twistserver.TwistServer()
            user=input("Enter SA username:")
            passw=input("Enter password for "+user+": ")
            ts.authenticate(user,passw)
            dgService=ts.device.DeviceGroupService
            serverService=ts.server.ServerService
            dgRef=com.opsware.device.DeviceGroupRef(sys.argv[1])
            rule=sys.argv[2]
            modifyDG(dgRef,rule)
    else:
        usage()