from gi.repository import Gtk, Gdk

from src import project
from src import tools

import string

"""
Class for manage GUI.
"""

class WindowTeXos(Gtk.Window):
    """
    The TeXos GUI
    """
    
    def __init__(self):
        """
        Initialize the main window
        """
        Gtk.Window.__init__(self, title="TeXos")
        self.set_default_size(600,400)
        self.init_menu()
        self.init_main()
        
#        builder = Gtk.Builder()
#        builder.add_from_file("src/glade/main.glade")
#        
#        #self.add(builder.get_object("box"))
#        builder.connect_signals(self)

        self.box = Gtk.VBox()
        self.box.pack_start(self.main, True, True, 0)
        
        self.add(self.box)

    def init_menu(self):
        """
        Initialize the menu
        """
        pass
    
    def init_main(self):
        """
        Initialize main container of the window
        """
        self.main = WelcomePage(on_change=self.update_page)
        
    def update_page(self,page):
        """
        Update the current shown page
        """
        self.box.remove(self.main)
        self.box.pack_end(page,True,True,0)
        self.box.show_all()
        tools.Debug("[Main window] Update Page")
#        self.remove(self.box)
#        self.add(page)
#        self.show_all()

class WelcomePage(Gtk.VBox):
    """
    Welcome Page
     Shown when no project is openend
    """
    
    def __init__(self,on_change):
        """
        Initialize Welcome Page
        """
        Gtk.VBox.__init__(self)
        
        self.on_change = on_change # When the page must leave his place to an other
        
        labelWelcom = Gtk.Label("Bienvenue sur l'interface de Teckos")
        
        buttonNew = Gtk.Button("Nouveau projet",margin=10)
        buttonNew.connect("clicked",self.on_buttonNew_clicked)
        buttonOpen = Gtk.Button("Continuer un projet",margin=10)
        
        boxButton = Gtk.HButtonBox(halign=Gtk.Align.CENTER)
        boxButton.pack_start(buttonNew,False,False,10)
        boxButton.pack_start(buttonOpen,False,False,10)
        
        self.pack_start(labelWelcom,True,False,10)
        self.pack_start(boxButton,False,False,5)
        
    def on_buttonNew_clicked(self,widget):
        new = ProjectPage(on_change=self.on_change,projectFile=None)
        self.on_change(new)
        tools.Debug("Clicked")
        
            
class ProjectPage(Gtk.HPaned):
    """
    Project Page
     Shown when a project is open
    """
    
    def __init__(self,on_change,projectFile=None):
        """
        Initialize Project Page
        """
        Gtk.HPaned.__init__(self)
        self.project = project.Project(file=projectFile)
        ### DEBUG ###
        self.project = TestProject
        ##
        
        self.leftBox = Gtk.VBox()
        self.rightBox = Gtk.Box()
        
        self.projectMenu = ProjectMenu(self.project,on_change=self.on_section_change)
        self.subMenu = ConduiteMenu(project=self.project,page=self.rightBox)
        
        self.leftBox.pack_start(self.projectMenu,False,False,0)
        self.leftBox.pack_start(self.subMenu,True,True,0)
        
        self.add1(self.leftBox)
        self.add2(self.rightBox)
        self.init_conduite_page()
        
    def on_section_change(self,section):
        tools.Debug("Change to :"+section)
        self.remove(self.rightBox)
        self.rightBox = Gtk.Box()
        self.add2(self.rightBox)
        if section == "Conduite":
            self.init_conduite_page()
        else:
            self.leftBox.remove(self.subMenu)
            self.subMenu = Gtk.VBox()
            self.leftBox.pack_end(self.subMenu,True,True,0)
            self.leftBox.show_all()
            
    def init_conduite_page(self):
        self.leftBox.remove(self.subMenu)
        self.subMenu = ConduiteMenu(project=self.project,page=self.rightBox)
        self.leftBox.pack_end(self.subMenu,True,True,0)
        self.leftBox.show_all()

