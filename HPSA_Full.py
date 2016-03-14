#!/opt/opsware/bin/python2.7
# -*- coding: utf-8 -*-
"""A python script to get informations about HP SA infrastructure and do some usefull actions
This script can:
- get SA version
- get mesh state (conflicts, mirroring, sync)
- get core and satellites
- get Database configuration for cores
- get server number by facility/core
- get duplicate server
- get Dynamic Device Groups to check if some are duplicates
- get Statistics about HP SA jobs

written by Florent Pied
"""

import os
import sys
import getpass
import datetime
import re
import math
from string import Template
import collections

sys.path.append('/opt/opsware/pylibs27')
from pytwist import *
from coglib import spinwrapper
from coglib import certmaster
from pytwist.com.opsware.search import Filter

global ts
ts=twistserver.TwistServer()
global spin
ctx=certmaster.getContextByName("spin","spin.srv","opsware-ca.crt")
spin=spinwrapper.SpinWrapper(ctx=ctx)


def usage():
	msg="""Usage: ./HPSA_Full.py
	-h, --help:	Display this help
	
	This tool create a hpsa_report.html file that contain informations about your HP SA infrastructure
	"""
	print(msg)
	sys.exit(1)


#=========================Format Functions=========================
def getIdFromRef(ref):
        tmp=str(ref).split("Ref:")
        return str(tmp[1][:-1])

def getNameFromRef(ref):
        tmp=str(ref).split(" (")
        return str(tmp[0])

def t2d(timestamp):#timestamp to date in string
	date=datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
	return date

def b2m(bytes):#bytes to mega:
	size=0
        size=bytes/(1024*1024.0)
        return "%.2f MB" % size

def b2g(bytes):#bytes to giga
	size=0
	size=bytes/(1024*1024*1024.0)
	return "%.2f GB" % size

def formatRollups(rollups):
	result="<table>"
	for k,v in rollups.iteritems():
		result+="<tr><th>"+k+"</th><td>"+' '.join(v)+"</td></tr>"
	return result+"</table>"

def formatMirroring(status):
	result="<p>Number of files:"+str(status.getTotalCount())+"<br/>Total size: "+b2g(status.getTotalBytes())+"</p><table><tr><th>Mirroring</th><th>Facility</th><th>Files</th><th>Size</th><th>Missing</th></tr>"
	for item in status.getInfos():
		state="Disable"
		color="gray"
		if item.mirroringEnabled and item.missingCount==0:
			state="Enable"
			color="green"
		elif item.mirroringEnabled and item.missingCount!=0:
			state="Enable"
			color="yellow"
		result+="<tr><td class="+color+">"+state+"</td><td>"+item.facilityName+"</td><td>"+str(item.realmCount)+"</td><td>"+b2g(item.realmBytes)+"</td><td>"+str(item.missingCount)+"</td></tr>"
	return result+"</table>"

def formatCores(dcore):
	result="<table><tr><th>ID</th><th>Facility</th></tr>"
	for item in dcore:
		result+="<tr><td>"+str(item['id'])+"</td><td>"+item['display_name']+"</td></tr>"
	return result+"</table>"

