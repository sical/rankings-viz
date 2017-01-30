#!/usr/bin/env python3.5

"""
@author: brthao
"""

import os, sys

from src.model.autoscrapp import AutoScrapp
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
    
        
        
