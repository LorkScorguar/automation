import csv
import datetime
from collections import OrderedDict
from dateutil.relativedelta import relativedelta

def getAllRun():
    allRun=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S.%f')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        duration=endDate-startDate
        allRun[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allRun

def getYesterdayServices():
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S.%f')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        yesterday=datetime.datetime.today()-datetime.timedelta(days=1)
        if yesterday.month==endDate.month and yesterday.year==endDate.year and yesterday.day==endDate.day:
            duration=endDate-startDate
            allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getLastMonthUsers():
    allUsers={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if row['user'] in allUsers.keys():
                allUsers[row['user']]+=1
            else:
                allUsers[row['user']]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items(), key=lambda t: t[1], reverse=True))
    return allUsersOrdered

def getLastYearUsers():
    allUsers={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            if row['user'] in allUsers.keys():
                allUsers[row['user']]+=1
            else:
                allUsers[row['user']]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items(), key=lambda t: t[1], reverse=True))
    return allUsersOrdered

def getLastMonthUsersPerDay():
    allUsers={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if endDate.day in allUsers.keys():
                allUsers[endDate.day]+=1
            else:
                allUsers[endDate.day]=1
    print(allUsers)
    allUsersOrdered=OrderedDict(sorted(allUsers.items(), key=lambda t: t[1], reverse=True))
    print(allUsersOrdered)
    userPerDay=[]
    for k,v in allUsersOrdered.items():
        userPerDay.append(v)
    return userPerDay

def getLastYearUsersPerMonth():
    allUsers={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            if endDate.month in allUsers.keys():
                allUsers[endDate.month]+=1
            else:
                allUsers[endDate.month]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items(), key=lambda t: t[1], reverse=True))
    userPerMonth=[]
    for k,v in allUsersOrdered.items():
        userPerMonth.append(v)
    return userPerMonth

def getLastMonthServices():
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S.%f')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            duration=endDate-startDate
            allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getLastYearServices():
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S.%f')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            duration=endDate-startDate
            allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getLastMonthErrors():
    allErrors={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if row['message'] in allErrors.keys() and row['status']=='error':
                allErrors[row['message']]={"nb":allErrors[row['message']]['nb']+1,"service":row['name']}
            else:
                allErrors[row['message']]={"nb":1,"service":row['name']}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items(), key=lambda t: t[1], reverse=True))
    return allErrorsOrdered

def getLastYearErrors():
    allErrors={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            if row['message'] in allErrors.keys() and row['status']=='error':
                allErrors[row['message']]={"nb":allErrors[row['message']]['nb']+1,"service":row['name']}
            else:
                allErrors[row['message']]={"nb":1,"service":row['name']}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items(), key=lambda t: t[1], reverse=True))
    return allErrorsOrdered
