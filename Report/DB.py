import calendar
import csv
import datetime
from dateutil.relativedelta import relativedelta
from collections import OrderedDict

def getAllUsers(userGroup='admin'):
    allUsers=OrderedDict()
    reader=csv.DictReader((open("database/allUsers.csv")))
    for row in reader:
        if userGroup!='admin':
            if row['group']==userGroup:
                allUsers[row['user']]=row['group']
        else:
            allUsers[row['user']]=row['group']
    return allUsers

def getAllGroups():
    allGroups=[]
    reader=csv.DictReader((open("database/allUsers.csv")))
    for row in reader:
        if row['group'] not in allGroups:
            allGroups.append(row['group'])
    return allGroups

def getUserGroup(user):
    group=""
    reader=csv.DictReader((open("database/allUsers.csv")))
    for row in reader:
        if row['user']==user:
            group=row['group']
            break
    return group

def getAllRun(userGroup='admin'):
    allRun=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        duration=endDate-startDate
        if userGroup!='admin':
            if getUserGroup(row['user'])==userGroup:
                allRun[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
        else:
            allRun[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allRun

def getYesterdayServices(userGroup='admin'):
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    yesterday=datetime.datetime.today()-datetime.timedelta(days=1)
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if yesterday.month==endDate.month and yesterday.year==endDate.year and yesterday.day==endDate.day:
            duration=endDate-startDate
            if userGroup!='admin':
                if getUserGroup(row['user'])==userGroup:
                    allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
            else:
                allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getYesterdayTop5Services(userGroup='admin'):
    return 'ok'

def getYesterdayTop5ServicesLabel(userGroup='admin'):
    top5=[]
    allServices={}
    reader=csv.DictReader((open("database/allRun.csv")))
    yesterday=datetime.datetime.today()-datetime.timedelta(days=1)
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if yesterday.month==endDate.month and yesterday.year==endDate.year and yesterday.day==endDate.day:
            if userGroup!='admin':
                if getUserGroup(row['user'])==userGroup:
                    if row['name'] not in allServices.keys():
                        allServices[row['name']]=1
                    else:
                        allServices[row['name']]+=1
            else:
                if row['name'] not in allServices.keys():
                    allServices[row['name']]=1
                else:
                    allServices[row['name']]+=1
    allServicesOrdered=OrderedDict(sorted(allServices.items(), key=lambda t: t[1], reverse=True))
    i=0
    for k in allServicesOrdered.keys():
        if i<5:
            top5.append(k)
        else:
            break
        i+=1
    return top5

def getLastMonthUsers(userGroup='admin'):
    allUsers={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if row['user'] in allUsers.keys():
                        allUsers[row['user']]+=1
                    else:
                        allUsers[row['user']]=1
            else:
                if row['user'] in allUsers.keys():
                    allUsers[row['user']]+=1
                else:
                    allUsers[row['user']]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items(), key=lambda t: t[1], reverse=True))
    return allUsersOrdered

def getLastYearUsers(userGroup='admin'):
    allUsers={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if row['user'] in allUsers.keys():
                        allUsers[row['user']]+=1
                    else:
                        allUsers[row['user']]=1
            else:
                if row['user'] in allUsers.keys():
                    allUsers[row['user']]+=1
                else:
                    allUsers[row['user']]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items(), key=lambda t: t[1], reverse=True))
    return allUsersOrdered

def getLastMonthUsersPerDay(userGroup='admin'):
    allUsers={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    for i in range(1,calendar.monthrange(prevmonth.year,prevmonth.month)[1]+1):
        allUsers[i]={}
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if row['user'] in allUsers[endDate.day]:
                        allUsers[endDate.day][row['user']]=allUsers[endDate.day][row['user']]+1
                    else:
                        allUsers[endDate.day][row['user']]=1
            else:
                if row['user'] in allUsers[endDate.day]:
                    allUsers[endDate.day][row['user']]=allUsers[endDate.day][row['user']]+1
                else:
                    allUsers[endDate.day][row['user']]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items()))
    userPerDay=[]
    for k,v in allUsersOrdered.items():
        nbUser=len(v.keys())
        userPerDay.append(nbUser)
    return userPerDay

def getLastYearUsersPerMonth(userGroup='admin'):
    allUsers={1:{},2:{},3:{},4:{},5:{},6:{},7:{},8:{},9:{},10:{},11:{},12:{}}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if row['user'] in allUsers[endDate.month]:
                        allUsers[endDate.month][row['user']]=allUsers[endDate.month][row['user']]+1
                    else:
                        allUsers[endDate.month][row['user']]=1
            else:
                if row['user'] in allUsers[endDate.month]:
                    allUsers[endDate.month][row['user']]=allUsers[endDate.month][row['user']]+1
                else:
                    allUsers[endDate.month][row['user']]=1
    allUsersOrdered=OrderedDict(sorted(allUsers.items()))
    userPerMonth=[]
    for k,v in allUsersOrdered.items():
        nbUser=len(v.keys())
        userPerMonth.append(nbUser)
    return userPerMonth

def getLastMonthServices(userGroup='admin'):
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            duration=endDate-startDate
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
            else:
                allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    return allServices

