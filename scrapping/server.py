#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 20:51:53 2016

@author: rvuillemot
"""


from autoscrapp import AutoScrapp
from flask import Flask


app = Flask(__name__)


        
@app.route("/")
def home():
    return "Hello World"
    
if __name__ == "__main__":
    
    #launch a thread that will autoscrapp every hour
    autoscrapp = AutoScrapp('http://www.maxifoot.fr/calendrier-ligue2.php')
    autoscrapp.start()
    
    #current/main thread will handle user/client request
    app.run()
    
        
        
