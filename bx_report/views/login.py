import smtplib
from datetime import date
from email.mime.text import MIMEText

import flask
import flask_login

from bx_report import app, VCAP
from bx_report.DIfactory.get_table import get_table
from bx_report.flask_user.user import user_loader
from bx_report.utils.Utilsdate import Utilsdate
from bx_report.views import GlobalV


# the route() decorator tells Flask what URL should trigger this function
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')

    if flask.request.method == 'POST':

        email = flask.request.form['email']
        password = flask.request.form['pw']
        auth_info = get_table(VCAP).client._authenticate(email, password)

        if auth_info:  # successfully authenticated
            GlobalV.set_current_date(Utilsdate.stringnize_date(date.today()))
            GlobalV.set_organizations(auth_info[1])
            if not auth_info[0]:  # normal user
                user = user_loader(email)
                flask_login.login_user(user)  # login created user
                return flask.redirect(flask.url_for(
                    'report_user_rt', date_str='current'))
            else:  # super user
                user = user_loader(email)
                flask_login.login_user(user)
                return flask.redirect(flask.url_for(
                    'report_admin_summary_rt', date_str='current'))

        return 'Bad login'


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for('login'))


@app.route('/forgotten', methods=['GET', 'POST'])
def forgotten():
    if flask.request.method == 'GET':
        return flask.render_template('forgotten.html')

    if flask.request.method == 'POST':
        email = flask.request.form['email']
        msg = MIMEText('Please reset password for {}.'.format(email))
        sender = email.strip()
        receiver = ['yu.liu003@gmail.com']
        msg['Subject'] = 'OPEN Bluemix reporting platform - password reset demand.'
        msg['From'] = email.strip()
        msg['To'] = 'yu.liu003@gmail.com'
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login('yu.liu003@gmail.com', 'password')
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return flask.redirect(flask.url_for('login'))
