from threading import Thread
from typing import List, Tuple, Union

from flask import Flask, current_app, render_template
from flask_mail import Message

from . import mail


def send_async_email(app: Flask, msg: Message):
    with app.app_context():
        mail.send(msg)


def send_email(to: Union[Tuple[str], List[str]], subject: str, template: str, **kwargs) -> Thread:
    app = current_app._get_current_object()
    msg = Message(
        app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
        sender=app.config['FLASKY_MAIL_SENDER'],
        recipients=to,
        body=render_template(template + '.txt', **kwargs),
        html=render_template(template + '.html', **kwargs)
    )
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