class ProjectMenu(Gtk.VBox):
    """
    Main Project menu
    """
    
    def __init__(self,project,on_change):
        """
        Initialize Projet menu
        """
        Gtk.VBox.__init__(self)
        self.project = project
        self.on_change = on_change
        
        self.store = Gtk.ListStore(str)
        self.store.append(["Conduite"])
        self.store.append(["Paramètres"])
        self.store.append(["Rendu"])
        
        self.treeWidget = Gtk.TreeView(self.store)
        self.treeWidget.append_column(Gtk.TreeViewColumn("Projet", Gtk.CellRendererText(),text = 0))
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(self.treeWidget,True,True,0)
        
    def on_tree_selection_change(self, select):
        model , treeiter = select.get_selected()
        if treeiter != None :
            self.on_change(model[ treeiter ][ 0 ])
        
class ConduiteMenu(Gtk.VBox):      
    """
    Main Project menu
    """
    
    def __init__(self,project,page):
        """
        Initialize Projet menu
        """
        Gtk.VBox.__init__(self)
        self.project = project
        self.currentSection = None
        self.page = page
        self.topPart = Gtk.HPaned()
        self.sectionPart = SectionEdit(self)
        
#        label = Gtk.Label("Hello World")
#        self.sectionPart.pack_start(label,True,False,0)
        
        self.update_store()
        
        self.treeWidget = Gtk.TreeView(self.store)
        self.treeWidget.append_column(Gtk.TreeViewColumn("Conduite", Gtk.CellRendererText(),text = 0))
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(self.treeWidget,True,True,0)
        
        self.sectionMenu = Gtk.VBox()
        self.topBox = Gtk.HBox()
        
        self.page.set_property("orientation",Gtk.Orientation.VERTICAL)
        
        self.topPart.add1(self.sectionMenu)
        self.topPart.add2(self.topBox)
        
        self.page.pack_start(self.topPart,True,True,0)
        self.page.pack_start(self.sectionPart,False,False,0)
        
        self.page.show_all()
           
    def update_store(self):
        self.store = Gtk.ListStore(str,int)
        for section in self.project.conduite.get_section_list():
            self.store.append(section)
        
    def on_tree_selection_change(self, select):
        model , treeiter = select.get_selected()
        if treeiter != None :
            tools.Debug(model[ treeiter ][ 0 ] + " ID : " + str(model[ treeiter ][ 1 ]))
            self.init_section_menu(model[ treeiter ][ 1 ])
            
    def init_section_menu(self,section):
        #self.page.remove(self.sectionMenu)
        #tools.cleanBox(self.topPart)
        self.topPart.remove(self.sectionMenu)
        self.currentSection = self.project.conduite.get_section(section)
        self.sectionMenu = SectionMenu(section=self.currentSection,on_change=self.on_top_change)
        self.topPart.add1(self.sectionMenu)
        self.topPart.show_all()
        tools.Debug("Change Section")
            
    def on_top_change(self,top=None):
        self.topPart.remove(self.topBox)
        if top is not None:
            self.topBox = TopPage(top=top,parent=self)
        tools.Debug("FOCUS")
        self.topBox.grab_focus()
#        self.topBox.grab_focus()
#        self.topBox.entryTop.grab_focus()
        #self.topBox.entryTop.activate()
#        event = Gdk.Event(Gdk.EventType.BUTTON_PRESS)
#        event.window = self.topBox.entryTop.get_window()
#        event.send_event = True
#        self.topBox.entryTop.emit("button-press-event",event)
#        event2 = Gdk.Event(Gdk.EventType.FOCUS_CHANGE)
#        event2.window = self.topBox.entryTop.get_window()
#        event2.send_event = True
#        event2.in_ = True
#        self.topBox.entryTop.emit("focus-in-event",event2)
        self.topPart.add2(self.topBox)
        self.topPart.show_all()
        
   
