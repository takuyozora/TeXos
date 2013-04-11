# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk#, GObject

import project
import tools
import gtkThread
#import pdf

import string
from widget import ListView, MiscWidget

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
        self.set_default_size(800,600)  
        self.set_icon_from_file("icon.svg")
        
        self.init_menu()
        self.init_main()
        
        self.box = Gtk.VBox()
        self.box.pack_start(self.main, True, True, 0)
        
        self.connect("delete-event", self.on_quit)
        
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
        #self.box.remove(self.main)
        self.main.emit("delete-event",Gdk.Event(Gdk.EventType.DELETE))
        tools.cleanBox(self.box)        
        self.main = page
        self.box.pack_end(self.main,True,True,0)
        self.box.show_all()
        tools.Debug("[Main window] Update Page")
        
    def on_quit(self,*args):
        self.main.emit("delete-event",Gdk.Event(Gdk.EventType.DELETE))
        Gtk.main_quit()

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
        
        labelWelcom = Gtk.Label()
        labelWelcom.set_markup("<big>Bienvenue sur l'interface de Teckos</big>")
        
        buttonNew = Gtk.Button("Nouveau projet",margin=10)
        buttonNew.connect("clicked",self.on_buttonNew_clicked)
        buttonOpen = Gtk.Button("Continuer un projet",margin=10)
        buttonOpen.connect("clicked",self.on_buttonOpen_clicked)
        
        boxButton = Gtk.HButtonBox(halign=Gtk.Align.CENTER)
        boxButton.pack_start(buttonNew,False,False,10)
        boxButton.pack_start(buttonOpen,False,False,10)
        
        box = Gtk.VBox()
        
        box.pack_start(labelWelcom,False,False,10)
        box.pack_start(boxButton,False,False,5)
        
        self.pack_start(box,True,False,0)
        
    def on_buttonNew_clicked(self,widget):
        new = ProjectPage(on_change=self.on_change,projectFile=None)
        self.on_change(new)
        
    def on_buttonOpen_clicked(self,widget):
        new = ProjectPage(on_change=self.on_change,projectFile=None)
        new.on_open_button_clicked(widget)
                   
