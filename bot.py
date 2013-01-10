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
#import sqlite3

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

    @staticmethod
    def gettitle(url):
        """
        need rewrite
        """
        title = re.compile(b'<title>(.*)</title>')
        r = request.urlopen(url).read(1024)
        if r.find(b'utf-8') != -1:
            de = 'utf-8'
        else:
            de = 'gbk'
        t = title.findall(r)
        if t:
            t = t[0]
            try:
                return t.decode(de)
            except:
                if de == 'gbk':
                    return t.decode('utf-8')
                else:
                    return t.decode('gbk')
        else:
            return "this page didn't have title"

    def reply(self, req):
        link = re.compile(r'(?:http[s]?://)?.*\.\w{2,5}[\w/]*', re.I)
        l = link.findall(req)
        if l:
            u = []
            for i in l:
                if i.find('http') == -1:
                    i = 'http://' + i
                u.append(Bot.gettitle(i))
            return u[0].strip()
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
        """
        req could not have % ...
        """
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

    def grouphandler(self, data):
        content_list = data['content']
        content = ''
        for i in content:
            if type(i) == list:
                continue
            else:
                content += i
        content = content.strip()
        if len(content) == 0:
            content == '表情'
        re = self.bot.reply(content)
        if re:
            self.send_group_msg(data['from_uin'], re)
        logger.info("IN:%s\nreply group:%s"%(content, re))

    def userhandler(self, data):
        content_list = data['content']
        content = ''
        for i in content:
            if type(i) == list:
                continue
            else:
                content += i
        content = content.strip()
        if len(content) == 0:
            content == '表情'
        re = self.bot.reply(content)
        if re:
            self.send_user_msg(data['from_uin'], re)
        logger.info("IN:%s\nreply user:%s"%(content, re))

if __name__ == "__main__":
    from config import qqcfg
    c = qqcfg()
    qq = Qbot(c[0],c[1])
    qq.login()
    #print(Bot.gettitle('http://www.qq.com'))