class SectionEdit(Gtk.VBox):
    """
    Part of screen where you can edit a section
    """
    
    def __init__(self,parent):
        """
        Initialize SectionEdit
        """
        
        Gtk.VBox.__init__(self)
        self.parent = parent
        
        label = Gtk.Label("Nom de la partie")
        self.nameEntry = Gtk.Entry()
        
        self.pack_start(label,False,False,0)
        self.pack_start(self.nameEntry,False,False,0)
        
class SectionMenu(Gtk.VBox):
    """
    Main Project menu
    """
    
    def __init__(self,section,on_change):
        """
        Initialize Projet menu
        """
        Gtk.VBox.__init__(self)
        self.section = section
        self.on_change = on_change

        self.store = Gtk.ListStore(str,int)
        self.store.connect("row-changed",self.reordered)
        for top in self.section.get_top_list():
            self.store.append(top)
        
        self.treeWidget = Gtk.TreeView(self.store)
        self.treeWidget.set_reorderable(True)
        self.treeWidget.append_column(Gtk.TreeViewColumn("Top", Gtk.CellRendererText(),text = 0))
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(self.treeWidget,True,True,0)
        try:
            self.on_change(self.section.tops[0])
        except:
            pass
        
    def reordered(self,widget,tree,treeiter):
        changed_id = widget[ treeiter ][1] # Trouve l'ID de la ligne qui a bougé
        oldPos = self.section.tops.index(self.section.get_top(changed_id)) # Mémorise son ancienne position
        newPos = int(str(tree)) # Mémorise sa nouvelle position
        if(newPos < oldPos): # Rectification si sa nouvelle position viens avant son ancienne
            oldPos += 1
        self.section.tops[newPos:newPos] = [self.section.get_top(changed_id)] # Ajout de la ligne a sa nouvelle place
        self.section.tops.pop(oldPos) # Retrait de la ligne a son ancienne place
        self.update_store() # Mise a jour du treeview
             
    def on_tree_selection_change(self, select):
        model , treeiter = select.get_selected()
        if treeiter != None :
            self.on_change(self.section.get_top(model[ treeiter ][ 1 ]))
                     
    def update_store(self):
        tools.cleanBox(self)
        self.store = Gtk.ListStore(str,int)
        self.store.connect("row-changed",self.reordered)
        for top in self.section.get_top_list():
            self.store.append(top)
        self.treeWidget = Gtk.TreeView(self.store)
        self.treeWidget.set_reorderable(True)
        self.treeWidget.append_column(Gtk.TreeViewColumn("Top", Gtk.CellRendererText(),text = 0))
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(self.treeWidget,True,True,0)
        self.show_all()
        
            
