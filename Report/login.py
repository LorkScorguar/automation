from flask import Flask, Blueprint, session, redirect, render_template, url_for, escape, request
import DB

login_page=Blueprint("login_page",__name__)
@login_page.route('/login', methods=['GET', 'POST'])

def login():
    invalid=False
    if request.method == 'POST':
        if request.form['username']=="admin" and request.form['password']=="admin":
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            session['group'] = DB.getUserGroup(request.form['username'])
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            invalid=True
    return render_template('login.html',invalid=invalid)
