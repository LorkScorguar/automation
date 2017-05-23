# Automation
Some scripts written for HP SA (Server Automation) and HP OO (Operations Orchestration)
Those scripts were tested on HP SA 10.0x and HP OO 10.2x and 10.5x

# AWS
Simple script to get info from AWS account
In order to have this working you need to create a secret.py file with:
 - getProxy function that will return proxy url:port
 - getAccess function that will return access_key,secret_access_key
 - getRegion function that will return region name
All those functions must return string
This is needed to avoid having AWS access key walking in the wild

# HP
Some scripts to play around HP Server Automation and HP Operations Orchestration

## Spin
The Spin is a low level API to manipulate objects, usefull to debug or solve conflicts in HPSA
Spin is available by web on https://<coreIP>:1004 (you need the spin-developper certificate)

## Twist
Twist is a component that give access to a powerfull API in java, python and C#
When you want to do something in SA with script check it.
Twist is available by web on https://<coreIP>:1032

# Network
Some scripts to play with network equipments and automate them
