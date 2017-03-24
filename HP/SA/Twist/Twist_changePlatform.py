#!/opt/opsware/bin/python2.7
# -*- coding: utf-8 -*-

#this script allow to change supported platform for packages and Software Policies
#as a sample, this version tick RHEL7 compat for all packages and Software Policies that are already compatible with RHEL6 in HPSA

import sys
sys.path.append("/opt/opsware/pylibs27")
import datetime
from pytwist import *
from pytwist.com.opsware.search import Filter
import re
import subprocess
import getpass

global pcount
global spcount
pcount=0
spcount=0

def getAllSP(user,passw):
	ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
	spService=ts.swmgmt.SoftwarePolicyService
	lspRef=spService.findSoftwarePolicyRefs(Filter())
	return lspRef

def changeSPPlatform(user,passw,spRef):
	result=""
        change=False
        global spcount
        ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
	spService=ts.swmgmt.SoftwarePolicyService
	spVO=spService.getSoftwarePolicyVO(spRef)
	lplatforms=spVO.getPlatforms()
	for plat in lplatforms:
                if re.search("Red Hat Enterprise Linux Server 6 X86_64",plat.name):
                        change=True
	if change:
		spcount+=1
		rhel7Ref=com.opsware.device.PlatformRef(61100)
		newLPlatforms=lplatforms+(rhel7Ref,)
		spVO.setPlatforms(newLPlatforms)
		spService.update(spRef, spVO, True, True)

def getAllZip(user,passw):
	ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
        zipService=ts.pkg.ZIPService
	filter=Filter()
	lzipRef=zipService.findZIPRefs(filter)
	return lzipRef

def changeZIPPlatform(user,passw,zipRef):
	result=""
	change=False
	global pcount
        ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
        zipService=ts.pkg.ZIPService
	platformService=ts.device.PlatformService
	zipVO=zipService.getZIPVO(zipRef)
	lplatforms=zipVO.getPlatforms()
	for plat in lplatforms:
		if re.search("Red Hat Enterprise Linux Server 6 X86_64",plat.name):
			change=True
	if change:
		pcount+=1
		rhel7Ref=com.opsware.device.PlatformRef(61100)
		newLPlatforms=lplatforms+(rhel7Ref,)
		zipVO.setPlatforms(newLPlatforms)
		zipService.update(zipRef, zipVO, True, True)



def run():
	global pcount
	global spcount
	user=raw_input("enter your username:")
    passw=getpass.getpass("enter password for "+user+":")	
	lzipRef=getAllZip(user,passw)
	for zipRef in lzipRef:
        	changeZIPPlatform(user,passw,zipRef)
	lspRef=getAllSP(user,passw)
        for spRef in lspRef:
                changeSPPlatform(user,passw,spRef)
	print("Changed "+str(pcount)+" packages")
	print("Changed "+str(spcount)+" software policies")

run()
