from flask import url_for
from flask_mail import Message
from app import mail


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
        sender='esiidat.sultengprov@gmail.com',
        recipients=[user.email])
    msg.body = f'''Ikuti link berikut untuk reset password: 
{url_for('accounts.reset_token', token=token, _external=True)}

Jika anda tidak meminta permintaan ini maka silahkan mengabaikan email ini
    '''
    mail.send(msg)