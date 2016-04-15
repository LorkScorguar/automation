#!/opt/opsware/bin/python2.7
# -*- coding: utf-8 -*-

#this script get last modification date for packages and SP

import sys
sys.path.append("/opt/opsware/pylibs27")
import datetime
from pytwist import *
from pytwist.com.opsware.search import Filter
import re
import subprocess
import getpass
import datetime

def getIdFromRef(ref):
        tmp=str(ref).split("Ref:")
        return str(tmp[1][:-1])

def getAllSPDate(user,passw):
	file=open("lastModifSP.csv","w")
	ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
	spService=ts.swmgmt.SoftwarePolicyService
	lspRef=spService.findSoftwarePolicyRefs(Filter())
	lspVO=spService.getSoftwarePolicyVOs(lspRef)
	for sp in lspVO:
                date=datetime.datetime.fromtimestamp(float(sp.modifiedDate)).strftime('%Y-%m-%d %H:%M')
                file.write(str(sp.name)+";"+str(date)+";"+str(sp.modifiedBy)+";"+getIdFromRef(sp.getRef())+"\n")
	file.close()
	return "ok"

def getAllZipDate(user,passw):
	file=open("lastModifZIP.csv","w")
	ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
        zipService=ts.pkg.ZIPService
	filter=Filter()
	lzipRef=zipService.findZIPRefs(filter)
	lzipVO=zipService.getZIPVOs(lzipRef)
	for zip in lzipVO:
		date=datetime.datetime.fromtimestamp(float(zip.modifiedDate)).strftime('%Y-%m-%d %H:%M')
		size=round(zip.fileSize/1048576.0,2)
		file.write(str(zip.name)+";"+str(date)+";"+str(zip.modifiedBy)+";"+str(size)+";"+getIdFromRef(zip.getRef())+"\n")
	file.close()
	return "ok"

def run():
	global pcount
	global spcount
	user=raw_input("enter your username:")
    	passw=getpass.getpass("enter password for "+user+":")
	getAllZipDate(user,passw)
	getAllSPDate(user,passw)
run()
