#!/usr/bin/env python3
# Author: maplebeats
# gtalk/mail: maplebeats@gmail.com

from qqlogin import QQlogin, COOKIE
import os
import json
from logger import logger
import pickle
import random
import threading

class Webqq(QQlogin):

    def __init__(self, qq, pw):
        super(Webqq, self).__init__(qq, pw) 
        self.msgid = 60000000
        self.clientid = "4646111"
        self.cookies = {} 
        self._login_info = {}
    
    def login(self):
        logger.info('login...')
        if os.path.isfile(COOKIE): 
            self.cookieJar.load(ignore_discard=True, ignore_expires=True)
        else:
            self._verifycode = self._getverifycode()
            self.pswd = self._preprocess(self._pw, self._verifycode)
            self._headers.update({"Referer":"http://ui.ptlogin2.qq.com/cgi-bin/login?target=self&style=5&mibao_css=m_webqq&appid={0}&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fweb.qq.com%2Floginproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20121029001".format(self.appid)})
            url = "http://ptlogin2.qq.com/login?u={0}&p={1}&verifycode={2}&aid={3}&u1=http%3A%2F%2Fweb.qq.com%2Floginproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&h=1&ptredirect=0&ptlang=2052&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=3-25-30079&mibao_css=m_webqq&t=1&g=1".format(self.qq, self.pswd, self._verifycode[1], self.appid)
            res = self._request(url=url, cookie=True)
            if res.find("成功") != -1:
                pass
            elif res.find("验证码") != -1:
                print("验证码错误")
                self._getverifycode()
                self.login()
            else:
                logger.error(res)
                raise Exception("登陆错误")
        self.cookies.update(dict([(x.name,x.value) for x in self.cookieJar]))
        tmp = self.get_login_info()
        logger.debug(tmp)
        if os.path.isfile(COOKIE) and tmp: #cookie timeout
            self._login_info.update(tmp)
            self.name_info()
            self.__poll()
        else:
            self.login()

    def name_info(self):
        logger.info('Fetching info')
        g = self.get_group_info()
        u = self.get_user_info()
        self.group = g[0]
        self.ginfo = {}
        for i in g[1]:
            self.ginfo.update(dict(((x['uin'],x['nick']) for x in i['minfo'])))
            try:
                self.ginfo.update(dict([(x['muin'],x['card']) for x in i['cards']]))
            except KeyError:
                logger.warn('This group have no card')
        self.finfo = dict(((x['uin'],x['nick']) for x in u['info']))
        try:
            self.finfo.update(dict([(x['uin'],x['markname']) for x in u['marknames']]))
        except KeyError:
            logger.warn('You do not have no markname')

    def get_login_info(self):
        INFO = 'info' #TODO this file is not necessary now,we can use logout method to avoid it.
        url = "http://d.web2.qq.com/channel/login2"
        self._headers.update({"Referer":"http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"})
        status = {'status':'online',
            'ptwebqq':self.cookies['ptwebqq'],
            'passwd_sig':'',
            'clientid':self.clientid,
            'psessionid':'null'
            }
        data = {'r':json.dumps(status),
            'clientid' : self.clientid,
            'psessionid':'null'
            }
        res = self._request(url, data)
        if res:
            with open(INFO, 'wb') as i:
                pickle.dump(res, i)
            return res
        else:
            with open(INFO, 'rb') as i:
                tmp = pickle.load(i)
                if len(tmp) > 2: #fix 103 code
                    return tmp
                else:
                    raise Exception("INFO is wrong")
            

    def get_user_info(self):
        url = "http://s.web2.qq.com/api/get_user_friends2"
        status = {'h':'hello',
            'vfwebqq':self._login_info['vfwebqq']
            }
        data = {'r':json.dumps(status)}
        res = self._request(url, data)
        return res

    def get_group_info(self):
        url = "http://s.web2.qq.com/api/get_group_name_list_mask2"
        status = {"vfwebqq":self._login_info['vfwebqq']}
        data = {'r':json.dumps(status)}
        res = self._request(url, data)
        ginfo = {}
        info = []
        for i in res['gnamelist']:
            ginfo.update({i['gid']:i['name']})
            url = "http://s.web2.qq.com/api/get_group_info_ext2?gcode={0}&vfwebqq={1}&t={2}".format(i['code'], self._login_info['vfwebqq'], random.randrange(1345457600000,1345458000000))
            res = self._request(url)
            info.append(res)
        return ginfo, info

    def __poll(self):
        while True:
            url = "http://d.web2.qq.com/channel/poll2"
            self._headers.update({"Referer":"http://d.web2.qq.com/proxy.html?v=20110331002&callback=1&id=2"})
            status = {'clientid':self.clientid,
                'psessionid':self._login_info['psessionid'] 
                }
            data = {'r':json.dumps(status),
                'clientid' : self.clientid,
                'psessionid':'null'
                }
            res = self._request(url=url, data=data)
            if res:
                threading.Thread(target=self.__pollhandler, args=(res,)).start()
    
    def __pollhandler(self, data):
        for i in data:
            if i:
                pt = i['poll_type']
                va = i['value']
                if pt == 'message':
                    self.userhandler(va)
                elif pt == 'group_message':
                    self.grouphandler(va)
                elif pt == 'ptwebqq': #TODO update cookie's file value
                    self.cookie.update({'ptwebqq':i['p']})
                elif pt == 'buddies_status_change':
                    pass #TODO
                elif pt == 'kick_message':
                    os.remove(COOKIE)
                    raise Exception("被下线")
                else:
                    pass

    def grouphandler(self, data):
        self.send_group_msg(data['from_uin'])

    def userhandler(self, data):
        self.send_user_msg(data['from_uin'])

    def msg_id(self):
        self.msgid += 1
        return self.msgid

    def send_user_msg(self, uin=None, msg="send user msg"):
        rmsg = '["'+msg+'",["font",{"name":"宋体","size":"13","style":[0,0,0],"color":"000000"}]]'
        url = "http://d.web2.qq.com/channel/send_buddy_msg2"
        status = {'to':uin,
            'face':180,
            'content':rmsg,
            'msg_id':self.msg_id(),
            'clientid':self.clientid,
            "psessionid":self._login_info['psessionid']
            }
        data = {'r':json.dumps(status),
            'clientid': self.clientid,
            'psessionid': self._login_info['psessionid']
        }
        res = self._request(url, data)
        return res

    def send_group_msg(self, uin=None, msg="send group msg"):
        rmsg = '["'+msg+'",["font",{"name":"宋体","size":"13","style":[0,0,0],"color":"000000"}]]'
        url = "http://d.web2.qq.com/channel/send_qun_msg2"
        status = {"group_uin":uin,
            "content":rmsg,
            "msg_id":self.msg_id(),
            "clientid":self.clientid,
            "psessionid":self._login_info['psessionid']
            }
        data = {'r':json.dumps(status),
            'clientid': self.clientid,
            'psessionid':self._login_info['psessionid']
        }
        res = self._request(url, data)
        return res

    def logout(self):
        url =  'http://d.web2.qq.com/channel/logout2?ids&clientid={0}&psessionid={1}&t={2}'.format(self.clientid, self._login_info['psessionid'], random.randrange(1345457600000,1345458000000))
        res = self._request(url)
        if res == 'ok':
            logger.info('logout success!')
            return True
        else:
            logger.error('logout failed!')
            return False

    def __del__(self):
        self.logout()

if __name__ == "__main__":
    from config import qqcfg
    c = qqcfg()
    qq = Webqq(c[0],c[1])
    qq.login()
