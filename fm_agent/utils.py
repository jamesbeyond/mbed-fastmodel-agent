#!/usr/bin/env python
"""
mbed SDK
Copyright (c) 2011-2018 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import io
import platform
import os
import sys
import time
import socket
import logging
from functools import partial

class SimulatorError(Exception):
    """
    Simulator specific Error
    """
    pass

class FMLogger(object):
    """! Yet another logger flavour """
    def __init__(self, name, lv=logging.INFO):
        logging.basicConfig(stream=sys.stdout,format='[%(created).2f][%(name)s]%(message)s', level=lv)
        self.logger = logging.getLogger(name)
        self.format_str = '[%(logger_level)s] %(message)s'

        def __prn_log(self, logger_level, text, timestamp=None):
            self.logger.debug(self.format_str% {
                'logger_level' : logger_level,
                'message' : text,
            })

        self.prn_dbg = partial(__prn_log, self, 'DBG')
        self.prn_wrn = partial(__prn_log, self, 'WRN')
        self.prn_err = partial(__prn_log, self, 'ERR')
        self.prn_inf = partial(__prn_log, self, 'INF')
        self.prn_txt = partial(__prn_log, self, 'TXT')
        self.prn_txd = partial(__prn_log, self, 'TXD')
        self.prn_rxd = partial(__prn_log, self, 'RXD')    

def check_import():
    """ Append PVLIB_HOME to PATH, so import PyCADI fm.debug can be imported """
    if 'PVLIB_HOME' in os.environ:
        #FastModels PyCADI have different folder on different host OS
        fm_pycadi_path1 = os.path.join(os.environ['PVLIB_HOME'], 'lib', 'python27')
        fm_pycadi_path2 = os.path.join(os.environ['PVLIB_HOME'], 'lib', 'python2.7')
        if os.path.exists(fm_pycadi_path1):
            sys.path.append(fm_pycadi_path1)
        elif os.path.exists(fm_pycadi_path2):
            sys.path.append(fm_pycadi_path2)
        else:
            print "Warning: Could not locate PyCADI in PVLIB_HOME/lib/python27"
    else:
        print "Warning: PVLIB_HOME not exist, check your fastmodel installation!"

    try:
        import fm.debug
    except ImportError as e:
        print "Error: Failed to import fast models PyCADI!!!"
        return False
    else:
        return True
    
def redirect_file():
    time.sleep(1)
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    
def get_log():
    data=[]
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    os.dup2(SAVE, sys.stdout.fileno())

    tee.terminate()
    
    with open (_TEMP_STDOUT,"r") as f:
        contents = f.readlines()
        for line in contents:
            line = line.strip()
            if line == "":
                pass
            else:
                data.append(line)
    return data
    
def check_host_os():
    """ check and return the type of host operating system """
    if platform.system().startswith("Windows"):
        return"Windows"
    elif platform.system().startswith("Linux"):
        return "Linux"
    else:
        return "UNKNOWN"

def remove_comments(line):
    """remove # comments from given line """
    i = line.find("#")
    if i >= 0:
        line = line[:i]
    return line.strip()

def strip_quotes(value):
    """strip both single or double quotes"""
    value = value.strip()
    if "\"" in value:
        return value.strip("\"")
    elif "\'" in value:
        return value.strip("\'")
    else:
        return value

def boolean_filter(value):

    """ try to determine if give string match boolean type
        @return boolean if the value matches
        @return the original value if not match
    """

    value = strip_quotes(value)
    
    if value in ["TRUE","True","true","1"]:
        return True
    elif value in ["FALSE","False","false","0"]:
        return False
    else:
        return value

def find_free_port():
    """try to determine a free random port"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port

