from flask import Flask, Blueprint, session, redirect, url_for, escape, request
import DB

login_page=Blueprint("login_page",__name__)
@login_page.route('/login', methods=['GET', 'POST'])

def login():
    login_form='''
        <form method="post">
            <p>Username:<input type=text name=username></p>
            <p>Password:<input type=secret name=password></p>
            <p><input type=submit value=Login></p>
        </form>
    '''
    if request.method == 'POST':
        if request.form['username']=="admin" and request.form['password']=="admin":
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            session['group'] = DB.getUserGroup(request.form['username'])
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            login_form="<p>invalid credentials</p>"+login_form
    return login_form