class ProjectPage(Gtk.VBox):
    """
    Project Page
     Shown when a project is open
    """
    
    def __init__(self,on_change,projectFile=None):
        """
        Initialize Project Page
        """
        Gtk.HPaned.__init__(self)
        self.project = project.load_from_file(file=projectFile)
        self.on_change = on_change
        ### DEBUG ###
        #self.project = TestProject
        ##
        
        self.contentPaned = Gtk.HPaned()
        
        self.leftMenu = Gtk.VBox()
        self.rightScreenPart = Gtk.Frame()
        
        self.subMenu = Gtk.Frame()
        self.projectMenu = ProjectMenu(self.project,on_change=self.on_menu_change)
        
        self.leftMenu.pack_start(self.projectMenu,False,True,0)
        self.leftMenu.pack_start(self.subMenu,True,True,0)
        
        self.contentPaned.add1(self.leftMenu)
        self.contentPaned.add2(self.rightScreenPart)
        
        self.init_toolbar()
        
        self.pack_start(self.toolbar,False,False,2)
        self.pack_start(self.contentPaned,True,True,0)
        
        self.connect("delete-event",self.on_quit_project)
        
    def init_toolbar(self):
        self.toolbar = Gtk.Toolbar()
        
        self.toolbarItems = {}
        self.toolbarItems["new"] = Gtk.ToolButton(Gtk.STOCK_NEW)
        self.toolbarItems["new"].connect("clicked",self.on_new_button_clicked)
        
        self.toolbarItems["open"] = Gtk.ToolButton(Gtk.STOCK_OPEN)
        self.toolbarItems["open"].connect("clicked",self.on_open_button_clicked)
        
        self.toolbarItems["save"] = Gtk.ToolButton(Gtk.STOCK_SAVE)
        self.toolbarItems["save"].connect("clicked",self.on_save_button_clicked)
        
        self.toolbarItems["save_as"] = Gtk.ToolButton(Gtk.STOCK_SAVE_AS)
        self.toolbarItems["save_as"].connect("clicked",self.on_save_as_button_clicked)
        
        self.toolbarItems["compile"] = Gtk.ToolButton(Gtk.STOCK_CONVERT)
        self.toolbarItems["compile"].connect("clicked",self.on_compile_button_clicked)
        
        
        
        self.toolbar.insert(self.toolbarItems["new"],0)
        self.toolbar.insert(self.toolbarItems["open"],1)
        self.toolbar.insert(self.toolbarItems["save"],2)
        self.toolbar.insert(self.toolbarItems["save_as"],3)
        
        self.toolbar.insert(Gtk.SeparatorToolItem(),4)
        
        self.toolbar.insert(self.toolbarItems["compile"],5)
        
    def on_compile_button_clicked(self,widget):
        if self.project.tmpFile is True:
            dialog = Gtk.MessageDialog(self.get_ancestor(Gtk.WindowType.TOPLEVEL), 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "Projet non sauvegardé")
            dialog.format_secondary_text("Le projet n'a pas encore été sauvegardé, voulez vous le faire maintenant ? (dans le cas contraire la compilation aura lieu dans un dossier temporaire)")
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self.on_save_as_button_clicked(Gtk.Button()) # On redirige vers la sauvegarde
            elif response == Gtk.ResponseType.NO:
                pass
            dialog.destroy()
            
        tools.Debug("Compile..")
        task = self.project.compile_latex_to_pdf()
        #GObject.idle_add(task.next)
        dialog = Gtk.MessageDialog(Gtk.Window(), 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Compilation terminée")
        if task is True:
            dialog.format_secondary_text("La compilation de la conduite est terminée")
        else:
            dialog.format_secondary_text("La compilation de la conduite a échouée")
        dialog.run()
        dialog.destroy()
        
    def on_new_button_clicked(self,widget):
        new = ProjectPage(on_change=self.on_change,projectFile=None)
        self.on_change(new)
    
    def on_open_button_clicked(self,widget):
        dialog = Gtk.FileChooserDialog("Sélectionner un fichier", Gtk.Window(),
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file = dialog.get_filename()
            tools.Debug("File chosen : "+file)
            if project.load_from_file(file,test=True) is not False:
                new = ProjectPage(on_change=self.on_change,projectFile=file)
                self.on_change(new)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
    
    def on_save_button_clicked(self,widget):
        if self.project.tmpFile is True: # Si le projet n'a pas encore été sauvegardé
            self.on_save_as_button_clicked(widget)
        else:
            self.project.save()
            
    def on_save_as_button_clicked(self,widget):
        dialog = Gtk.FileChooserDialog("Sélectionner un fichier", Gtk.Window(),
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file = dialog.get_filename()
            tools.Debug("File chosen : "+file)
            self.project.save_as(file)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
        
    def on_quit_project(self,*args):
        tools.Debug("on quit projet ?")
        if self.project.need_save():
            dialog = Gtk.MessageDialog(self.get_ancestor(Gtk.WindowType.TOPLEVEL), 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "Projet non sauvegardé")
            dialog.format_secondary_text("Le projet a été modifié depuis sa dernière sauvegarde. Voulez vous le sauvegarder avant de quitter ?")
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                self.on_save_button_clicked(Gtk.Button()) # On redirige vers la sauvegarde
            elif response == Gtk.ResponseType.NO:
                pass
        
            dialog.destroy()
        
    def on_menu_change(self,section):
        tools.Debug("Change to :"+section)
        if section == "conduite":
            self.init_conduite_menu()
        elif section == "settings":
            self.init_setting_menu()
        elif section == "help":
            self.init_help_menu()
        else:
            self.clean_part()
            self.subMenu.show_all()
    
    def clean_part(self): # Nettoie de l'ancienne section choisie
        try:
            self.subMenu.remove(self.subMenu.get_child())
            self.rightScreenPart.remove(self.rightScreenPart.get_child())
        except TypeError: # Raise if empty
            pass
            
    def init_conduite_menu(self):
        self.clean_part()
        self.subMenu.add(ConduiteMenu(project=self.project,screen=self.rightScreenPart))
        self.subMenu.show_all()
        
    def init_help_menu(self):
        self.clean_part()
        self.subMenu.add(HelpMenu(project=self.project,screen=self.rightScreenPart))
        self.subMenu.show_all()
        
    def init_setting_menu(self):
        self.clean_part()
        self.subMenu.add(SettingMenu(project=self.project,screen=self.rightScreenPart))
        self.subMenu.show_all()

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
        
        self.menu = ListView.ListView("Projet",[["Conduite","conduite"],["Préférences","settings"],["Aide","help"]],on_select=self.on_select)
        
        self.pack_start(self.menu,False,False,0)
        
    def on_select(self, select):
        model , treeiter = select.get_selected()
        if treeiter != None :
            self.on_change(model[ treeiter ][ 1 ])
 
class RenderMenu(Gtk.VBox):
    """
    Main Render Menu (page)
    """
     
    def __init__(self,project,screen):
        """
        Initialize Render menu
        """
        Gtk.VBox.__init__(self)
        
        self.project = project
        self.screen = screen
        
        self.page = Gtk.VBox()
        
        self.store = Gtk.ListStore(str,int)
        for section in self.project.conduite.get_section_list():
            self.store.append(section)
        self.treeWidget = Gtk.TreeView(self.store)
        self.treeWidget.set_reorderable(True)
        self.treeWidget.append_column(Gtk.TreeViewColumn("Conduite", Gtk.CellRendererText(),text = 0))
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(self.treeWidget,True,True,0)
        self.show_all()
        
class SettingMenu(Gtk.VBox):
    """
    Setting Menu class
    """
    
    def __init__(self,project,screen):
        """
        Initialize Setting menu
        """
        Gtk.VBox.__init__(self)
        
        self.project = project
        self.screen = screen
        
        self.page = Gtk.Frame()
        self.menu = ListView.ListView("Préférences",[["Générales","common"]],on_select=self.on_select)
        self.screen.add(self.page)
        
        self.pack_start(self.menu,True,True,0)
        self.show_all()
        
    def on_select(self,selected):
        model , treeiter = selected.get_selected()
        if treeiter != None :
            if model[treeiter][1] == "common":
                self.init_common_settings()
                
    def clean(self): # Nettoie de l'ancienne section choisie
        try:
            self.page.remove(self.page.get_child())
        except TypeError: # Raise if empty
            pass
            
    def init_common_settings(self):
        self.clean()
        self.page.add(CommonSettings(self.project))
        self.page.show_all()
        
class CommonSettings(Gtk.VBox):
    """
        Common settings page
    """
    
    def __init__(self,project):
        """
            Initialize
        """
        Gtk.VBox.__init__(self)
        self.project = project
        
        self.compileIndexFrame = Gtk.Frame()
        self.compileIndexFrame.set_label("Compilation des indexs")
        compileIndexLabel = Gtk.Label()
        compileIndexLabel.set_markup("<b> Compiler en deux fois </b> :")
        compileIndexSwitch = Gtk.Switch()
        compileIndexSwitch.connect("notify::active",self.on_compileIndexSwitch_activate)
        compileIndexSwitch.set_active(self.project.settings.compile_index)
        compileIndexExplain= Gtk.Label("La compilation en deux fois permet d'être sur que les index seront créés. Le fichier PDF aura eonc un sommaire des parties du spectacle pour mieux se repérer. En revanche la compilation en deux fois prends plus de temps")
        compileIndexExplain.set_line_wrap(True)
        compileIndexBox = Gtk.VBox()
        compileIndexHBox = Gtk.HBox()
        
        compileIndexHBox.pack_start(compileIndexLabel,True,True,5)
        compileIndexHBox.pack_start(compileIndexSwitch,False,False,5)
        compileIndexBox.pack_start(compileIndexHBox,False,False,0)
        compileIndexBox.pack_start(compileIndexExplain,False,False,0)
        self.compileIndexFrame.add(compileIndexBox)
        
        self.checkLatexFrame = Gtk.Frame()
        self.checkLatexFrame.set_label("Vérification de la syntaxe latex")
        checkLatexLabel = Gtk.Label()
        checkLatexLabel.set_markup("<b> Vérificaction de la syntaxe </b> :")
        checkLatexSwitch = Gtk.Switch()
        checkLatexSwitch.connect("notify::active",self.on_checkLatexSwitch_activate)
        checkLatexSwitch.set_active(self.project.settings.check_latex)
        checkLatexExplain= Gtk.Label("Vérifier pour chaque top si la syntaxe est bonne, cela permet de repérer les erreurs en cas d'échec de compilation")
        checkLatexExplain.set_line_wrap(True)
        checkLatexBox = Gtk.VBox()
        checkLatexHBox = Gtk.HBox()
        
        checkLatexHBox.pack_start(checkLatexLabel,True,True,5)
        checkLatexHBox.pack_start(checkLatexSwitch,False,False,5)
        checkLatexBox.pack_start(checkLatexHBox,False,False,0)
        checkLatexBox.pack_start(checkLatexExplain,False,False,0)
        self.checkLatexFrame.add(checkLatexBox)
        
        self.pack_start(self.compileIndexFrame,False,False,5)
        self.pack_start(self.checkLatexFrame,False,False,5)
        
        #self.show_all()
        
    def on_compileIndexSwitch_activate(self,widget,*args):
        self.project.settings.compile_index = widget.get_active()
        
    def on_checkLatexSwitch_activate(self,widget,*args):
        self.project.settings.check_latex = widget.get_active()
            
        
class ConduiteMenu(Gtk.VBox):
    """
    Main Project menu
    """
    
    def __init__(self,project,screen):
        """
        Initialize Projet menu
        """
        Gtk.VBox.__init__(self)
        self.project = project

        self.page = SectionPage(project.conduite.get_first_section(),parent=self)
        self.screen = screen
        
        self.update_store()
        self.treeWidget.set_cursor(0)
    
        self.screen.add(self.page)
        self.screen.show_all()
        
    def put_delete_button(self):
        buttonDelete = Gtk.Button("Supprimer")
        buttonDelete.connect("clicked",self.on_buttonDelete_clicked)
        if len(self.project.conduite.sections) <= 1:
            buttonDelete.set_sensitive(False)
        self.pack_end(buttonDelete,False,False,0)
        
    def on_buttonDelete_clicked(self,widget):
        model , treeiter = self.treeWidget.get_selection().get_selected()
        if treeiter != None :
            toDelete = self.project.conduite.get_section(model[treeiter][1])
            index = self.project.conduite.sections.index(toDelete)
            self.project.conduite.sections.remove(toDelete)
            self.update_store()
            self.treeWidget.set_cursor(index-1)
             
        
    def reordered(self,widget,tree,treeiter):
        changed_id = widget[ treeiter ][1] # Trouve l'ID de la ligne qui a bougé
        oldPos = self.project.conduite.sections.index(self.project.conduite.get_section(changed_id)) # Mémorise son ancienne position
        newPos = int(str(tree)) # Mémorise sa nouvelle position
        if(newPos < oldPos): # Rectification si sa nouvelle position viens avant son ancienne
            oldPos += 1
        self.project.conduite.sections[newPos:newPos] = [self.project.conduite.get_section(changed_id)] # Ajout de la ligne a sa nouvelle place
        self.project.conduite.sections.pop(oldPos) # Retrait de la ligne a son ancienne place
        self.update_store() # Mise a jour du treeview
           
    def update_store(self):
        tools.cleanBox(self)
        self.store = Gtk.ListStore(str,int)
        self.store.connect("row-changed",self.reordered)
        for section in self.project.conduite.get_section_list():
            self.store.append(section)
        self.treeWidget = Gtk.TreeView(self.store)
        self.treeWidget.set_reorderable(True)
        self.treeWidget.append_column(Gtk.TreeViewColumn("Conduite", Gtk.CellRendererText(),text = 0))
        self.treeWidget.set_enable_search(False)
        self.treeWidget.set_headers_clickable(False)
        
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.treeWidget)
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(scroll,True,True,0)
        self.put_delete_button()
        self.show_all()
        self.set_size_request(120,-1) #Original width
        
    def on_tree_selection_change(self, select):
        model , treeiter = select.get_selected()
        if treeiter != None :
            tools.Debug(model[ treeiter ][ 0 ] + " ID : " + str(model[ treeiter ][ 1 ]))
            self.init_section_menu(model[ treeiter ][ 1 ])
            
    def init_section_menu(self,section):
        #self.page.remove(self.sectionMenu)
        #tools.cleanBox(self.topPart)
        section = self.project.conduite.get_section(section)
        self.page.change_section(section)
#        self.topPart.remove(self.sectionMenu)
#        self.currentSection = self.project.conduite.get_section(section)
#        self.sectionMenu = SectionMenu(section=self.currentSection,on_change=self.on_top_change)
#        self.topPart.add1(self.sectionMenu)
#        self.topPart.show_all()
        tools.Debug("Change Section")
            
    def on_top_change(self,top=None):
        self.topPart.remove(self.topBox)
        if top is not None:
            self.topBox = TopPage(top=top,parent=self)
        tools.Debug("FOCUS")
        #self.topBox.grab_focus()
        self.grab_focus()
        self.topPart.add2(self.topBox)
        self.topPart.show_all()
        
class SectionPage(Gtk.VBox):
    """
    Part of screen where you can edit section
    """
    
    def __init__(self,section,parent):
        """
        Initialize SectionPage
        """
        Gtk.VBox.__init__(self)
        
        self.section = section
        self.parent = parent
        
        self.sectionEdit = SectionEdit(section,on_change=self.parent.update_store)
        self.sectionGroup = Gtk.HPaned()
        
        self.topPage = TopPage(self,self.section.get_first_top())
        self.sectionMenu = SectionMenu(section,on_change=self.on_top_change)
        
        self.sectionGroup.add1(self.sectionMenu)
        self.sectionGroup.add2(self.topPage)
        
        self.pack_start(self.sectionEdit,False,False,0)
        self.pack_start(self.sectionGroup,True,True,0)
        
    def on_top_change(self,top):
        tools.Debug("on_top_change, top :"+str(top))
        self.topPage.clean()
        self.topPage.__init__(self, top)
        self.parent.grab_focus()
        self.topPage.show_all()
#        self.sectionGroup.remove(self.topPage)
#        self.topPage = TopPage(self,top)
#        self.sectionGroup.add2(self.topPage)
        #self.show_all()
    
    def change_section(self,section):
        self.clean()
        self.__init__(section,self.parent)
        self.show_all()
    
    def clean(self):
        tools.cleanBox(self)
   
class SectionEdit(Gtk.VBox):
    """
    Part of screen where you can edit a section name
    """
    
    def __init__(self,section,on_change):
        """
        Initialize SectionEdit
        """
        
        Gtk.VBox.__init__(self)
        self.section = section
        self.on_change = on_change
        
        box = Gtk.HBox()
        
        boxName = Gtk.VBox()
        labelName = Gtk.Label("Nom de la partie")
        self.nameEntry = Gtk.Entry()
        self.nameEntry.set_text(section.name)
        self.nameEntry.connect("changed",self.on_nameEntry_change)
        
        boxBank = Gtk.VBox()
        labelBank = Gtk.Label("Numéro de banque")
        self.bankEntry = Gtk.SpinButton()
        self.bankEntry.set_range(1,255)
        self.bankEntry.set_increments(1,1)
        self.bankEntry.set_value(section.bank)
        self.bankEntry.connect("changed",self.on_bankEntry_change)
        
        boxName.pack_start(labelName,False,False,0)
        boxName.pack_start(self.nameEntry,False,False,0)
        boxBank.pack_start(labelBank,False,False,0)
        boxBank.pack_start(self.bankEntry,False,False,0)
        
        box.pack_start(boxName,True,True,0)
        box.pack_start(boxBank,False,False,0)
        
        self.pack_start(box,False,False,0)
        
    def on_nameEntry_change(self,widget):
        self.section.name = widget.get_text()
        self.on_change()
        
    def on_bankEntry_change(self,widget):
        self.section.bank = widget.get_value_as_int()
        
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

        self.update_store()
        self.treeWidget.set_cursor(0)
        
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
        column = Gtk.TreeViewColumn("Liste des tops", Gtk.CellRendererText(),text = 0)
        self.treeWidget.append_column(column)
        self.treeWidget.set_enable_search(False)
        self.treeWidget.set_headers_clickable(False)
        
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.treeWidget)
        #tools.Debug(str(scroll.get_allocated_width()))
        #self.treeWidget.set_size_request(200,-1)
        
        select = self.treeWidget.get_selection()
        select.connect("changed",self.on_tree_selection_change)
        
        self.pack_start(scroll,True,True,0)
        self.show_all()
        self.set_size_request(180,-1) #Original width
            
                 
class TopPage(Gtk.VBox):
    """
    Main Top Page
    """
    
    def __init__(self,parent,top):
        """
        Initialize Top Page
        """
        Gtk.VBox.__init__(self)
        self.top = top
        self.parent = parent
        self.section = parent.section
        
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
        if self.parent.parent.project.settings.check_latex:
            self.imageState = MiscWidget.StateIcon()
            boxAction = Gtk.HBox()
            boxAction.pack_start(self.entryAction,True,True,0)
            boxAction.pack_start(self.imageState,False,False,0)
            self.worker = None
        else:
            boxAction = Gtk.Frame()
            boxAction.add(self.entryAction)
        
        buttonLeft = Gtk.Button("Supprimer")
        buttonLeft.connect("clicked",self.on_delete_clicked)
        if len(self.section.tops) <= 1:
            buttonLeft.set_sensitive(False)
        if self.section.is_last_top(self.top):
            self.buttonRight = Gtk.Button("Créer top suivant")
            self.buttonRight.connect("clicked",self.on_create_next_clicked)
            buttonNewSection = Gtk.Button("Créer partie suivante")
            buttonNewSection.connect("clicked",self.on_new_section_clicked)
        else:
            self.buttonRight = Gtk.Button("Continuer")
            self.buttonRight.connect("clicked",self.on_continue_clicked)
        buttonBox = Gtk.HButtonBox()
        buttonBox.set_layout(Gtk.ButtonBoxStyle.EDGE)
        buttonBox.add(buttonLeft)
        if self.section.is_last_top(self.top):
            buttonBox.add(buttonNewSection)
        buttonBox.add(self.buttonRight) 
        
        buttonBox.set_focus_chain([self.buttonRight,buttonLeft])
        
        self.preview = Gtk.Label(self.top.get_latex_preview())  
        
        self.pack_start(labelTop,False,False,0)
        self.pack_start(self.entryTop,False,False,0)
        self.pack_start(labelAction,False,False,0)
        self.pack_start(boxAction,False,False,0)
        self.pack_start(buttonBox,False,False,0)
        self.pack_start(self.preview,True,True,0)
        
        self.set_focus_chain([self.entryTop,self.entryAction,buttonBox,self.entryTop])
        
    def on_entryTop_change(self,widget):
        self.top.top = widget.get_text()
        self.parent.sectionMenu.update_store()
        
    def on_entryAction_change(self,widget):
        self.top.action = widget.get_text()
        if self.parent.parent.project.settings.check_latex:
            self.update_state()
        #self.preview.set_label(self.top.get_latex())
        self.update_preview()
        
    def update_state(self):
        if self.worker is None:
            self.worker = gtkThread.LatexCheckThread(self.top,self.imageState)
            self.worker.start()
        else:
            if self.worker.end:
                self.worker = gtkThread.LatexCheckThread(self.top,self.imageState)
                self.worker.start()
            else:
                self.worker.append(self.top)
                
    def update_preview(self):
        self.preview.set_text(self.top.get_latex_preview())
    
    def syntax_completion(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if key == "BackSpace": # Remove double accolade parenthèse guillemet ou crochet
            buffer = widget.get_buffer()
            text = buffer.get_text()
            char = text[widget.get_position()-1]
            if char in ("[","{","(","\""): 
                try:
                    if (text[widget.get_position()] == "]" and char == "[") or (text[widget.get_position()] == "}" and char == "{") or (text[widget.get_position()] == "\"" and char == "\""):
                        buffer.delete_text(widget.get_position(),1)
                except IndexError:
                    pass
        else: # Essai de faire sortir les lettres des parenthese ou crpchet si tapper dedans
            buffer = widget.get_buffer()
            text = buffer.get_text()
            jumpout = False
            try:
                char = text[widget.get_position()]
            except IndexError:
                    char = ""
            if char in ("]",")"): #Si l'on se trouve bien avant une parenthese ou crochet
                if key in string.ascii_letters:
                    buffer.insert_text(widget.get_position()+1,key,1) # Ajoute la lettre en dehors
                    widget.set_position(widget.get_position()+2) # Place le curseur après la lettre
                    return True # Arrêter le traitement de la lettre pour ne pas l'ajouter une fois de trop
                elif key in ("parenleft","bracketleft","braceleft","quotedbl"):
                    tools.Debug("Traitement d'un double délimiteur")
                    jumpout = True
#                    buffer.insert_text(widget.get_position()+1,key,1)
#                    buffer.insert_text(widget.get_position()+2,key,1)
#                    widget.set_position(widget.get_position()+2) # Place le curseur après la lettre
                    #return True # Arrêter le traitement de la lettre pour ne pas l'ajouter une fois de trop
            if key == "parenleft": # Double les parenthèses
                buffer = widget.get_buffer()
                if jumpout is True:
                    buffer.insert_text(widget.get_position()+1,"(",1)
                    buffer.insert_text(widget.get_position()+2,")",1)
                    widget.set_position(widget.get_position()+2)
                    return True
                buffer.insert_text(widget.get_position(),")",1)
            elif key == "bracketleft": # Double les crochets
                buffer = widget.get_buffer()
                if jumpout is True:
                    buffer.insert_text(widget.get_position()+1,"[",1)
                    buffer.insert_text(widget.get_position()+2,"]",1)
                    widget.set_position(widget.get_position()+2)
                    return True
                buffer.insert_text(widget.get_position(),"]",1)
            elif key == "braceleft": # Double les accolades
                buffer = widget.get_buffer()
                if jumpout is True:
                    buffer.insert_text(widget.get_position()+1,"{",1)
                    buffer.insert_text(widget.get_position()+2,"}",1)
                    widget.set_position(widget.get_position()+2)
                    return True
                buffer.insert_text(widget.get_position(),"}",1)
            elif key == "quotedbl": # Double les guillemets
                buffer = widget.get_buffer()
                if jumpout is True:
                    buffer.insert_text(widget.get_position()+1,"\"",1)
                    buffer.insert_text(widget.get_position()+2,"\"",1)
                    widget.set_position(widget.get_position()+2)
                    return True
                buffer.insert_text(widget.get_position(),"\"",1)
        return False
        
    def on_entryAction_key_press_event(self,widget,event):
        key = Gdk.keyval_name(event.keyval)
        tools.Debug(key)
        if key == "Return":
            self.buttonRight.grab_focus()
            return False
        else:
            return self.syntax_completion(widget, event)
    
    def on_continue_clicked(self,widget):
        pos = self.section.get_top_pos(self.top)
        self.parent.sectionMenu.treeWidget.set_cursor(pos+1)
        
    def on_create_next_clicked(self,widget):
        tools.Debug("create new")
        self.section.append(project.Top("Description du top"))
        self.parent.sectionMenu.update_store()
        pos = self.section.get_top_pos(self.top)
        self.parent.sectionMenu.treeWidget.set_cursor(pos+1)

    def on_new_section_clicked(self,widget):
        index = self.parent.parent.project.conduite.sections.index(self.section) +1 # On récupère l'index
        self.parent.parent.project.conduite.sections[index:index] = [project.Section("Partie")] # On insert une nouvelle partie
        self.parent.parent.update_store()
        pos = self.parent.parent.project.conduite.get_section_pos(self.section)
        self.parent.parent.treeWidget.set_cursor(pos+1)
     
    def on_delete_clicked(self,widget):
        pos = self.section.get_top_pos(self.top)
        self.section.tops.remove(self.top)
        self.parent.sectionMenu.update_store()
        if pos > 0:
            pos -= 1
        self.parent.sectionMenu.treeWidget.set_cursor(pos)
        
            
    def on_focus_entry(self,widget,arg):
        tools.Debug("event focus")
#        self.activate()
#        self.entryTop.set_position(2)

    def clean(self):
        tools.cleanBox(self)
        
class HelpMenu(Gtk.VBox):
    """
    Main Help Menu (page)
    """
     
    def __init__(self,project,screen):
        """
        Initialize Render menu
        """
        Gtk.VBox.__init__(self)
        
        self.project = project
        self.screen = screen
        
        self.page = Gtk.VBox()
        
        menu_list = [["Syntaxe","syntax"]]
        self.menu = ListView.ListView("Aide",menu_list,on_select=self.on_select)
        
        
        self.pack_start(self.menu,True,True,0)
        self.show_all()      
        
    def on_select(self, select):
        model , treeiter = select.get_selected()
        if treeiter != None :
            #self.on_change(model[ treeiter ][ 1 ])
            pass

       
            
#if __name__ == '__main__':
#    window = WindowTeXos ()
#    window.show_all()
#    Gtk.main()            
             
        
        