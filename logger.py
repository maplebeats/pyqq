#!/usr/bin/env python3
# Author: maplebeats
# gtalk/mail: maplebeats@gmail.com

import logging
from config import decfg

cfg = decfg()

logger = logging.getLogger()
logging.basicConfig(filename='qq.log')

if cfg:
    FORMAT = '%(levelname)s %(module)s %(message)s'
    logger.setLevel(logging.DEBUG)
else:
    FORMAT = '%(message)s'
    logger.setLevel(logging.INFO)
hdlr = logging.StreamHandler()
formatter = logging.Formatter(FORMAT)
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
