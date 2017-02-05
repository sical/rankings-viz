#!/usr/bin/env python3.5

"""
@author: brthao
"""

import os, sys

from src.model.autoscrapp import MaxiFootAutoScrapp
from flask import Flask


app = Flask(__name__)

@app.route("/<sport>/season/<id>")
def display_season(sport,id):
	#return rankchart, giving it the id so rankchart will be generic and make a GET request to api_soccerseason
	print(app.static_url_path)
	return app.send_static_file("/html/rankchart.html")

@app.route("/api/soccerseason/<id>")
def api_soccerseason(id):
	#return html containing json object of a season corresponding to the year (API)
	#https://www.jokecamp.com/blog/guide-to-football-and-soccer-data-and-apis/#footballdata
	pass
	
	#set root path?
	#return json object
        
@app.route("/")
def home():
	
	#return "rankchart.html"
    return "Hello World"
    
if __name__ == "__main__":
    
    #launch a thread that will autoscrapp every hour
    soccer_fr_league_2_scrapp = MaxiFootAutoScrapp('soccer_fr_league_2','http://www.maxifoot.fr/calendrier-ligue2.php')
    soccer_fr_league_2_scrapp.start()
    
    #current/main thread will handle user/client request
    app.run()
    
        
        
