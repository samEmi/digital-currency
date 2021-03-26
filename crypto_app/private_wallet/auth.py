# auth.py
import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask import current_app
from private_wallet.dbs.SessionModel import SessionModel
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    data = {
        'username':request.form.get('username'),
        'password': request.form.get('password'),
    }

    if data['username'] == current_app.config['username'] \
       and data['password'] == current_app.config['password']:
        #TODO: are these access tokens necessary
        access_token = create_access_token(identity=data['username'], expires_delta=timedelta(minutes=30))
        refresh_token = create_refresh_token(identity=data['username'], expires_delta=timedelta(minutes=30))
        SessionModel.delete()
        SessionModel(access_token=access_token,
                     refresh_token=refresh_token).save()
        return redirect(url_for('main.withdraw_tokens_from_acc'))
    else:
        flash('Invalid login credentials', 'login')
        return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    data = {
        'username': request.form.get('username'),
        'password': request.form.get('password')
    }
    current_app.config['username'] = data['username']
    current_app.config['password'] = data['password']
    return redirect(url_for('auth.login'))

@auth.route('/logout')
def logout():
    return redirect(url_for('main.index'))