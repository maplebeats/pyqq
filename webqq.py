#!/usr/bin/env python3
#
# Author: maplebeats
#
# gtalk/mail: maplebeats@gmail.com
#
# Last modified:	2012-08-23 15:50
#
# Filename:		webqq.py
#
# Description: Webqq class
#
from urllib import parse,request
from http import cookiejar
import random,time
import json,re,hashlib
import threading

import logging

from bot import Bot

from config import *

class Webqq:

  def _hexchar2bin(self,num):
    arry= bytearray()
    for i in range(0, len(num), 2):
      arry.append(int(num[i:i+2],16))
    return arry

  def _preprocess(self,password=None,verifycode=None):
    self.hashpasswd=self._md5(password)
    I=self._hexchar2bin(self.hashpasswd)
    H = self._md5(I + bytes(verifycode[2],encoding="ISO-8859-1"))
    G = self._md5(H + verifycode[1].upper());
    return G

  def _md5(self,string):
    try:
      string = string.encode('utf-8')
    except:
      pass
    return hashlib.md5(string).hexdigest().upper()
  
  def _request(self, url, data=None):
    if data:
      data = parse.urlencode(data).encode('utf-8')
      rr = request.Request(url,data,self._headers)
    else:
      rr = request.Request(url=url, headers=self._headers)
    with self.opener.open(rr) as fp:
      try:
        res = fp.read().decode('utf-8')
      except:
        res = fp.read()
    return res

  def __init__(self,user,passwd):

    self.__qq = user
    self.pswd = passwd

    self.cookieJar = cookiejar.CookieJar()
    self.opener = request.build_opener(request.HTTPCookieProcessor(self.cookieJar))
    self._headers = {
                   "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1",
                   "Accept-Language":"zh-cn,en;q=0.8,en-us;q=0.5,zh-hk;q=0.3",
                   "Accept-Encoding":"deflate",
                   "Connection":"keep-alive",
                   "Referer":"http://ui.ptlogin2.qq.com/cgi-bin/login?target=self&style=5&mibao_css=m_webqq&appid=1003903&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fweb.qq.com%2Floginproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20120619001"
    }

    self.clientid = "4646111"
    self._msgid = 60000000
    
    self.bot = Bot()

  def _getverifycode(self):
    urlv = 'http://check.ptlogin2.qq.com/check?uin=%s&appid=567008010&r=%s'%(self.__qq,random.Random().random())
    res = self._request(url = urlv)
    verify=eval(res.split("(")[1].split(")")[0])
    verify=list(verify)
    if verify[0]=='1':
      imgurl="http://captcha.qq.com/getimage?aid=567008010&r=%s&uin=%s"%(random.Random().random(),self.__qq)
      self.__verifyimg = "verify"
      with open(self.__verifyimg,"wb") as f:
        f.write(request.urlopen(imgurl).read())
      verify[1]=input("vf # ").strip()
    return verify

  def _login(self):
    urlv="http://ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s"%(self.__qq,self.passwd,self.__verifycode[1])+"&aid=567008010&u1=http%3A%2F%2Fweb.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=3-25-30079&mibao_css=m_webqq&t=1&g=1"
    res = self._request(url = urlv)
    if res.find('登录成功') != -1:
      logger.info("login sucess")
    elif res.find('验证码不正确') != -1:
      logger.warn('wrong verify')
      self._getverifycode()
      self._login()
    else:
      logger.error(res)

  def _poll(self):
    urlv = "http://d.web2.qq.com/channel/poll2"
    self._headers.update({"Referer":"http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"})
    status = {'clientid':self.clientid,'psessionid':self._login_info['psessionid']}
    data = {'r':json.dumps(status),
    'clientid' : self.clientid,
    'psessionid':	'null'
    }
    res = self._request(urlv,data)
    if res: 
      res = json.loads(res)
      self.message_received(res)

      heart = threading.Timer(1,self._poll)
      heart.start()
    else:
      self._poll()
  
  def connect(self):
    self.__qq = self.__qq.strip()
    self.pswd = self.pswd.strip()
    self.__verifycode = self._getverifycode()
    self.passwd = self._preprocess(
      self.pswd,
      self.__verifycode
    )

    logger.info("loging...")
    self._login()
    
    self.cookies = dict([(x.name,x.value) for x in self.cookieJar])
    
    urlv = "http://d.web2.qq.com/channel/login2"
    self._headers.update({"Referer":"http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"})
    status = {'status':'online','ptwebqq':self.cookies['ptwebqq'],'passwd_sig':'','clientid':self.clientid,'psessionid':'null'}
    data = {'r':json.dumps(status),
    'clientid' : self.clientid,
    'psessionid':	'null'
    }
    res = self._request(urlv,data)
    data = json.loads(res)

    self._login_info = data['result']

    self._get_info()
    
    self._poll()

  def msg_id(self): self._msgid += 1 ; return self._msgid

  def message_received(self,msg):
    if msg['retcode'] == 0:
      for i in msg['result']:
        poll_type = i['poll_type']
        data = i['value']
        if poll_type == 'message':
          from_uin = data['from_uin']
          content = data['content'][1]
          tt = threading.Thread(target=self.send_user_msg,args=(from_uin,self._botmsg(content),))
          tt.start()
          if from_uin in self._user_info:
            logger.info('[%s]:%s' % (self._get_name(from_uin),content))
          else:
            logger.info('[Somebody]:%s' % (content))
        elif poll_type == 'group_message' :
          from_uin = data['from_uin']
          groupname = self._get_name(from_uin)
          content = data['content'][1]
          send_uin = data['send_uin']
          username = self._get_name(send_uin)
          tt = threading.Thread(target=self.send_group_msg,args=(from_uin,self._botmsg(content),))
          tt.start()
          logger.info('[%s][%s]:%s' % (groupname,username,content))
        else:
          pass

  def _botmsg(self,msg): return self.bot.get_msg(msg)

  def _get_name(self,uin):
    '''<group> only,do not it use in <message>'''
    if uin in self._user_info:
      return self._user_info[uin]
    elif uin in self._group_info:
      return self._group_info[uin]
    else:
      logger.warn("can't find user's info")

  def _get_info(self):
    self._group_info = {}
    
    urlv = "http://s.web2.qq.com/api/get_user_friends2"
    status = {'h':'hello','vfwebqq':self._login_info['vfwebqq']}
    data = {'r':json.dumps(status)}
    res = self._request(urlv,data)
    data = json.loads(res)
    if data['retcode'] == 0:
      self._user_info = dict([(x['uin'],x['nick']) for x in data['result']['info']])
      logger.debug('fetch users info sucess')
    else:
      logger.error('fetch users info fail')

    urlv = "http://s.web2.qq.com/api/get_group_name_list_mask2"
    status = {"vfwebqq":self._login_info['vfwebqq']}
    data = {'r':json.dumps(status)}
    res = self._request(urlv,data)
    res = json.loads(res)
    if res['retcode']:
      logger.warn("fetch group list fail,refetch!")
      self._get_info()
    else:
      data = res['result']['gnamelist']
      for i in data:
        self._group_info.update({i['gid']:i['name']})
        urlv = "http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s&vfwebqq=%s&t=%s" % (i['code'],self._login_info['vfwebqq'],random.randrange(1345457600000,1345458000000))
        res = self._request(urlv)
        data = json.loads(res)
        self._user_info.update(dict([(x['uin'],x['nick']) for x in data['result']['minfo']]))
        logger.debug("fetch %s's users info sucess" % i['name'])

  def send_user_msg(self,uin,msg="test"):
    rmsg = "[\""+msg+"\",[\"font\",{\"name\":\"宋体\",\"size\":\"13\",\"style\":[0,0,0],\"color\":\"000000\"}]]"
    urlv = "http://d.web2.qq.com/channel/send_buddy_msg2"
    status = {'to':uin,'face':180,'content':rmsg,'msg_id':self.msg_id(),'clientid':self.clientid,"psessionid":self._login_info['psessionid']}
    data = {'r':json.dumps(status),
            'clientid': self.clientid,
            'psessionid': self._login_info['psessionid']
    }
    res = self._request(urlv,data)
    data = json.loads(res)
    if data['retcode'] == 0:
      logger.info("To [%s]-->%s" % (self._get_name(uin),msg))
    else:
      logger.warn("ReSend:%s" % msg)
      self.send_user_msg(self,uin,msg)

  def send_group_msg(self,uin=None,msg="test"):
    urlv = "http://d.web2.qq.com/channel/send_qun_msg2"
    rmsg = "[\""+msg+"\",[\"font\",{\"name\":\"宋体\",\"size\":\"13\",\"style\":[0,0,0],\"color\":\"000000\"}]]"
    status = {"group_uin":uin,"content":rmsg,"msg_id":self.msg_id(),"clientid":self.clientid,"psessionid":self._login_info['psessionid']}
    data = {'r':json.dumps(status),
            'clientid': self.clientid,
            'psessionid':self._login_info['psessionid']
    }
    res = self._request(urlv,data)
    data = json.loads(res)
    if data['retcode'] == 0:
      logger.info("To [%s]-->%s" % (self._get_name(uin),msg))
    else:
      logger.warn("ReSend:%s" % msg)
      self.send_user_msg(self,uin,msg)

if __name__ == "__main__":
  logger = logging.getLogger()
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  hdlr = logging.StreamHandler()
  hdlr.setFormatter(formatter)
  logger.addHandler(hdlr)
  logger.setLevel(logging.DEBUG)
  qq = Webqq(qq_config['user'],qq_config['passwd'])
  qq.connect()