class TopPage(Gtk.VBox):
    """
    Main Top Page
    """
    
    def __init__(self,top,parent):
        """
        Initialize Top Page
        """
        Gtk.VBox.__init__(self)
        self.top = top
        self.parent = parent
        self.section = parent.currentSection
        
        labelTop = Gtk.Label("Decription du top")
        self.entryTop = Gtk.Entry()
        self.entryTop.set_text(self.top.top)
        self.entryTop.connect("changed",self.on_entryTop_change)
        self.entryTop.connect("focus-in-event",self.on_focus_entry)
        
        labelAction = Gtk.Label("Action à faire")
        self.entryAction = Gtk.Entry()
        self.entryAction.set_text(self.top.action)
        self.entryAction.connect("changed",self.on_entryAction_change)
        self.entryAction.connect("key_press_event",self.on_entryAction_key_press_event)
        
        buttonLeft = Gtk.Button("Précédent")
        if self.section.is_last_top(self.top):
            self.buttonRight = Gtk.Button("Créer top suivant")
        else:
            self.buttonRight = Gtk.Button("Continuer")
            self.buttonRight.connect("clicked",self.on_continue_clicked)
        buttonBox = Gtk.HButtonBox()
        buttonBox.set_layout(Gtk.ButtonBoxStyle.EDGE)
        buttonBox.add(buttonLeft)
        buttonBox.add(self.buttonRight)
        
        buttonBox.set_focus_chain([self.buttonRight,buttonLeft])
        
        self.preview = Gtk.Label(self.top.get_latex())  
        
        self.pack_start(labelTop,False,False,0)
        self.pack_start(self.entryTop,False,False,0)
        self.pack_start(labelAction,False,False,0)
        self.pack_start(self.entryAction,False,False,0)
        self.pack_start(buttonBox,False,False,0)
        self.pack_start(self.preview,True,True,0)
        
        self.set_focus_chain([self.entryTop,self.entryAction,buttonBox,self.entryTop])
        
    def on_entryTop_change(self,widget):
        self.top.top = widget.get_text()
        self.parent.sectionMenu.update_store()
        
    def on_entryAction_change(self,widget):
        self.top.action = widget.get_text()
        self.preview.set_label(self.top.get_latex())
        self.preview.show()
        
    def on_entryAction_key_press_event(self,widget,event):
        key = Gdk.keyval_name(event.keyval)
        tools.Debug(key)
        if key == "Return":
            self.buttonRight.grab_focus()
        elif key == "parenleft": # Double les parenthèses
            buffer = widget.get_buffer()
            buffer.insert_text(widget.get_position(),")",1)
        elif key == "bracketleft": # Double les crochets
            buffer = widget.get_buffer()
            buffer.insert_text(widget.get_position(),"]",1)
        elif key == "braceleft": # Double les accolades
            buffer = widget.get_buffer()
            buffer.insert_text(widget.get_position(),"}",1)
        elif key == "BackSpace": # Remove double accolade parenthèse ou crochet
            buffer = widget.get_buffer()
            text = buffer.get_text()
            char = text[widget.get_position()-1]
            if char in ("[","{","("): 
                try:
                    if (text[widget.get_position()] == "]" and char == "[") or (text[widget.get_position()] == "}" and char == "{") or (text[widget.get_position()] == ")" and char == "("):
                        buffer.delete_text(widget.get_position(),1)
                except IndexError:
                    pass
        else: # Essai de faire sortir les lettres des parenthese ou crpchet si tapper dedans
            buffer = widget.get_buffer()
            text = buffer.get_text()
            try:
                char = text[widget.get_position()]
            except IndexError:
                    return False
            if char in ("]",")"): #Si l'on se trouve bien avant une parenthese ou crochet
                if key in string.ascii_letters:
                    buffer.insert_text(widget.get_position()+1,key,1) # Ajoute la lettre en dehors
                    widget.set_position(widget.get_position()+2) # Place le curseur après la lettre
                    return True # Arrêter le traitement de la lettre pour ne pas l'ajouter une fois de trop
                
        return False
    
    def on_continue_clicked(self,widget):
        pos = self.section.get_top_pos(self.top)
        self.parent.sectionMenu.treeWidget.set_cursor(pos+1)
        self.parent.on_top_change()
        
    def on_focus_entry(self,widget,arg):
        tools.Debug("event focus")
#        self.activate()
#        self.entryTop.set_position(2)
        
        
       
            
if __name__ == '__main__':
    TestProject = project.Project()
    prempartie = project.Section("Première partie")
    prempartie.tops.append(project.Top("10"))
    prempartie.tops.append(project.Top("20"))
    prempartie.tops.append(project.Top("30"))
    prempartie.tops.append(project.Top("40"))
    seconpartie = project.Section("Seconde partie")
    dernpartie = project.Section("Dernière partie")    
    TestProject.conduite.sections.append(prempartie)
    TestProject.conduite.sections.append(seconpartie)
    TestProject.conduite.sections.append(dernpartie)
    window = WindowTeXos ()
    window.show_all()
    Gtk.main()            
             
        
        