#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from google.appengine.api import mail
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class LogSenderHandler(InboundMailHandler):
  def receive(self, mail_message):
    logging.info("Received a message from: " + mail_message.sender + mail_message.subject)

    message = mail.EmailMessage(sender = 'MozTW God <noreply@moztw-tasks.appspotmail.com>',
    subject="No Reply！")
    message.to = mail_message.sender
    message.body = "寄這裡不會有任何回應的！\r\n請利用這個雷鳥傳信系統 http://moztw-tasks.appspot.com/mail"
    message.send()

application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
run_wsgi_app(application)
