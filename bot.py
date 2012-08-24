#!/usr/bin/env python3
#
# Author: maplebeats
#
# gtalk/mail: maplebeats@gmail.com
#
# Last modified:	2012-08-23 18:41
#
# Filename:		bot.py
#
# Description: SB机器人
#

from urllib import request,parse
from http import cookiejar
import json

import re

import sqlite3

class Bot:

  def _request(self, url, data=None, opener=None):
    if data:
      data = parse.urlencode(data).encode('utf-8')
      rr = request.Request(url,data,self._headers)
    else:
      rr = request.Request(url=url, headers=self._headers)
    with opener.open(rr) as fp:
      try:
        res = fp.read().decode('utf-8')
      except:
        res = fp.read()
    return res

  def __init__(self):
    self.simi_init()
    self.link = re.compile(r'[http://|\w*\.]?.*\.\w{2,4}[^\w]+')
  
  def reply(self,req):
    l = self.link.search(req)
    if l:
      return l.group(0)
    else:
      return self.simi_bot(req) or self.hito_bot()

  @staticmethod
  def gettitle(link):
    pass

  def simi_init(self):
    simi_Jar = cookiejar.CookieJar()
    self.simi_opener = request.build_opener(request.HTTPCookieProcessor(simi_Jar))
    self._headers = {
                   "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1",
                   "Accept-Language":"zh-cn,en;q=0.8,en-us;q=0.5,zh-hk;q=0.3",
                   "Accept-Encoding":"deflate",
                   "Referer":"http://www.simsimi.com/talk.htm"
    }
    urlv = "http://www.simsimi.com/func/req?%s" % parse.urlencode({"msg": "hi", "lc": "zh"})
    self._request(url=urlv,opener=self.simi_opener)

  def simi_bot(self,req):
    urlv = "http://www.simsimi.com/func/req?%s" % parse.urlencode({"msg": req, "lc": "zh"})
    res = self._request(urlv,opener=self.simi_opener)
    if res =="{}":
      return False
    else:
      return json.loads(res)['response']
  
  def hito_bot(self):
    urlv = "http://api.hitokoto.us/rand"
    res = request.urlopen(urlv).read().decode()
    hit = json.loads(res)
    return hit['hitokoto']
