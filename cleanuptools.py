# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 15:58:35 2014

At the moment this just prints an error and a it to a text file named lasterror.txt

@author: Thomas
"""

def errorhandling(error,experiment):
    import time
    datenow = time.strftime("%x")
    timenow = time.strftime("%X")
    errorfile = open('%s_errorlog.txt' %(experiment),'a')
    errorfile.write('The last error was on %s at %s :\n' %(datenow, timenow))    
    errorfile.write(error)
    errorfile.write("\n")
    quit
    