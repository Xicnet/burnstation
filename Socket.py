#!/bin/env python
# -*- coding: utf-8 -*-

from ErrorsHandler import *
from socket import *

#--------------------------------------------------------------------
def socket_message(message):
    SERVER = "localhost"
    PORT = 4096
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.connect((SERVER, PORT))
    except Exception, e:
        logger.error("socket_message EXCEPTION: " + str(e))
        logger.error("socket_message: maybe burnstation_daemon is not running?")
        return

    messlen, received = sock.send(message), 0
    if messlen != len(message):
            print "Failed to send complete message"
    """
    print "Received: ",
    while received < messlen:
        data = sock.recv(1024)
        sys.stdout.write(data)
        received += len(data)
    print
    """
    sock.close()
