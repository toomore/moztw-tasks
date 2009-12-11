#!/usr/bin/env python
#coding=utf-8
from datamodel import angeldata,angelmailbox,angelmasterlist,guessangel
from google.appengine.api import mail
import time,datetime
from random import randrange,choice

############### Menu
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

  def showsetting(self):
    a = '<a href="/mailsetting">設定暱稱</a>'
    return a

  def guessangel(self):
    a = '<a href="/angelguess">猜一猜</a>'
    return a

  def listmenu(self):
    a = self.showmailboxmenu() + " " + self.mastermenu() + " " + self.myangel() + " " + self.showsetting() + " " + self.guessangel()
    return a

############### Send mails
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

############### Show mail box
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
        cssclass = 'fromangel'
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
    #for i in angeldata.all():
    for i in angelmasterlist.all():
      self.allmail.append(i.key().id_or_name())

class ifeelgood:
  def good(self):
    color = choice(['紅','橙','黃','綠','藍','靛','紫','黑','白'])
    nom = randrange(0,101)
    gps = choice(['東','南','西','北',])
    food = choice(['張君雅小妹妹','科學麵','五香乖乖','魷魚絲','水煮蛋','土豆麵筋','薄皮嫩雞','大麥克','滿天星',
                  '五更腸旺','豪記臭豆腐','文山清茶半糖少冰','早餐店的鮮奶茶','白馬馬力夯','維大力','保力達','蠻牛','寶礦立水得',
                  'Open 小將','全家就是你家','香雞排','阿鈣 (我有健康的膝蓋...)','麻辣鍋','饅頭夾蛋','無糖豆漿','八匙綠豆八寶冰','珍珠奶茶不加珍珠',
                  '蔥油餅','麻油雞','泰式酸辣蛤蜊義大利麵','酸辣湯','正忠排骨飯','池上便當','紅豆沙餡','四神湯','巧克力吐司加蛋加起士',
                  '草莓吐司加蛋加起士','花生吐司加蛋加起士','鍋燒烏龍麵','酸辣湯','蛋黃麵','青椒炒肉絲','羊肉燴飯','涼麵','泡菜水餃'
                  ])
    return color,nom,gps,food

class guesstheangel(angelmenu):
  def __init__(self,user = None):
    angelmenu.__init__(self,user)
    self.user = user

  def indata(self,ggangel):
    ''' Into data '''
    ## Get the key of user's angel.
    try:
      myangelkey = angeldata.get_by_key_name(self.myangels)
      guessangel(ggangel = ggangel, ref = myangelkey.key()).put()
    except:
      pass

  @property
  def guessworking(self):
    a = None
    u = angeldata.get_by_key_name(self.user)
    for i in u.ggg.order('-created_at').fetch(1):
      a = i.ggangel

    if a is not None:
      b = angeldata.get_by_key_name(a)
      #getuserinfo = b.nickname + ' (%s)' % (b.key().id_or_name()).split('@')[0]
      getuserinfo = b.nickname
    else:
      getuserinfo = None

    return getuserinfo

  @property
  def guess(self):
    getuserinfo = self.guessworking
    if getuserinfo is not None:
      rv = '小主人覺得你是： <b>%s</b>'.decode('utf-8') % getuserinfo
    else:
      rv = '小主人還沒有猜你'.decode('utf-8')

    return rv

  @property
  def whatiguess(self):
    ''' Get myangel into self.guess'''
    getuserinfo = guesstheangel(self.myangels).guessworking
    if getuserinfo is not None:
      rv = '我覺得小天使是： <b>%s</b>'.decode('utf-8') % getuserinfo
    else:
      rv = '<a href="/angelguess">我還沒有猜小天使</a>'.decode('utf-8')

    return rv
