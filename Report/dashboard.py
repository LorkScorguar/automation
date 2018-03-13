import calendar
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, session, redirect, render_template, url_for, escape, request
from login import login_page
import DB

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
app.register_blueprint(login_page)

@app.route('/')
def index():
    if 'username' in session:
        data=DB.getYesterdayServices(session['group'])
        dataGraph=DB.getYesterdayTop5Services(session['group'])
        label=DB.getYesterdayTop5ServicesLabel(session['group'])
        return render_template('yesterday_services.html',data=data,dataGraph=dataGraph,graphLabel=label)
    else:
        if config['AUTHENTICATION']:
            return redirect(url_for('login_page.login'))
        else:
            session['username'] = "admin"
            session['password'] = "admin"
            session['group'] = DB.getUserGroup(request.form['username'])
            session['logged_in'] = True
            data=DB.getYesterdayServices(session['group'])
            dataGraph=DB.getYesterdayTop5Services(session['group'])
            label=DB.getYesterdayTop5ServicesLabel(session['group'])
            return render_template('yesterday_services.html',data=data,dataGraph=dataGraph,graphLabel=label)

@app.route('/last_month_users')
def last_month_users():
    if 'username' in session:
        data=DB.getLastMonthUsers(session['group'])
        dataGraph=DB.getLastMonthUsersPerDay(session['group'])
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        label=[]
        for i in range(1,calendar.monthrange(prevmonth.year,prevmonth.month)[1]+1):
            label.append(i)
        return render_template('last_month_users.html',data=data,dataGraph=dataGraph,graphLabel=label)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_month_services')
def last_month_services():
    if 'username' in session:
        data=DB.getLastMonthServices(session['group'])
        dataGraph=DB.getLastMonthServicesPerDay(session['group'])
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        label=[]
        for i in range(1,calendar.monthrange(prevmonth.year,prevmonth.month)[1]+1):
            label.append(i)
        return render_template('last_month_services.html',data=data,dataGraph=dataGraph,graphLabel=label)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_month_errors')
def last_month_errors():
    if 'username' in session:
        data=DB.getLastMonthErrors(session['group'])
        dataGraph=DB.getLastMonthErrorsRatePerDay(session['group'])
        prevmonth=datetime.datetime.today()+relativedelta(months=-1)
        label=[]
        for i in range(1,calendar.monthrange(prevmonth.year,prevmonth.month)[1]+1):
            label.append(i)
        return render_template('last_month_errors.html',data=data,dataGraph=dataGraph,graphLabel=label)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_year_users')
def last_year_users():
    if 'username' in session:
        data=DB.getLastYearUsers(session['group'])
        dataGraph=DB.getLastYearUsersPerMonth(session['group'])
        return render_template('last_year_users.html',data=data,dataGraph=dataGraph,graphLabel=[1,2,3,4,5,6,7,8,9,10,11,12])
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_year_services')
def last_year_services():
    if 'username' in session:
        data=DB.getLastYearServices(session['group'])
        dataGraph=DB.getLastYearServicesPerMonth(session['group'])
        return render_template('last_year_services.html',data=data,dataGraph=dataGraph,graphLabel=[1,2,3,4,5,6,7,8,9,10,11,12])
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_year_errors')
def last_year_errors():
    if 'username' in session:
        data=DB.getLastYearErrors(session['group'])
        dataGraph=DB.getLastYearErrorsRatePerMonth(session['group'])
        return render_template('last_year_errors.html',data=data,dataGraph=dataGraph,graphLabel=[1,2,3,4,5,6,7,8,9,10,11,12])
    else:
        return redirect(url_for('login_page.login'))

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login_page.login'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
_host=app.config['SERVERNAME']
_port=app.config['PORT']
app.run(_host,_port)
