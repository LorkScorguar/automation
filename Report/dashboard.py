from flask import Flask, session, redirect, url_for, escape, request

app = Flask(__name__)

@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    else:
        redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form='''
        <form method="post">
            <p>Username:<input type=text name=username></p>
            <p>Password:<input type=secret name=password></p>
            <p><input type=submit value=Login></p>
        </form>
    '''
    if request.method == 'POST':
        if request.form['username']=="test" and request.form['password']=="test":
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return redirect(url_for('index'))
        else:
            login_form="<p>invalid credentials</p>"+login_form
    return login_form

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
