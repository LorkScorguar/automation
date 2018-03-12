import calendar
from flask import Flask, session, redirect, render_template, url_for, escape, request
from login import login_page
import DB

app = Flask(__name__)
app.register_blueprint(login_page)

@app.route('/')
def index():
    if 'username' in session:
        data=DB.getYesterdayServices()
        return render_template('yesterday_services.html',data=data)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_month_users')
def last_month_users():
    if 'username' in session:
        data=DB.getLastMonthUsers()
        dataGraph=DB.getLastMonthUsersPerDay()
        fd,ld=calendar.monthrange(prevmonth.year,prevmonth.month)
        label=[]
        for i in range(fd,ld):
            label.append(i)
        return render_template('last_month_users.html',data=data,dataGraph=dataGraph,graphLabel=label)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_month_services')
def last_month_services():
    if 'username' in session:
        data=DB.getLastMonthServices()
        return render_template('last_month_services.html',data=data)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_month_errors')
def last_month_errors():
    if 'username' in session:
        data=DB.getLastMonthErrors()
        return render_template('last_month_errors.html',data=data)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_year_users')
def last_year_users():
    if 'username' in session:
        data=DB.getLastYearUsers()
        dataGraph=DB.getLastYearUsersPerMonth()
        return render_template('last_year_users.html',data=data,dataGraph=dataGraph,graphLabel=['january','february','march','april','may','june','july','august','september','october','november','december'])
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_year_services')
def last_year_services():
    if 'username' in session:
        data=DB.getLastYearServices()
        return render_template('last_year_services.html',data=data)
    else:
        return redirect(url_for('login_page.login'))

@app.route('/last_year_errors')
def last_year_errors():
    if 'username' in session:
        data=DB.getLastYearErrors()
        return render_template('last_year_errors.html',data=data)
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
