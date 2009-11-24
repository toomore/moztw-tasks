#!/usr/bin/env python
#coding=utf-8
from datamodel import angeldata
from google.appengine.api import mail

class angelmenu:
  def __init__(self,angel):
    self.angel = angel
    self.master = angeldata.get_by_key_name(angel).mymaster

  def mastermenu(self):
    if self.master:
      a = '<a href="/mailtomaster">關心小主人↓</a>'
    else:
      a = '沒有建立小主人'
    return a

  def myangel(self):
    an = angeldata.gql("WHERE mymaster = '%s'" % self.angel)
       
    if int(an.count()):
      #a = '<a href="/mailtoangel">呼叫小天使 %s </a>' % str(an.get().key().id_or_name())
      a = '<a href="/mailtoangel">呼叫小天使↑</a>'
    else:
      a = '哭哭！沒有小天使！'
    return a

  def listmenu(self):
    a = self.mastermenu() + " " + self.myangel()
    return a

  def sendmails(self,context,angel=None,master=None):
    footnote = """
--
這是一封由雷鳥郵差代發的信件，回覆給郵差是沒有用的啦！
不過到這裡有用： http://moztw-tasks.appspot.com/mail
"""
    if angel:
      ## to master
      message = mail.EmailMessage(sender = 'MozTW Angel <noreply@moztw-tasks.appspotmail.com>',
      subject="您有一封小天使寄來的關心！")
      message.to = self.master
      message.body = "這是一封小天使寄給您的信，內容如下：\r\n\r\n%s %s" % (context.encode('utf-8'),footnote)
      message.send()
    elif master:
      ## to angel, need to search data.
      an = angeldata.gql("WHERE mymaster = '%s'" % self.angel)
      message = mail.EmailMessage(sender = 'MozTW Master <noreply@moztw-tasks.appspotmail.com>',
      subject="您有一封小主人寄來的感謝！")
      message.to = an.get().key().id_or_name()
      message.body = "這是一封小主人寄給您的信，內容如下：\r\n\r\n%s %s" % (context.encode('utf-8'),footnote)
      message.send()
