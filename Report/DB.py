import calendar
import csv
import datetime
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

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
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    fd,ld=calendar.monthrange(prevmonth.year,prevmonth.month)
    for i in range(fd,ld):
        allUsers[i]=0
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            allUsers[endDate.day]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items()))
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
            allUsers[endDate.month]+=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items()))
    userPerMonth=[]
    for k,v in allUsersOrdered.items():
        userPerMonth.append(v)
    return userPerMonth

def getLastMonthServices():
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S.%f')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            duration=endDate-startDate
            allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getLastMonthServicesPerDay():
    allServices={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    fd,ld=calendar.monthrange(prevmonth.year,prevmonth.month)
    for i in range(fd,ld):
        allServices[i]=0
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            allServices[endDate.day]+=1
    return allServices

def getLastYearServices():
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    prevyear=datetime.datetime.today()+relativedelta(years=-1)
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S.%f')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevyear.year==endDate.year:
            duration=endDate-startDate
            allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getLastYearServicesPerMonth():
    allServices={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevyear=datetime.datetime.today()+relativedelta(years=-1)
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevyear.year==endDate.year:
            allServices[endDate.month]+=1
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
            elif row['status']=='error':
                allErrors[row['message']]={"nb":1,"service":row['name']}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items(), key=lambda t: t[1]['nb'], reverse=True))
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
            elif row['status']=='error':
                allErrors[row['message']]={"nb":1,"service":row['name']}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items(), key=lambda t: t[1]['nb'], reverse=True))
    return allErrorsOrdered

def getLastMonthErrorsRatePerDay():
    allErrors={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    fd,ld=calendar.monthrange(prevmonth.year,prevmonth.month)
    for i in range(fd,ld):
        allErrors[i]={"nb":0,"total":0}
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if endDate.day in allErrors.keys():
                if row['status']=='error':
                    allErrors[endDate.day]={"nb":allErrors[endDate.day]['nb']+1,"total":allErrors[endDate.day]['total']+1}
                else:
                    allErrors[endDate.day]={"nb":allErrors[endDate.day]['nb'],"total":allErrors[endDate.day]['total']+1}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items()))
    errorPerDay=[]
    for k,v in allErrorsOrdered.items():
        if v['total']>0:
            errorPerDay.append((v['nb']*100)/v['total'])
        else:
            errorPerDay.append(0)
    return errorPerDay

def getLastYearErrorsRatePerMonth():
    allErrors={1:{"nb":0,"total":0},2:{"nb":0,"total":0},3:{"nb":0,"total":0},4:{"nb":0,"total":0},5:{"nb":0,"total":0},6:{"nb":0,"total":0},7:{"nb":0,"total":0},8:{"nb":0,"total":0},9:{"nb":0,"total":0},10:{"nb":0,"total":0},11:{"nb":0,"total":0},12:{"nb":0,"total":0}}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevyear=datetime.datetime.today()+relativedelta(years=-1)
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S.%f')
        if prevyear.year==endDate.year:
            if endDate.month in allErrors.keys():
                if row['status']=='error':
                    allErrors[endDate.month]={"nb":allErrors[endDate.month]['nb']+1,"total":allErrors[endDate.month]['total']+1}
                else:
                    allErrors[endDate.month]={"nb":allErrors[endDate.month]['nb'],"total":allErrors[endDate.month]['total']+1}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items()))
    errorPerMonth=[]
    for k,v in allErrorsOrdered.items():
        if v['total']>0:
            errorPerMonth.append((v['nb']*100)/v['total'])
        else:
            errorPerMonth.append(0)
    return errorPerMonth
