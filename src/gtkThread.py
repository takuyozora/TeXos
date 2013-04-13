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
        tools.log("Starting",log_type=tools.LOG_THREAD,class_type=self,optional_type="check_top")        
        name = "/tmp/"+"tmpTop.tex" ## WINDOWS : corriger le /tmp
        try:
            while True:
                latex = self.queue.get(timeout=15)
                if self.queue.empty() is not True:
                    continue
                with open(name+".tex", "w") as f:  ## WINDOWS : corriger le /tmp
                    f.write(latex)
                cmd = "/usr/bin/pdflatex -halt-on-error -output-directory=%(dir)s %(name)s.tex" % {"name": name, "dir": "/tmp"}
                args = shlex.split(cmd)
                p = subprocess.Popen(args,stdout=subprocess.PIPE)
                while p.poll() is None:
                    tools.log("Compiling ..",log_type=tools.LOG_THREAD,optional_type="check_top")         
                    time.sleep(0.1)
                self.state =  p.wait() == 0
                tools.log("Compilation end : "+str(self.state),log_type=tools.LOG_THREAD,optional_type="check_top")
                self._update_state()
        except queue.Empty:
            tools.log("The queue is empty -> thread end",log_type=tools.LOG_THREAD,optional_type="check_top")
            self.end = True
        
    def append(self,top):
        tools.log("An element is add to the thread",log_type=tools.LOG_THREAD,optional_type="check_top")
        self.queue.put(top.get_only_top_latex())
    
    def _update_state(self):
        tools.log("Updating the widget state",log_type=tools.LOG_THREAD,optional_type="check_top")
        self.widget.set_state(self.state)
        return False