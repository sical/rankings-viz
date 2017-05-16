#!/usr/bin/env python3.6
# coding: utf-8
"""
@author: brthao
"""

import os, sys
import psycopg2
import urllib.parse
import json

from src.model.autoscrapp import MaxiFootAutoScrapp
from flask import Flask, request, send_from_directory



urllib.parse.uses_netloc.append("postgres")
#use remote db
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

conn.autocommit = True

cur = conn.cursor()


app = Flask(__name__)
app.config["static_folder"] = "../../static/"
app.config["root"] = "../../"
	
	
@app.route("/html/<path:filename>")
def download_file(filename):
	#return send_from_directory('/static/html', filename)
	file = send_from_directory(app.config["static_folder"]+'html', filename)
	return file
	
	
@app.route("/logs")
def display_logs():
	cur.execute("SELECT * FROM LOG;")
	rows = cur.fetchall()
	if rows == None:
		return "HTTP_404_NOT_FOUND"
	res = ""
	for row in rows:
		log = str(row[2]) + " " + str(row[0]) + " : " + str(row[1])  + "<br>"
		res = res + log
	return res
	#return send_from_directory(app.config["root"],"log.txt")


@app.route("/data/championships")
def get_championships():
	return send_from_directory(app.config["static_folder"]+'data', "championships.json")	
	
	
#access to json data of championships
@app.route("/data/<filename>")
def return_data(filename):
	cur.execute("SELECT * FROM DATA WHERE name=%s;",(filename,))
	res = cur.fetchone()
	if res == None:
		return "HTTP_404_NOT_FOUND"
	return res[1]
	
	#return send_from_directory(app.config["static_folder"]+'data', filename)	


@app.route("/")
def home():
	return send_from_directory(app.config["static_folder"]+'html', "rankchart.html")
	#return "rankchart.html"
    #return "Hello World"
    
    
    
    
    
if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))

	#actual year will be scrapped continuously
	actual = "2016-2017"
	
	f = open("static/data/championships.json","r")
	
	jsonData = f.read()
	data = json.loads(jsonData)
	
	
	for championship in data:		
		for season in championship["seasons"]:
			if season["label"] == actual:
				#scrapp continuously
				MaxiFootAutoScrapp(season["name"],season["url"]).start()
				
			else:
				#scrapp only once
				MaxiFootAutoScrapp(season["name"],season["url"]).scrapping()
		
	

	#current/main thread will handle user/client request
	app.run(host='0.0.0.0', port=port)
    
        
        
