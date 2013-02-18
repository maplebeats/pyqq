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
import sqlite3

import sys, os
import subprocess
import platform
import time

cfg = botcfg()
gcfg = cfg[0]
fcfg = cfg[1]

class Computer:
    '''
    just for my computer
    run commands or timing to complete tasks
    Windows XP and Arch64(sudo without password)
    TODO: XP support
    '''

    def __init__(self):
        self.platform = platform.system()
        self.mods = {'shutdown':['关机', 'poweroff'], 'reboot':['重启', 'reboot'], 'timeout':['延时', 'delay', '后'], 'notify':['提醒', 'notify']}

    def run(self, con):
        '''
        check then commands and run it
        '''
        return self.notify(con)

    def commands(self, *coms):
        re = []
        for com in coms:
            r = subprocess.call(com)
            re.append(r)
            com = ' '.join(com)
            if not r:
                logger.info('run %s success' % com)
            else:
                logger.error('run %s failed(%d)' % (com, r))
        return re

    def shutdown(self):
        if self.platform == 'Linux':
            self.commands(['poweroff'])
        else:
            logger.error('Sorry, This platform did not support!')
        return True

    def reboot(self):
        if self.platform == 'Linux':
            self.commands(['reboot'])
        else:
            logger.error('Sorry, This platform did not support!')
        return True

    def settimeout(self, time, *coms):
        r = threading.Timer(time, self.command, args=(coms))
        r.start()
        return True

    def setinterval(self, com):
        '''
        how to stop this? TvT interrupterror?
        '''
        r = threading.Timer(time, self.command, args=(coms))
        r.start()
        i = threading.Timer(time, self.setinterval)
        i.start()
        return True

    def notify(self, words):
        '''
        linux only and you should have installed libnotify packge.
        '''
        return self.commands(['notify-send', '-t', '2', 'QQ' , words])


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
        self.computer = Computer()
        self.link = re.compile(r'(?:http[s]?://)?([a-z]{1,8}\.?.*\.[a-z]{2,5}[a-z/]*)', re.I)
        self.commands = ('关机', '重启', '消息', '命令', '延时', '间隔')
        self.commod = {} #command mode  TODO 多人控制模式！用字典来储存每人的mode

    def grouphandler(self, data):
        if gcfg[0]:
            content_list = data['content']
            suin = data['send_uin']
            fuin = data['from_uin']
            try:
                sname = self.ginfo[suin] 
            except KeyError: #TODO 加入新人时会产生KeyError
                self.name_info() #重新请求
                sname = self.ginfo[suin] 
            content = ''
            for i in content_list:
                if type(i) == list:
                    continue
                else:
                    content += i
            content = content.strip()
            if len(content) == 0:
                content == '表情'
            l = self.link.search(content)
            if gcfg[2] and l:
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
            try:
                fname = self.finfo[uin]
            except KeyError:
                logger.warn('[%d] has no card' % uin)
                fname = 'S.B.'
            content = ''
            for i in content_list:
                if type(i) == list:
                    continue
                else:
                    content += i
            content = content.strip()
            if len(content) == 0:
                content == 'FACE'
            l = self.link.search(content)
            if fcfg[2] and l:
                re = self.bot.reply(url=l.group(1))
            elif content == 'control' and not self.commod.get(uin):
                self.commod.update({uin:True})
                re = 'Run commands mode begin'
            elif self.commod.get(uin) and content.upper() != 'QUIT':
                r = self.computer.run(content)
                re = ''
                for i in r:
                    if i == 0:
                        re += 'commands operation success!'
                    else:
                        re += 'commands operation failed(%d)' % i

            elif content.upper() == 'QUIT' and self.commod.get(uin):
                self.commod.update({uin:False})
                re = 'Quit command mode!'
            else:
                if fcfg[1]:
                    re = self.bot.reply(content)
                else:
                    re = None
            logger.info("[F]%s:%s\n[R]:%s"%(fname, content, re))
            if re:
                re = self.send_user_msg(uin, re)
                if re != 'ok':
                    logger.error('[F][E]回复[%s]发送失败' % fname)
        else:
            pass

if __name__ == "__main__":
    from config import qqcfg
    c = qqcfg()
    try:
        qq = Qbot(c[0],c[1])
        qq.login()
    except KeyboardInterrupt:
        qq.logout()
#   print(Bot.gettitle('http://www.baidu.com'))
