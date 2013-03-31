from gi.repository import Gtk

class StateIcon(Gtk.Image):
    """
    Simple State Icon
    """
    
    def __init__(self,state=True,size=Gtk.IconSize.SMALL_TOOLBAR):
        """
        Initialize
        """
        Gtk.Image.__init__(self)
        self.size = size
        self.set_state(state)
        
    def set_state(self,state):
        self.state = state
        if state is True:
            self.set_from_stock(Gtk.STOCK_YES,self.size)
        elif state is False:
            self.set_from_stock(Gtk.STOCK_NO,self.size)
            
    def get_state(self):
        return self.state