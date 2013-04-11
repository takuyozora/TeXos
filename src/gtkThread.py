# -*- coding: utf-8 -*-

import threading
import subprocess
#import tools
import shlex
import tools
import time
import queue
from gi.repository import GObject

GObject.threads_init()

class LatexCheckThread(threading.Thread):
    def __init__(self,top,widget):
        threading.Thread.__init__(self)
        self.widget = widget
        self.queue = queue.Queue()
        self.append(top)
 
    def run(self):
        self.state = None
        self.end = False
        tools.Debug("Start thread")        
        name = "/tmp/"+"tmpTop.tex" ## WINDOWS : corriger le /tmp
        try:
            while True:
                tools.Debug(" [thread] Boucle")
                latex = self.queue.get(timeout=15)
                if self.queue.empty() is not True:
                    continue
                with open(name+".tex", "w") as f:  ## WINDOWS : corriger le /tmp
                    f.write(latex)
                cmd = "/usr/bin/pdflatex -halt-on-error -output-directory=%(dir)s %(name)s.tex" % {"name": name, "dir": "/tmp"}
                args = shlex.split(cmd)
                p = subprocess.Popen(args,stdout=subprocess.PIPE)
                while p.poll() is None:
                    tools.Debug(" [thread] Currently compiling [TOP] ...")            
                    time.sleep(0.1)
                tools.Debug(" [thread] Compile end [TOP] !")
                self.state =  p.wait() == 0
                tools.Debug(" [thread] Compile : "+str(self.state))
                self._update_state()
        except queue.Empty:
            tools.Debug("EMPTY")
            self.end = True
        
    def append(self,top):
        tools.Debug("Element ajouté au thread")
        self.queue.put(top.get_only_top_latex())
    
    def _update_state(self):
        tools.Debug(" [thread] UPDATE_STATE..")
        self.widget.set_state(self.state)
        return False