def getLastMonthServicesPerDay(userGroup='admin'):
    allServices={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    for i in range(1,calendar.monthrange(prevmonth.year,prevmonth.month)[1]+1):
        allServices[i]=0
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    allServices[endDate.day]+=1
            else:
                allServices[endDate.day]+=1
    allServicesOrdered=OrderedDict(sorted(allServices.items()))
    servicePerDay=[]
    for k,v in allServicesOrdered.items():
        servicePerDay.append(v)
    return servicePerDay

def getLastYearServices(userGroup='admin'):
    allServices=OrderedDict()
    reader=csv.DictReader((open("database/allRun.csv")))
    prevyear=datetime.datetime.today()+relativedelta(years=-1)
    for row in reader:
        startDate=datetime.datetime.strptime(row['startDate'],'%Y-%m-%d %H:%M:%S')
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevyear.year==endDate.year:
            duration=endDate-startDate
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                        allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
            else:
                allServices[row['id']]={"uuid":row['uuid'],"name":row['name'],"duration":duration,"status":row['status'],"user":row['user'],"message":row['message']}
    allServicesOrdered=OrderedDict(sorted(allServices.items()))
    return allServicesOrdered

def getLastYearServicesPerMonth(userGroup='admin'):
    allServices={1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevyear=datetime.datetime.today()+relativedelta(years=-1)
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevyear.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    allServices[endDate.month]+=1
            else:
                allServices[endDate.month]+=1
    allServicesOrdered=OrderedDict(sorted(allServices.items()))
    servicePerMonth=[]
    for k,v in allServicesOrdered.items():
        servicePerMonth.append(v)
    return servicePerMonth

def getLastMonthErrors(userGroup='admin'):
    allErrors={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if row['message'] in allErrors.keys() and row['status']=='error':
                        allErrors[row['message']]={"nb":allErrors[row['message']]['nb']+1,"service":row['name']}
                    elif row['status']=='error':
                        allErrors[row['message']]={"nb":1,"service":row['name']}
            else:
                if row['message'] in allErrors.keys() and row['status']=='error':
                    allErrors[row['message']]={"nb":allErrors[row['message']]['nb']+1,"service":row['name']}
                elif row['status']=='error':
                    allErrors[row['message']]={"nb":1,"service":row['name']}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items(), key=lambda t: t[1]['nb'], reverse=True))
    return allErrorsOrdered

def getLastYearErrors(userGroup='admin'):
    allErrors={}
    reader=csv.DictReader((open("database/allRun.csv")))
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        prevyear=datetime.datetime.today()+relativedelta(years=-1)
        if prevyear.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if row['message'] in allErrors.keys() and row['status']=='error':
                        allErrors[row['message']]={"nb":allErrors[row['message']]['nb']+1,"service":row['name']}
                    elif row['status']=='error':
                        allErrors[row['message']]={"nb":1,"service":row['name']}
            else:
                if row['message'] in allErrors.keys() and row['status']=='error':
                    allErrors[row['message']]={"nb":allErrors[row['message']]['nb']+1,"service":row['name']}
                elif row['status']=='error':
                    allErrors[row['message']]={"nb":1,"service":row['name']}
    allErrorsOrdered=OrderedDict(sorted(allErrors.items(), key=lambda t: t[1]['nb'], reverse=True))
    return allErrorsOrdered

def getLastMonthErrorsRatePerDay(userGroup='admin'):
    allErrors={}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevmonth=datetime.datetime.today()+relativedelta(months=-1)
    for i in range(1,calendar.monthrange(prevmonth.year,prevmonth.month)[1]+1):
        allErrors[i]={"nb":0,"total":0}
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevmonth.month==endDate.month and prevmonth.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if endDate.day in allErrors.keys():
                        if row['status']=='error':
                            allErrors[endDate.day]={"nb":allErrors[endDate.day]['nb']+1,"total":allErrors[endDate.day]['total']+1}
                        else:
                            allErrors[endDate.day]={"nb":allErrors[endDate.day]['nb'],"total":allErrors[endDate.day]['total']+1}
            else:
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

def getLastYearErrorsRatePerMonth(userGroup='admin'):
    allErrors={1:{"nb":0,"total":0},2:{"nb":0,"total":0},3:{"nb":0,"total":0},4:{"nb":0,"total":0},5:{"nb":0,"total":0},6:{"nb":0,"total":0},7:{"nb":0,"total":0},8:{"nb":0,"total":0},9:{"nb":0,"total":0},10:{"nb":0,"total":0},11:{"nb":0,"total":0},12:{"nb":0,"total":0}}
    reader=csv.DictReader((open("database/allRun.csv")))
    prevyear=datetime.datetime.today()+relativedelta(years=-1)
    for row in reader:
        endDate=datetime.datetime.strptime(row['endDate'],'%Y-%m-%d %H:%M:%S')
        if prevyear.year==endDate.year:
            if userGroup!='admin':
                if userGroup==getUserGroup(row['user']):
                    if endDate.month in allErrors.keys():
                        if row['status']=='error':
                            allErrors[endDate.month]={"nb":allErrors[endDate.month]['nb']+1,"total":allErrors[endDate.month]['total']+1}
                        else:
                            allErrors[endDate.month]={"nb":allErrors[endDate.month]['nb'],"total":allErrors[endDate.month]['total']+1}
            else:
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
