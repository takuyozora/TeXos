#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Launch the main windows of TeXos
"""

from gi.repository import Gtk
from src import gui

if __name__ == '__main__':
    window = gui.WindowTeXos ()
    window.show_all()
    Gtk.main()