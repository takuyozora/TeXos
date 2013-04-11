# -*- coding: utf-8 -*-

import tools
import latex

import copy
import pickle
import subprocess
import ntpath
import time
import shlex
from os import path

PROJECT_ARCHITECTURE_VERSION = 1.0



def load_from_file(file,test=False):
    if type(file) == str:
        with open(file,'rb') as f:
            try:
                obj = pickle.load(f)
                tools.Debug("Open succesfull")
                obj.file = file # Important de mettre a jour le chemin du fichier
                obj.make_copy()
                return obj
            except pickle.UnpicklingError:
                return False
    if test is False:
        return Project()
    else:
        return False

class Project():
    """
    Main class of a Project
    """
    
    def __init__(self,file=None):
        """
        Initialize Project
        """
        if file is not None: # If open an existing project
            self.file = file
            result = self.load_from_file(self.file)
            if result is not False:
                self = result
                self.file = file # Important de mettre a jour la destination du fichier source
                return None
        else: # Create an empty project
            self.name = "Nouveau Projet"
            self.file = "/tmp/"+str(tools.unique_id())+".texos" # WINDOWS : il faut corriger ça !
            self.tmpFile = True
            self.settings = ProjectSetting()
            self.conduite = Conduite()
            self.version = PROJECT_ARCHITECTURE_VERSION
            self.make_copy() # In order to check if it was modified
    
    def make_copy(self):
        self.last_copy = copy.deepcopy(self)
        self.last_copy.last_copy = None
            
    def save_as(self,file):
        tmp = self.file
        self.file = file
        if self.save() is not True:
            self.file = tmp
            tools.Debug("Erreur lors de la sauvegarde")
    
    def need_save(self): # Retourne vrai si le projet doit être sauvegardé
        #return (self != self.last_copy or self.tmpFile is True)
        return self != self.last_copy
            
    def save(self):
        if self.need_save():
            with open(self.file,"wb") as f:
                self.tmpFile = False
                pickle.dump(self, f)
                self.make_copy()
                tools.Debug("Save succesfull")
                return True
        else:
            tools.Debug("No need to save")
        
    def compile_latex_to_pdf(self): # Necessite 2 compilation pour obtenir l'index des pages
        latex = self.conduite.compile_all()
        #yield True
        
        if self.settings.compile_index:
            n_compile = 2
        else:
            n_compile = 1
        
        filepath,filename = ntpath.split(self.file)
        name = ".".join(filename.split(".")[:-1])
        absolut = path.join(filepath,name)
        with open(absolut+".tex", "w") as f:  ## Améliorer le / par un os.path
            f.write(latex)
        cmd = "/usr/bin/pdflatex -halt-on-error -output-directory=%(dir)s %(name)s.tex" % {"name": "\""+absolut+"\"", "dir": filepath}
        args = shlex.split(cmd)
        succes = None
        for i in range(n_compile):
            succes = self._compile(args) is True and succes is not False
            
        return succes
        #yield False
        
    def _compile(self,args):
        p = subprocess.Popen(args,stdout=subprocess.PIPE)
        while p.poll() is None:
            tools.Debug("Currently compiling ...")            
            #yield True
            time.sleep(0.1)
        tools.Debug("Compile end !")
        return p.wait() == 0
    
    def __eq__(self,other):
        tmp = self.last_copy
        self.last_copy= None
        #other.last_copy = tmp
        tools.Debug(other.__dict__)
        tools.Debug(self.__dict__)
        eq = (self.__dict__ == other.__dict__) # Compare les attributs de l'objet avec un autre
        self.last_copy = tmp
        return eq
    
class Conduite():
    """
    Main class of a conduite
    """
    
    def __init__(self):
        """
        Initialize conduite
        """
        self.sections = list()
    
    def get_section(self,sectionId):
        for section in self.sections:
            if section.id == sectionId:
                return section
        raise NameError("ID doesn't find in the section list")
    
    def get_section_list(self):
        for section in self.sections:
            yield [section.name,section.id]
            
    def get_first_section(self):
        try:
            return self.sections[0]
        except IndexError:
            self.sections.append(Section("Partie"))
            return self.get_first_section()
    
    def get_section_pos(self,section):
        return self.sections.index(section)
    
    def compile_all(self):
        return latex.compile_conduite(self)
    
    def compile_section(self,section=None):
        if section is None:
            result = ""
            for section in self.sections:
                result += "\n" + self.compile_section(section)
            return result
                
        before = self.sections.index(section)-1
        if before < 0:
            before = ["",0]
        else:
            before = [self.sections[before].name,self.sections[before].bank]
        after = self.sections.index(section)+1
        if after >= len(self.sections):
            after = ["",0]
        else:
            after = [self.sections[after].name,self.sections[after].bank]
        result = latex.compile_section(section, before, after)
        tools.Debug(result)
        return result
    
    def __eq__(self,other):
        return self.__dict__ == other.__dict__
    
class Section():
    """
    Main class of a section
    """
    
    def __init__(self,name="",bank=1):
        """
        Initialize section
        """
        self.tops = list()
        self.name = name
        self.bank = bank
        self.id = tools.unique_id()
        
    def get_top(self,top_id):
        for top in self.tops:
            if top.id == top_id:
                return top
        raise NameError("ID doesn't find in the top list")
        
    def get_top_list(self):
        if len(self.tops) == 0:
            self.tops.append(Top("Description du top"))
        for top in self.tops:
            yield [top.top,top.id]
            
    def is_last_top(self,top):
        if top == self.tops[-1]:
            return True
        
    def get_top_pos(self,top):
        return self.tops.index(top)
    
    def get_first_top(self):
        try:
            return self.tops[0]
        except IndexError:
            self.tops.append(Top("Description du top"))
            return self.get_first_top()
        
    def append(self,top):
        self.tops.append(top)
        
    def __eq__(self,other):
        return self.__dict__ == other.__dict__
        
class Top():
    """
    Main class of a Top
    """
    
    def __init__(self,top=""):
        self.top = top
        self.action = ""
        self.id = tools.unique_id()
        
    def get_latex(self):
        return latex.transform(self.action)
    
    def get_latex_preview(self):
        """ Give a latex preview of what is typing """
        raw_latex = self.get_latex()
        text = ""
        for line in raw_latex:
            text += line +"\n"
        return text
    
    def get_only_top_latex(self):
        return latex.compile_only_top(self)
    
    def get_subs(self):
        return latex.get_subs(self.action)
    
    def get_pistes(self):
        return latex.get_pistes(self.action)
    
    def __eq__(self,other):
        return self.__dict__ == other.__dict__
    

        
class ProjectSetting():
    """
    Settings of a project
    """
    
    def __init__(self):
        """
        Initialize settings
        """
        
        self.compile_index = True
        self.check_latex = True
    
    def __eq__(self,other):
        return self.__dict__ == other.__dict__
        