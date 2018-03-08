import csv

def getAllRun():
    allRun={}
    reader=csv.DictReader((open("database/allRun.csv"))
    for row in reader:
        allRun[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":row['duration'],"status":row['status']}
    return allRun
