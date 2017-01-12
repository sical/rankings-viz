#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 20:51:53 2016

@author: rvuillemot
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import urllib.request
import pandas as pd
import json
import lxml

# 2009-2010
# premier-league-2010-2011.htm#j8

# Has the game been played yet?
def is_played_game(score):
    split = score.split("-")
    if(len(split) != 2):
        return False
    if(len(split[0]) == 0):
        return False
    else:
        return True

# ??
def flatten(d, parent_key=''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten(v, '%s%s_' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)

def scrap(url):
    req = urllib.request.Request(url)
    r = urllib.request.urlopen(req)
    soup = BeautifulSoup(r, 'lxml')
    
    days = soup.find_all("table", class_="cd1")
    
    nb_days = len(days)
    
    print(nb_days)
    
    # Test True
    assert nb_days == 38

    
    # Init rankings
    teams = {}
    for day in days:
        d = day.find_all("tr")
        d.pop(0) # ??
        for games in d:
            game = games.find_all("td")
            score = games.find("th")
            teams[game[0].text] = [{"day": x, "pts": 0, "win": 0, "rank": 0} for x in range(39)]

    assert len(set(teams)) == 20

    return(teams, days);

def parse_compute(teams, days):
    for day in days:
        d = day.find_all("tr")
        current_day = int(d.pop(0).text.split(" ")[1].split("e")[0])
        for games in d:
            game = games.find_all("td")
            score = games.find("th")
            teamHome = game[0].text
            teamAway = game[1].text
            if is_played_game(score.text):
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
    
if __name__ == "__main__":
    
    html, days = scrap('http://www.maxifoot.fr/calendrier-ligue1-2015-2016.htm')    
    teams = parse_compute(html, days)

    flat_teams = []
    
    for team in teams:
        for day in teams[team]:
            d = day
            d['team'] = team
            flat_teams.append(d)
            
    # Do we have the right number of days?
    assert len(flat_teams) == (20 * 39)
    
    df = pd.DataFrame.from_dict(flat_teams);

    # Solving ties
    df = df.sort_values(['day', 'pts', 'win'], ascending=[True, False, True]);

    # Calculate ranking
    df['rank'] = df.groupby('day')['pts'].rank(ascending=False, method='first').apply(lambda x: int(x))
    
    df.sort_values(['rank'], ascending=False);
    df.to_json(orient='records')
    df.to_csv(header=True, columns=["day", "pts", "rank", "team"], sep=',', index=False)
    
    #with open('ranking-predictions/soccer_ligue1.json', 'w') as fp:
    #    fp.write(df.to_json(orient='records'))
    with open('data/soccer_ligue1.csv', 'w') as fp:
        fp.write(df.to_csv(header=True, columns=["day", "pts", "rank", "team"], sep=',', index=False))
        print("File saved!")