"""
Server for workbot

Reccurents tasks:
- check if AWS access_key is older than 90 days and replace it if needed
- check ManageIQ to see if there is pending requests
"""
import datetime
import sys
sys.path.append("../AWS")
import iam
import Config

def reccuring():
    today = datetime.datetime.now(datetime.timezone.utc)
    days90 = today-datetime.timedelta(days=90)
    dres = iam.checkKeyForUser(False,Config.aws_user)
    for k,v in dres.items():
        for ac in v:
            if ac['createdDate']<days90:
                print("Access key "+ac['accessKeyId']+" for user "+k+" is old ("+str(age)+" days)")


if __name__ == '__main__':
    print("Welcome")
    reccuring()
