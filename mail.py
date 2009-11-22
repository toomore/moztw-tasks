#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging, email
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info("Received a message from: " + mail_message.sender + mail_message.subject)

application = webapp.WSGIApplication([LogSenderHandler.mapping()], debug=True)
run_wsgi_app(application)
