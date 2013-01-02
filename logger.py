#!/usr/bin/env python3
# Author: maplebeats
# gtalk/mail: maplebeats@gmail.com

import logging

logger = logging.getLogger()
FORMAT = '%(levelname)s %(module)s %(message)s'
formatter = logging.Formatter(FORMAT)
hdlr = logging.StreamHandler()
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)