def reportHTML():
    tpl=Template("""<html>
    <head>
        <meta http-equiv=Content-Type content='text/html; charset=utf-8'>
        <title>HP SA Report</title>
	<style>
		table{
			border: 1px solid black;
		}
		.green{
			background-color: green;
		}
		.gray {
			background-color: gray;
		}
		.yellow {
			background-color: yellow;
		}
		.red {
			background-color: red;
		}
	</style>
    </head>
    <body>
        <h2>HP Server Automation $saVersion</h2>
        <p> Started on: $startDate</p>
        <div id='versions'>
	    <h3>Versions</h3>
            <table>
                <tr><th>Component</th><th>Version</th></tr>
                <tr><td>Twist</td><td>$twistVersion</td></tr>
                <tr><td>Spin</td><td>$spinVersion</td></tr>
                <tr><td>Spin DB</td><td>$spinDBVersion</td></tr>
            </table>
        </div>
        <div id='rollups'><h3>Rollups</h3><p>
		$rollups
        </p></div>
        <div id='mesh-infos'><h3>Mesh Status</h3>
                <p>Conflicts: $conflicts</p>
		<h3>Software Repository Mirroring</h3>
		$mirroring
		<h3>Mesh Synchronization</h3>
		$sync
        </div>
        <div id='cores'>
	    <h3>Cores</h3>
	    $cores
            <p>hardware, id, nb core, nb sat, if sat are in HA, sat link to cores</p>
        </div>
        <div id='db'>
        <div>
        <div id='servers'><h3>Servers</h3>
            <p>number and repartition<br />
            duplicates</p>
        <div>
        <div id='devicegroups'>
            <p>number and duplicate dynamics</p>
        <div>
        <div id='jobs'><h3>Jobs</h3>
            <p>number of jobs per month $jobNumber<br />
            job by type<br />
            average length by type<br />
            average number of target by type</p>
        </div>
    </body>
</html>
""")
    today=datetime.datetime.today()
    saVersion=getSAVersion()
    twistVersion=getTwistVersion()
    spinVersion=getSpinVersion()
    spinDBVersion=getSpinDBVersion()
    startDate=getSAStartDate()
    drollups=getRollups()
    rollups=formatRollups(drollups)
    conflicts=getConflicts()
    dmirroring=getMirroring()
    mirroring=formatMirroring(dmirroring)
    dcore=getCores()
    cores=formatCores(dcore)
    sync=""
    jobNumber=getJobsStats()
    report=tpl.substitute(saVersion=saVersion,twistVersion=twistVersion,spinVersion=spinVersion,spinDBVersion=spinDBVersion,rollups=rollups,startDate=t2d(startDate),conflicts=conflicts,mirroring=mirroring,sync=sync,cores=cores,jobNumber=jobNumber)
    file=open("hpsa_report.html","w")
    file.write(report)
    file.close()


#=========================Pure HP SA Functions=========================
def getSAVersion():
	version=ts.shared.TwistConsoleService.getAPIVersionLabel()
	version=version.split(" ")[1]
	return str(version)

def getTwistVersion():
	version=ts.shared.TwistConsoleService.getVersion()
	return str(version)

def getSAStartDate():
	startDate=ts.shared.TwistConsoleService.getStartDate()
	return startDate

def getSpinVersion():
	version=spin.sys.getConfDirective(directive='spin.version')
	return str(version)

def getSpinDBVersion():
	version=spin.sys.getConfDirective(directive='spin.db.version')
	return str(version)

def getRollups():
	drollups=collections.OrderedDict()
	path="/opt/opsware/hotfix/"
	major=os.listdir(path)
	for item in major:
		minor=os.listdir(path+item)
		if item!="installed":
			for it in minor:
				try:
					rollupVersion=open(path+item+"/"+it+"/VERSION","r").read()
					drollups[rollupVersion]=os.listdir(path+item+"/"+it+"/installed")
				except:
					continue
	return drollups

def getConflicts():
	lconflicts=spin.multimaster.getConflicts()
	return str(len(lconflicts['conflicts']))

def getMirroring():
	status=ts.locality.RealmService.getMirroringStatus()
	return status

def getCores():
	dcores=spin.DataCenter.getCores()
	return dcores

def getMeshSync():
	state=spin.multimaster.getState("meshstate",count_only=1)
	return state

#def getFacilities():

def getAgentRepartition():
	print()

def getJobsStats():
	jobService=ts.job.JobService
	filtre=Filter()
	filtre.objectType='job'
	filtre.expression="JobInfoVO.startDate within_last_months 1"
	result=jobService.findJobRefs(filtre)
	number=len(result)
	return str(number)

#=========================Main=========================

def run():
	if len(sys.argv) > 1:
		if sys.argv[1]=="-h" or sys.argv[1]=="--help":
			usage()
	else:
		reportHTML()

#run()
getAgentRepartition()
