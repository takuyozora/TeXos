# -*- coding: utf-8 -*-

#from gi.repository import Gtk
from uuid import uuid4 # Create unique ID


class LogLevel:
    """
        Define the log level
    """
       
    def __init__(self,log_level,log_name,log_prompt=None):
        """
            Initialize LogLevel
        """
        self.level = log_level
        self.name = log_name
        self.prompt = log_prompt
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name

ACTIVE_LOG = True
PROMPT_LOG = True
MAX_LOG_LEVEL = 0 
LOG_FILE_PATH = "/tmp/log_texos.log"
LOG_DEFAULT = LogLevel(10,"default")
LOG_MAIN = LogLevel(20,"main")
LOG_THREAD = LogLevel(30,"thread",log_prompt=False)
LOG_GUI = LogLevel(30,"gui",log_prompt=False)

def unique_id():
    return int(str(uuid4().int)[:9]) ### Trouver mieux que un aléatoir tronqué à 10 ###

def Debug(msg):
    """
     Print a msg if debug mode is on 
    """
    print(msg)
    
def cleanBox(box):
    children = box.get_children()
    for child in children:
        #child.unparent()
        box.remove(child)
    #Debug("Clean box : "+str(box))
   
def init_log():
    with open(LOG_FILE_PATH,"w"):
        pass 
    
def log(msg,log_type=LOG_DEFAULT,class_type=None,optional_type=None):
    """
        Permet de rédiger un fichier log 
    """
#    try:
#        global LOG_FILE_INIT
#    except NameError:
#        LOG_FILE_INIT = None
#        global LOG_FILE_INIT
#        LOG_FILE_INIT = False
    
    if ACTIVE_LOG is not True:
        return None
    elif MAX_LOG_LEVEL != 0 and MAX_LOG_LEVEL > log_type.level:
        return None
    
    log_msg = "["+str(log_type)+"]"
    if class_type is not None:
        log_msg += "["+class_type.__class__.__name__+"]" 
    if optional_type is not None:
        log_msg += "["+optional_type+"]" 
    log_msg += " "+msg    
    
    if PROMPT_LOG and log_type.prompt is not False:
        Debug(log_msg)
    
#    if LOG_FILE_INIT is not True:
#        LOG_FILE_INIT = True
#        mode = "w"
#    else:
#        mode = "a"
    mode = "a"
    
    with open(LOG_FILE_PATH,mode) as f:
        f.write(log_msg+"\n")
        return True
    return False