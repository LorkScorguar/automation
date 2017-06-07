# Automation
Some scripts written to automate tasks on:
 - HPE OO
 - HPE SA
 - F5
 - AWS


# AWS
Simple script to get info from AWS account
In order to have this working you need to create a secret.py file with:
 - getProxy function that will return proxy url:port
 - getAccess function that will return access_key,secret_access_key
 - getRegion function that will return region name  
All those functions must return string  
This is needed to avoid having AWS access key walking in the wild  

# HP
Some scripts to play around HPE Server Automation (SA) and HPE Operations Orchestration (OO)
Those scripts were tested on HPE SA 10.0x and HPE OO 10.2x and 10.5x

## Spin
The Spin is a low level API to manipulate objects, usefull to debug or solve conflicts in HPSA  
Spin is available by web on https://< coreIP >:1004 (you need the spin-developper certificate)

## Twist
Twist is a component that give access to a powerfull API in java, python and C#  
When you want to do something in SA with script check it.  
Twist is available by web on https://< coreIP >:1032  

# Network
Some scripts to play with network equipments and automate them
