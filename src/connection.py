# Copyright 2010-2011 Florent Le Coz <louiz@louiz.org>
#
# This file is part of Poezio.
#
# Poezio is free software: you can redistribute it and/or modify
# it under the terms of the zlib license. See the COPYING file.

"""
Defines the Connection class
"""

import logging
log = logging.getLogger(__name__)

from gettext import (bindtextdomain, textdomain, bind_textdomain_codeset,
                     gettext as _)

import getpass
import sleekxmpp

from config import config
from logger import logger
import common

class Connection(sleekxmpp.ClientXMPP):
    """
    Receives everything from Jabber and emits the
    appropriate signals
    """
    __init = False
    def __init__(self):
        resource = config.get('resource', '')
        if config.get('jid', ''):
            self.anon = False # Field used to know if we are anonymous or not.
            # many features will be handled diferently
            # depending on this setting
            jid = '%s/%s' % (config.get('jid', ''), resource)
            password = config.get('password', '') or getpass.getpass()
        else: # anonymous auth
            self.anon = True
            jid = '%s/%s' % (config.get('server', 'anon.louiz.org'), resource)
            password = None
        sleekxmpp.ClientXMPP.__init__(self, jid, password, ssl=True)
        self.auto_reconnect = False
        self.auto_authorize = None
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0004')
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0060')
        self.register_plugin('xep_0071')
        self.register_plugin('xep_0085')
        if config.get('send_poezio_info', 'true') == 'true':
            info = {'name':'poezio',
                    'version':'0.7.2-dev'}
            if config.get('send_os_info', 'true') == 'true':
                info['os'] = common.get_os_info()
            self.register_plugin('xep_0092', pconfig=info)
        if config.get('send_time', 'true') == 'true':
            self.register_plugin('xep_0202')

    def start(self):
        # TODO, try multiple servers
        # With anon auth.
        # (domain, config.get('port', 5222))
        custom_host = config.get('custom_host', '')
        custom_port = config.get('custom_port', -1)
        if custom_host and custom_port != -1:
            res = self.connect((custom_host, custom_port), reattempt=False)
        else:
            res = self.connect(reattempt=False)
        if not res:
            return False
        self.process(threaded=True)
        return True
