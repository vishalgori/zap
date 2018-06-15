#!/usr/bin/python2.7
from zapv2 import *
import argparse
import socket
import subprocess
import time
import os, sys
import logging

class Session_Handling:
    def __init__(self):
        pass

    def enable_session_handling(self, log_file_name, config):
        # Configure logging.
        logging.basicConfig(filename=log_file_name, level=logging.DEBUG)
        logging.info("Session handling method called.")

        zapip = config['ZAP'][0]['zapip']
        zapport = config['ZAP'][1]['zapport']
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if zapip or zapport is None:
            result = sock.connect_ex(('0.0.0.0', 8080))
            if result != 0:
                logging.debug("ZAP not running. Starting ZAP service now on localhost.")
                try:
                    subprocess.Popen(['/zap/zap.sh', '-daemon'],
                                 stdout=open(os.devnull, 'w'))
                except:
                    logging.critical("Zap script not found at /zap/zap.sh. " + str(sys.exc_info()[0]))
                    raise
                logging.debug('Waiting for ZAP to load, 10 seconds ...')
                time.sleep(10)
            else:
                logging.debug("Found ZAP running on http://0.0.0.0:8080")
        else:
            result = sock.connect_ex((zapip, zapport))
            logging.debug("Connecting to zap on " + str(zapip) + ":" + str(zapport) + " Result: " + result)
            if result != 0:
                logging.critical("No zap server found on " + zapip + ":" + zapport)
                raise

        # Enabling session handling in ZAP.
        zap = ZAPv2()
        result = zap.core.set_option_http_state_enabled(True)
        logging.debug("Auto session handling enabled: " + result)
        return "Auto session handling enabled."
