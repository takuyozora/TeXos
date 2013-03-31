# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, Poppler


class PdfView(Gtk.Frame):
    
    def __init__(self,uri):
        Gtk.Frame.__init__(self)
        self.document = Poppler.Document.new_from_file(uri, None)
        self.page = self.document.get_page(0)
        
        self.connect("draw",self.draw)
        self.set_app_paintable(True)
        
    def draw(self,widget,surface):
        self.page.render(surface)
        
    def init_iter(self):
        self.indexer = Poppler.IndexIter.new(self.document)
        self.walk_iter(self.indexer)
            
    def walk_iter(self,iter):
        while True:
            child = Poppler.IndexIter.get_child(iter)
            action = Poppler.IndexIter.get_action(iter)
            print(action.named.title)
            print(action.goto_dest.dest.page_num)
            dest = self.document.find_dest(action.named.title)
            self.structure.append([])
            if not Poppler.IndexIter.next(iter):
                break