#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datamodel import angelmailbox
from google.appengine.api import mail
from angelapp import ifeelgood

import logging

footnote = """

♥ 幸運顏色： %s
♥ 幸運號碼： %s
♥ 幸運方位： %s
♥ 幸運食物： %s
--
這是一封由雷鳥郵差代發的信件，回覆給郵差是沒有用的啦！
不過到這裡有用： http://moztw-tasks.appspot.com/mail
""" % ifeelgood().good()

mails = angelmailbox.gql('where sended = False limit 8')
if mails.count():
  logging.info('Mails: %s' % mails.count())

for i in mails:
  i.sended = bool(1)
  i.put()

  if i.sendtype == 1:
    ##God
    footnote = """

--
這是一封由雷鳥郵差代發的信件，回覆給郵差是沒有用的啦！
我是 God！不要懷疑！多多關心小主人！多多感謝小天使！
才能得永生！
http://moztw-tasks.appspot.com/mail
"""
    message = mail.EmailMessage(
      sender = 'MozTW 雷鳥郵差 <noreply@moztw-tasks.appspotmail.com>',
      subject="您有一封 God 寄來的通知！")
    message.bcc = i.to
    message.body = "這是一封 God 寄給您的信，通知重要的內容：\r\n\r\n%s %s" % (i.context.encode('utf-8'),footnote)
    message.send()

  if i.sendtype == 2:
    ## to master
    toreply = """

★ 要順手回一封給小天使嗎？
★ http://moztw-tasks.appspot.com/mailtoangel

"""
    message = mail.EmailMessage(
      sender = 'MozTW 雷鳥郵差 <noreply@moztw-tasks.appspotmail.com>',
      subject="您有一封小天使飛來的關心！")
    message.bcc = i.to
    message.body = "這是一封小天使寄給您的信，內容如下：\r\n\r\n%s %s%s" % (i.context.encode('utf-8'),toreply,footnote)
    message.send()


  if i.sendtype == 3:
    ## to angel
    toreply = """

★ 要順手回一封給小主人嗎？
★ http://moztw-tasks.appspot.com/mailtomaster

"""
    message = mail.EmailMessage(
      sender = 'MozTW 雷鳥郵差 <noreply@moztw-tasks.appspotmail.com>',
      subject="您有一封小主人寄來的感謝！")
    message.bcc = i.to
    message.body = "這是一封小主人寄給您的信，內容如下：\r\n\r\n%s %s%s" % (i.context.encode('utf-8'),toreply,footnote)
    message.send()

