#/usr/bin/env python3

from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

def qqcfg():
    qq = config.get('account', 'qq')
    pw = config.get('account', 'pw')
    return (qq, pw)

def botcfg():
    genable = config.getboolean('gbot', 'enable')
    gauto = config.getboolean('gbot', 'auto')
    gurl = config.getboolean('gbot', 'url')
    fenable = config.getboolean('fbot', 'enable')
    fauto = config.getboolean('fbot', 'auto')
    furl = config.getboolean('fbot', 'url')
    return ((genable, gauto, gurl),(fenable, fauto, furl))

def decfg():
    return config.getboolean('debug', 'enable')
