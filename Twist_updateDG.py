#!/opt/opsware/bin/python
"""
A simple script to populate Device Group swith rules automatically
Avoid the usage of Dynamic Device Group
"""

import sys
sys.path.append('/opt/opsware/pylibs2')
from pytwist import *


s=twistserver.TwistServer()
dgService=ts.device.DeviceGroupService
serverService=ts.server.ServerService
global ts
global dgService
global serverService

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
    dgContent=dgRef.getDevices()
    return dgContent

def getNewContent(rule):
    newDGContent=[]
    filterDvc=com.opsware.search.Filter()
    filterDvc.expression = rule
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
    dgRef.removeDevices(toRemove)
    dgRef.addDevices(toAdd)


if __name__ == '__main__':
    if sys.argv[1] == "-help" or sys.argv[1] == "-h" or len(sys.argv)>2:
        usage()
    else:
        dgRef=sys.argv[1]
        rule=sys.argv[2]
        modifyDG(dgRef,rule)