#!/usr/bin/env python3
# Author: maplebeats
# gtalk/mail: maplebeats@gmail.com

from urllib import request,parse
from http import cookiejar
import json
from webqq import Webqq
import re
import threading
from logger import logger
from config import botcfg
#import sqlite3
cfg = botcfg()
gcfg = cfg[0]
fcfg = cfg[1]

class Bot:

    def _request(self, url, data=None, opener=None):
        if data:
            data = parse.urlencode(data).encode('utf-8')
            rr = request.Request(url, data, self._headers)
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
        self.cfg = botcfg()

    @staticmethod
    def gettitle(url):
        """
        Can't process gzip compress
        """
        tre = re.compile(b'<title[^>]*>([^<]*)<')
        content = b''
        title = b''
        try:
            with request.urlopen(url) as r:
                for i in range(300):
                    content += r.read(64)
                    if len(content) < 64:
                        break
                    m = tre.search(content, re.IGNORECASE)
                    n = re.search(b'charset=.+?>', content, re.IGNORECASE)  #有些SB网站把charset写在后面
                    if m and n:
                        title = m.group(1)
                        break
        except:
            logger.warn('url time out')
        if content.upper().find(b'UTF-8') != -1:
            charset = 'utf-8'
        elif content.upper().find(b'GB2312') != -1 or content.upper().find(b'GBK'):
            charset = 'gbk'
        elif content.upper().find(b'BIG5') != -1:
            charset = 'big5'
        else:
            charset= 'utf-8'
        try:
            title = title.decode(charset).replace('\n', '')
            title = title.strip()
        except UnboundLocalError: #G.F.W
            title = 'G.F.W我恨你' 
        return title 

    def reply(self, req=None, url=None):
        if url:
            url = 'http://' + url
            return Bot.gettitle(url)
        else:
            return self.simi_bot(req) or self.hito_bot()

    def simi_init(self):
        simi_Jar = cookiejar.CookieJar()
        self.simi_opener = request.build_opener(request.HTTPCookieProcessor(simi_Jar))
        self._headers = {
                         "User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1",
                         "Accept-Language":"zh-cn,en;q=0.8,en-us;q=0.5,zh-hk;q=0.3",
                         "Accept-Encoding":"deflate",
                         "Referer":"http://www.simsimi.com/talk.htm"
        }
        url = "http://www.simsimi.com/func/req?%s" % parse.urlencode({"msg": "hi", "lc": "zh"})
        self._request(url=url, opener=self.simi_opener)

    def simi_bot(self, req):
        url = "http://www.simsimi.com/func/req?%s" % parse.urlencode({"msg": req, "lc": "zh"})
        res = self._request(url, opener=self.simi_opener)
        if res == "{}":
            return False
        else:
            return json.loads(res)['response']

    def hito_bot(self):
        url = "http://api.hitokoto.us/rand"
        res = request.urlopen(url).read().decode()
        hit = json.loads(res)
        return hit['hitokoto']


class Qbot(Webqq):

    def __init__(self, qq, ps):
        super(Qbot, self).__init__(qq, ps)
        self.bot = Bot()
        self.link = re.compile(r'(?:http[s]?://)?(.*\.\w{2,5}[\w/]*)', re.I)

    def grouphandler(self, data):
        if gcfg[0]:
            content_list = data['content']
            suin = data['send_uin']
            fuin = data['from_uin']
            try:
                sname = self.ginfo[suin] 
            except KeyError: #TODO 加入新人时会产生KeyError
                self.name_info #重新请求
            content = ''
            for i in content_list:
                if type(i) == list:
                    continue
                else:
                    content += i
            content = content.strip()
            if len(content) == 0:
                content == '表情'
            if gcfg[2]:
                l = self.link.search(content)
                re = self.bot.reply(url=l.group(1))
                re = "@%s Title:%s" % (sname, re)
            else:
                if gcfg[1]:
                    re = self.bot.reply(content)
                else:
                    re = None
            logger.info("[G]<%s>[%s]:%s\n[R]:%s"%(self.group[fuin], sname, content, re)) 
            if re:
                re = self.send_group_msg(fuin, re)
                if re != 'ok':
                    logger.error('[G][E]回复[%s]发送失败' % sname)
        else:
            pass

    def userhandler(self, data):
        if fcfg[0]:
            content_list = data['content']
            uin = data['from_uin']
            content = ''
            for i in content_list:
                if type(i) == list:
                    continue
                else:
                    content += i
            content = content.strip()
            if len(content) == 0:
                content == '表情'
            if fcfg[2]:
                l = self.link.search(content)
                re = self.bot.reply(url=l.group(1))
            else:
                if fcfg[1]:
                    re = self.bot.reply(content)
                else:
                    re = None
            logger.info("[F]%s:%s\n[R]:%s"%(self.finfo[uin], content, re))
            if re:
                re = self.send_user_msg(uin, re)
                if re != 'ok':
                    logger.error('[F][E]回复[%s]发送失败' % self.finfo[suin])
        else:
            pass

if __name__ == "__main__":
    from config import qqcfg
    c = qqcfg()
    qq = Qbot(c[0],c[1])
    qq.login()
#   print(Bot.gettitle('http://www.baidu.com'))
