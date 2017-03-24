#!/opt/opsware/bin/python2.7
# -*- coding: utf-8 -*-
#this script gets output of script that ran against multiple server and format the output in a csv

import sys
sys.path.append("/opt/opsware/pylibs27")
import datetime
from pytwist import *
from pytwist.com.opsware.search import Filter
import getpass

def getIdFromRef(ref):
        tmp=str(ref).split("JobRef:")
        return str(tmp[1][:-1])

def getNameFromRef(ref):
        tmp=str(ref).split(" (")
        return str(tmp[0])

def checkJobs(user,passw,jid):
        result=""
		file=open("jobResult.csv","a")
        try:
                ts=twistserver.TwistServer()
                ts.authenticate(user, passw)
                jobService=ts.job.JobService
                result=jobService.getResult(com.opsware.job.JobRef(jid))
				for elem in result.elemResultInfo :
					file.write(str(elem.element.name)+";"+str(elem.output.exitCode)+";"+str(elem.output.tailStdout))
        except:
                result="Authentication failed."

def run():
		user=raw_input("enter your username:")
		passw=getpass.getpass("enter password for "+user+":")
		jid=raw_input("Enter job id:")
		checkJobs(user,passw,int(jid))

run()
