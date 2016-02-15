#!/opt/opsware/bin/python2.7
# -*- coding: utf-8 -*-

#this script extract all custom scripts that are used in Audit

import sys
sys.path.append("/opt/opsware/pylibs27")
import datetime
from pytwist import *
from pytwist.com.opsware.search import Filter
import re
import subprocess
import getpass
import os

def extractAllScripts(user,passw,folderID):
        ts=twistserver.TwistServer()
        ts.authenticate(user, passw)
        folderService=ts.folder.FolderService
        lauditPRef=folderService.getChildren(com.opsware.folder.FolderRef(folderID))
        auditPolicyService=ts.compliance.sco.AuditPolicyService
        for i in range(len(lauditPRef)):
                item=auditPolicyService.getAuditPolicyVO(lauditPRef[i])
                try:
                        file=open(item.name,"w")
                        file.write("DESCRIPTION:\n"+str(item.description)+"\nCONTROL SCRIPT:\n"+str(item.getPolicy().getSCOPolicy()[0].rules[0].script)+"\nREMEDIATION SCRIPT:\n"+str(item.getPolicy().getSCOPolicy()[0].rules[0].remediateScript)+"\n")
                        file.close()
                except:
                        os.remove(item.name)
                        continue
        return "ok"

def run():
        global pcount
        global spcount
        user=raw_input("enter your username:")
        passw=getpass.getpass("enter password for "+user+":")
	folderID=input("Enter folder id that contains all audits:")
	extractAllScripts(user,passw,folderID)

run()
