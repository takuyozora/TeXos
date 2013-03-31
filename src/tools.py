# -*- coding: utf-8 -*-

from gi.repository import Gtk
from uuid import uuid4 # Create unique ID

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