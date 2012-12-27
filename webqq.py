#!/usr/bin/env python3

from qqlogin import QQlogin
import logging

COOKIEFILE="cookie"

logger = logging.getLogger()
formatter = logging.Formatter('%(levelname)s %(message)s')
hdlr = logging.StreamHandler()
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)

class Webqq(QQlogin):

    def __init__(self, qq, pw):
        super(Webqq, self).__init__(qq,pw) ##is that true?
        self.msgid = 60000000
        self.cookies={} #{k:v}
    
    def login(self):
        url = "http://ptlogin2.qq.com/login?u=%s&p=%s&verifycode=%s&aid=%s"%(self.qq,self.__pw,self._verifycode[1],self.appid)\
        + "&u1=http%3A%2F%2Fweb.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=3-25-30079&mibao_css=m_webqq&t=1&g=1"
        self._headers.update({"Referer":"http://ui.ptlogin2.qq.com/cgi-bin/login?target=self&style=5&mibao_css=m_webqq&appid=%s"%(self.appid)+"&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fweb.qq.com%2Floginproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20121029001"}) #todo
        if os.path.isfile(COOKIE): #use saved cookie
            self.cookieJar.load(COOKIE)
        else:
            res = self._request(url=url, cookie=True)
            if res.find("登陆成功") != -1:
                logger.debug(res)
            elif res.find("验证码不正确") != -1:
                logger.error("验证码错误")
                self._getverifycode()
                self.login()
            else:
                logger.error(res)
        self.cookies.update(dict([(x.name,x.value) for x in self.cookieJar]))

    def __poll(self):
        url = "http://d.web2.qq.com/channel/poll2"
        self._headers.update({"Referer":"http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"})
        pass
