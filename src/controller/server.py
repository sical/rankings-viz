#!/usr/bin/env python3.5

"""
@author: brthao
"""

import os, sys

from src.model.autoscrapp import MaxiFootAutoScrapp
from flask import Flask, request, send_from_directory


app = Flask(__name__)
app.config["static_folder"] = "../../static/"

@app.route("/html/<path:filename>")
def download_file(filename):
	#return send_from_directory('/static/html', filename)
	file = send_from_directory(app.config["static_folder"]+'html', filename)
	return file
	
	
@app.route("/<sport>/season/<id>")
def display_season(sport,id):
	#return rankchart, giving it the id so rankchart will be generic and make a GET request to api_soccerseason
	print(app.static_url_path)
	#return app.send_static_file("/html/rankchart.html")
	return send_from_directory('html', "rankchart.html")
	
	
@app.route("/data/<filename>")
def return_data(filename):
	return send_from_directory(app.config["static_folder"]+'data', filename)	

@app.route("/api/soccer/season/<id>")
def api_soccerseason(id):
	#return html containing json object of a season corresponding to the year (API)
	#https://www.jokecamp.com/blog/guide-to-football-and-soccer-data-and-apis/#footballdata
	pass
	
	#set root path?
	#return json object
        
@app.route("/")
def home():
	return send_from_directory(app.config["static_folder"]+'html', "rankchart.html")
	#return "rankchart.html"
    #return "Hello World"
    
if __name__ == "__main__":
    
    #launch a thread that will autoscrapp every hour
    soccer_fr_league_2_scrapp = MaxiFootAutoScrapp('soccer_fr_league_2','http://www.maxifoot.fr/calendrier-ligue2.php')
    soccer_fr_league_2_scrapp.start()
    
    
    
    #current/main thread will handle user/client request
    app.run()
    
        
        
