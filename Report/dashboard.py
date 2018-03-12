from flask import Flask, session, redirect, render_template, url_for, escape, request
from login import login_page

app = Flask(__name__)
app.register_blueprint(login_page)

@app.route('/')
def index():
    """if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    else:
        redirect(url_for('login_page.login'))"""
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login_page.login'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
