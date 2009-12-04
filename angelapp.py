#!/usr/bin/env python
#coding=utf-8
from datamodel import angeldata,angelmailbox
from google.appengine.api import mail
import time,datetime

class angelmenu:
  def __init__(self,angel):
    self.angel = angel
    self.an = angeldata.gql("WHERE mymaster = '%s'" % self.angel)
    try:
      self.myangels = self.an.get().key().id_or_name()
    except:
      self.myangels = None
    #self.master = self.an.get().get_by_key_name(angel).mymaster
    self.master = angeldata.get_by_key_name(angel).mymaster

  def mastermenu(self):
    if self.master:
      a = '<a href="/mailtomaster">關心小主人↓</a>'
    else:
      a = '沒有建立小主人'
    return a

  def myangel(self):
    #an = angeldata.gql("WHERE mymaster = '%s'" % self.angel)
       
    if int(self.an.count()):
      #a = '<a href="/mailtoangel">呼叫小天使 %s </a>' % str(an.get().key().id_or_name())
      a = '<a href="/mailtoangel">呼叫小天使↑</a>'
    else:
      a = '哭哭！沒有小天使！'
    return a

  def showmailboxmenu(self):
    a = '<a href="/mailbox">Mailbox</a>'
    return a

  def listmenu(self):
    a = self.showmailboxmenu() + " | " + self.mastermenu() + " | " + self.myangel()
    return a

class sendmails(angelmenu):
  def __init__(self,user = None):
    angelmenu.__init__(self,user)

  def sendmails(self,context,angel=None,master=None):

    if angel:
      ## to master
      intoangelmailbox = angelmailbox(sender = self.angel,
                                      to = self.master,
                                      context = context,
                                      sendtype = 2,
                                      sended = bool(0)).put()

    elif master:
      ## to angel, need to search data.
      an = angeldata.gql("WHERE mymaster = '%s'" % self.angel)
      
      intoangelmailbox = angelmailbox(sender = self.angel,
                                      to = an.get().key().id_or_name(),
                                      context = context,
                                      sendtype = 3,
                                      sended = bool(0)).put()

class showmailbox(angelmenu):
  def __init__(self,user = None):
    angelmenu.__init__(self,user)

  def show(self,per = 10):
    import time
    findsender = angelmailbox.gql("WHERE sender = '%s' order by created_at desc" % self.angel)
    findto = angelmailbox.gql("WHERE to = '%s' order by created_at desc" % self.angel)
    c = {}
    d = {}
    for i in findsender:
      c[int(time.mktime(i.created_at.timetuple()))] = dict(sender = i.sender, to = i.to, context = i.context, time = i.created_at)

    for i in findto:
      d[int(time.mktime(i.created_at.timetuple()))] = dict(sender = i.sender, to = i.to, context = i.context, time = i.created_at)

    for i in d.keys():
      c[i] = d[i]

    desc = c.keys()
    desc.sort(reverse=1)

    dd = ''
    sender = ''
    for i in desc:
      if c[i]['sender'] == self.angel and c[i]['to'] == self.master:
        sender = 'To 小主人'
        cssclass = 'tomaster'
      elif c[i]['sender'] == self.master and c[i]['to'] == self.angel:
        sender = 'From 小主人'
        cssclass = 'frommaster'
      elif c[i]['sender'] == self.angel and c[i]['to'] == self.myangels:
        sender = 'To 小天使'
        cssclass = 'toangel'
      elif c[i]['sender'] == self.myangels and c[i]['to'] == self.angel:
        sender = 'From 小天使'
        cssclass = 'frommaster'
      else:
        sender = 'From God'
        cssclass = 'fromgod'

      if len(c[i]['context']) > 140:
        c[i]['context'] = c[i]['context'][:140] + '<i>... (略，請見信箱)</i>'.decode('utf-8')

      dd = dd + '''
<tr class='%s'><td>%s</td><td>→ %s</td><td>%s<br><i>%s ago</i></td></tr>
''' % (
        cssclass,sender,
        c[i]['context'].encode('utf-8').replace('\r\n','<br>'),
        ((c[i]['time'] + datetime.timedelta(hours=8)).ctime()),
        str(datetime.datetime.now() - c[i]['time'])[:-7]
      )
    return dd
    #return self.angel,self.master,self.myangels

class sendalluser:
  def __init__(self):
    self.allmail = []
    for i in angeldata.all():
      self.allmail.append(i.key().id_or_name())
