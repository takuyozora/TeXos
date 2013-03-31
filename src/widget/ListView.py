from gi.repository import Gtk

class ListView(Gtk.Frame):
    """
        Custom TreeView Widget
    """
    
    def __init__(self,title,elems,types=None,on_select=None,create_list=None):
        """
            Initialize
        """
        
        Gtk.Frame.__init__(self)
        
        self.on_select = on_select
        self._elems = elems
        self.types = types
        
        if on_select is not None:
            self.on_select = on_select
        else:
            self.on_select = self._default_on_select
        if create_list is not None:
            self.create_list = create_list
        else:
            self.create_list = self._default_create_list
            
        self.create_store()
        self.tree = Gtk.TreeView(self.store)
        self.tree.append_column(Gtk.TreeViewColumn(title, Gtk.CellRendererText(),text = 0))
        
        select = self.tree.get_selection()
        select.connect("changed",self.on_select)
        
        self.add(self.tree)
        self.show_all()
        self.tree.set_cursor(0)
        
    def create_store(self):
        self.create_list()
        self.store = Gtk.ListStore(*self.identify_type())
        for elem in self.elems:
            self.store.append(elem)
        
    def identify_type(self):
        if self.types is not None:
            return self.types # Si les types on été prédéfinis
        types = []
        for elem in self.elems[0]: # On cherches les types de la première série d'éléments
            types.append(type(elem))
        return types
    
    def _default_create_list(self):
        self.elems = self._elems
        
    def _default_on_select(self,selected):
        model , treeiter = selected.get_selected()
        if treeiter != None :
            print(model[ treeiter ])

class ListViewScrolled(Gtk.ScrolledWindow, ListView):
    """
        Custom TreeView Widget Scrolled
    """
    
    def __init__(self,*args,**kwargs):
        """
            Initialize
        """
        Gtk.ScrolledWindow.__init__(self)
        ListView.__init__(self,*args,**kwargs)
        
        self.tree.reparent(self)
        self.show_all()
    
if __name__ == '__main__':
    elems = [ ["1",1], ["2",1], ["4",3]]
    window = Gtk.Window()
    tree = ListView("Tops",elems)
    window.add(tree)
    window.show_all()
    
    Gtk.main()