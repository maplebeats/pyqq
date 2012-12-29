#/usr/bin/env python3

from configparser import ConfigParser

def getconfig():
    cfg = {}
    config = ConfigParser()
    config.read("config.ini")
    qq = config.get('account','qq')
    pw = config.get('account','pw')
    return (qq,pw)
