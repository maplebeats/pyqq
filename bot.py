#!/usr/bin/env python3
#
# Author: maplebeats
#
# gtalk/mail: maplebeats@gmail.com
#
# Last modified: 2012-08-20 17:19
#
# Filename: bot.py
#
# Description: SB机器人
#

from urllib import request,parse
from http import cookiejar
import json

class Bot:

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

  def __init__(self):
    self.cookieJar = cookiejar.CookieJar()
    self.opener = request.build_opener(request.HTTPCookieProcessor(self.cookieJar))
    self._headers = {
                   "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1",
                   "Accept-Language":"zh-cn,en;q=0.8,en-us;q=0.5,zh-hk;q=0.3",
                   "Accept-Encoding":"gzip, deflate",
                   "Referer":"http://www.simsimi.com/talk.htm"
    }
    urlv = "http://www.simsimi.com/func/req?%s" % parse.urlencode({"msg": "hi", "lc": "zh"})
    self._request(urlv)

  def get_msg(self,req):
    urlv = "http://www.simsimi.com/func/req?%s" % parse.urlencode({"msg": req, "lc": "zh"})
    res = self._request(urlv)
    if res =="{}":
      return self.get_hit()
    else:
      return json.loads(res)['response']
  
  def get_hit(self):
    urlv = "http://api.hitokoto.us/rand"
    res = request.urlopen(urlv).read().decode()
    hit = json.loads(res)
    return hit['hitokoto']
