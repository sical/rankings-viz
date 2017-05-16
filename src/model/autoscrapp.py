#!/usr/bin/env python3

"""
@author: rvuillemot
@contributor: brthao
"""

from threading import Thread
from bs4 import BeautifulSoup
from urllib.request import urlopen

import urllib.request
import pandas as pd
import json
import lxml
import schedule
import time
import datetime
import sys

import os
import psycopg2
import urllib.parse

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

class MaxiFootAutoScrapp(Thread):
	
	def __init__(self,name,url):
		Thread.__init__(self)
		self.url = url
		self.name = name
		# 2009-2010
	# premier-league-2010-2011.htm#j8

	# Has the game been played yet?
	def is_played_game(self, score):
		split = score.split("-")
		if(len(split) != 2):
			return False
		if(len(split[0]) == 0):
			return False
		else:
			return True

	# ??
	def flatten(self, d, parent_key=''):
		items = []
		for k, v in d.items():
			try:
				items.extend(flatten(v, '%s%s_' % (parent_key, k)).items())
			except AttributeError:
				items.append(('%s%s' % (parent_key, k), v))
		return dict(items)

	def scrap(self,url):
		#need to specify user agent to avoid error FORBIDDEN 403 responses
		headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"}
		req = urllib.request.Request(url, headers=headers)
		
		#req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
		r = urllib.request.urlopen(req)
		
		soup = BeautifulSoup(r, 'lxml')
		
		days = soup.find_all("table", class_="cd1")
		
		nb_days = len(days)
		
		#print(nb_days)
		
		# Test True
		#assert nb_days == 38

		
		# Init rankings
		teams = {}
		for day in days:
			d = day.find_all("tr")
			d.pop(0) # ??
			for games in d:
				game = games.find_all("td")
				score = games.find("th")
				teams[game[0].text] = [{"day": x, "pts": 0, "win": 0, "rank": 0} for x in range(39)]

		#assert len(set(teams)) == 20

		return(teams, days);

	def parse_compute(self, teams, days):
		for day in days:
			d = day.find_all("tr")
			current_day = int(d.pop(0).text.split(" ")[1].split("e")[0])
			for games in d:
				game = games.find_all("td")
				score = games.find("th")
				teamHome = game[0].text
				teamAway = game[1].text
				if self.is_played_game(score.text):
					scoreHome = int(score.text.split("-")[0])
					scoreAway = int(score.text.split("-")[1])
					if(scoreHome > scoreAway):
						teams[teamHome][current_day]['pts'] = teams[teamHome][current_day-1]['pts'] + 3
						teams[teamHome][current_day]['win'] += 1

						teams[teamAway][current_day]['pts'] = teams[teamAway][current_day-1]['pts']
					elif(scoreHome < scoreAway):
						teams[teamHome][current_day]['pts'] = teams[teamHome][current_day-1]['pts']

						teams[teamAway][current_day]['pts'] = teams[teamAway][current_day-1]['pts'] + 3
						teams[teamAway][current_day]['win'] += 1
					else:
						teams[teamHome][current_day]['pts'] = teams[teamHome][current_day-1]['pts'] + 1
						teams[teamAway][current_day]['pts'] = teams[teamAway][current_day-1]['pts'] + 1
				else:
					teams[teamHome][current_day]['pts'] = teams[teamHome][current_day-1]['pts']
					teams[teamAway][current_day]['pts'] = teams[teamAway][current_day-1]['pts']
		
		return teams;	
		
		
		
	def scrapping(self):
		print("scrapping of " + self.name)
		sys.stdout.flush()
		html = ""
		days = ""
		try:
			html, days = self.scrap(self.url)
		except urllib.error.HTTPError:
			print("HTTP error")
			return   
		except urllib.error.URLError:
			print("URL error")
			return 
		#these errors may only exist when I scrapp every 2-3 sec	
			
			
		teams = self.parse_compute(html, days)

		flat_teams = []
		
		
		for team in teams:
			for day in teams[team]:
				d = day
				d['team'] = team
				flat_teams.append(d)
				
		# Do we have the right number of days?
		#assert len(flat_teams) == (20 * 39)
		
		df = pd.DataFrame.from_dict(flat_teams);

		# Solving ties
		df = df.sort_values(['day', 'pts', 'win'], ascending=[True, False, True]);

		# Calculate ranking
		df['rank'] = df.groupby('day')['pts'].rank(ascending=False, method='first').apply(lambda x: int(x))
		
		df.sort_values(['rank'], ascending=False);
		values = df.to_json(orient='records')
		df.to_csv(header=True, columns=["day", "pts", "rank", "team"], sep=',', index=False)
		
		
		
		
		cur.execute("SELECT * FROM DATA WHERE name=%s;",(self.name,))
		
		#res=""
		#try:
		res = cur.fetchone()
		#except psycopg2.ProgrammingError:
		#	print("no tuples found" + self.name)
		#	res = None
			
		
		#if res != None:
		if cur.rowcount != -1 and cur.rowcount == 1 and res != None and res[1] != None:
			#res[0]=name, res[1]=json
			
			is_new = False
			
			#now = datetime.datetime.now()
			#date = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " + str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
			
			
			if str(res[1])==str(values):
				print("NO CHANGES")
			else:
				
				is_new = True
				print("CHANGES")
				
				cur.execute("UPDATE DATA set json=%s WHERE name=%s",(values,self.name))
				
			text = "SCRAPPING FOR " + self.name + " FROM " + self.url + "\n"
			
			cur.execute("INSERT INTO LOG VALUES(current_timestamp, %s, %s);",(text,is_new))
			
		else:
			print("PAS DE TUPLE AVEC " + self.name)
			try:
				cur.execute("INSERT INTO DATA VALUES(%s,%s)",(self.name,values))
			except psycopg2.Error as e:
				print("Unable to connect!")
				print(e.pgerror)
				print(e.diag.message_detail)
				#sys.exit(1)
			except:
				print("Unexpected error:", sys.exc_info()[0])
		
		#writing in file is not persistent with heroku, need to use postgresql db		
		#with open('log.txt', "a") as fp:
		#	now = datetime.datetime.now()
		#	fp.write(str(now.day) + "." +str(now.month) + "." +str(now.year) + " - " +str(now.hour) + ":" +str(now.minute) + ":" +str(now.second) + " :")
		#	fp.write("SCRAPPING FOR " + self.name + " FROM " + self.url + "\n")
		
		#with open('static/data/'+self.name+'.json', 'w+') as fp:
		 #   fp.write(df.to_json(orient='records'))
		    
		#with open('static/data/soccer_ligue1.csv', 'w') as fp:
		#	fp.write(df.to_csv(header=True, columns=["day", "pts", "rank", "team"], sep=',', index=False))
		#	print("File saved!")
   	
		
	def run(self):
		
		#scrapp every hour
		schedule.every(1).hour.do(self.scrapping)
		
		#every 27 minutes so the heroku free dyno wont sleep before the scrapp work
		#schedule.every(0.45).hour.do(self.scrapping)
		
		#finally, dyno only check traffic (requests i think...) to decide to sleep or not
		
		#to test
		#schedule.every(0.08).minutes.do(self.scrapping)
		
		while True:
			schedule.run_pending()
			time.sleep(1)

	

