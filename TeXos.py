#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Launch the main windows of TeXos
"""

from gi.repository import Gtk
# Add the "src" directory to the python path 
from sys import path as PYTHONPATH
from os import getcwd, path
PYTHONPATH.append(path.join(getcwd(),"src"))
# --
from src import gui

if __name__ == '__main__':
    window = gui.WindowTeXos ()
    window.show_all()
    Gtk.main()
