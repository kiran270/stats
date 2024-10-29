from flask import Flask, render_template
from flask import * 
import operator
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from prettytable import PrettyTable
import re
import os

app = Flask(__name__)

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/getstats",methods = ["POST","GET"])
def stats():
	squad_url=request.form.get("url")
	ground_url=request.form.get("groundurl")
	ftype=request.form.get("type")
	if ftype=="WT20":
		ftype="23"
	elif ftype=="MT20":
		ftype="6"
	elif ftype=="MTEST":
		ftype="1"
	elif ftype=="MODI":
		ftype="2"
	elif ftype=="WODI":
		ftype="9"
	print(squad_url)
	response = requests.get(squad_url)
	soup = BeautifulSoup(response.text, 'html.parser')
	players_table_rows=soup.find_all('tr')
	player_ids=[]
	for i in range(1,len(players_table_rows)):
		players=players_table_rows[i].find_all('td')
		x=players[1].find_all('a', class_='ds-inline-flex ds-items-start ds-leading-none')
		y=players[2].find_all('a', class_='ds-inline-flex ds-items-start ds-leading-none')
		if len(x) > 0:
			x=x[0]
			if x.has_attr('href'):
				temp={}
				if "cricketers" in x["href"]:
					z=x["href"].split("/")
					temp["name"]=z[2]
					temp["team"]="A"
					if temp not in player_ids:
						player_ids.append(temp)
		if len(y) > 0:
			y=y[0]
			if y.has_attr('href'):
				temp={}
				if "cricketers" in y["href"]:
					z=y["href"].split("/")
					temp["name"]=z[2]
					temp["team"]="B"
					if temp not in player_ids:
						player_ids.append(temp)

	# players= soup.find_all('a', class_='ds-inline-flex ds-items-start ds-leading-none')
	
	print(player_ids)
	# for x in players:
	#     temp={}
	#     if x.has_attr('href'):
	#         if "cricketers" in x["href"]:
	#             z=x["href"].split("/")
	#             temp["name"]=z[2]
	#             temp["team"]="A"
	#             if temp not in player_ids:
	#             	player_ids.append(temp)
	stats=[]
	for i in player_ids:
	    print(i)
	    tempdata={}
	    tempsplit=i["name"].split("-")
	    Batting_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    Bowling_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    Batting_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    Bowling_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    batting_first_data=parsebatting(Batting_First)
	    batting_second_data=parsebatting(Batting_Second)
	    bowling_first_data=parsebowling(Bowling_First)
	    bowling_second_data=parsebowling(Bowling_Second)
	    tempdata["player_name"]=i["name"]
	    tempdata["team"]=i["team"]
	    tempdata["Batting_First"]=batting_first_data
	    tempdata["Bowling_First"]=bowling_first_data
	    tempdata["Batting_Second"]=batting_second_data
	    tempdata["Bowling_Second"]=bowling_second_data
	    stats.append(tempdata)
	# create_dream11_teams(stats)
	# print(stats)
	reports=groundstats(ground_url)
	return render_template("urls3.html",stats=stats,reports=reports)
def groundstats(ground_url):
	reports=[]
	headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Referer': 'https://example.com',
			'Accept-Language': 'en-US,en;q=0.9',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
		}
	response = requests.get(ground_url,headers=headers)
	soup = BeautifulSoup(response.text, 'html.parser')
	urls=soup.find_all('a')
	reporturls=[]
	groundstats=[]
	for i in urls:
		if i.has_attr('href'):
			if "full-scorecard" in i["href"]:
				reporturls.append(i["href"])
	for i in reporturls:
		temp=i.replace("full-scorecard","match-report")
		tempurl="https://www.espncricinfo.com"+temp
		print(tempurl)
		response = requests.get(tempurl)
		soup = BeautifulSoup(response.text, 'html.parser')
		summary=soup.find_all('i')
		for x in summary:
			if x.text:
				if x.text not in reports:
					reports.append(x.text)
	return reports

def parsebatting(url):
	headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://example.com',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
	}
	data=[]
	response = requests.get(url,headers=headers)
	soup = BeautifulSoup(response.text, 'html.parser')
	engineTables=soup.find_all('table',class_='engineTable')
	for i in engineTables:
		temp= i.find_all('caption')
		if len(temp) > 0:
			if temp[0].text=="Innings by innings list":
				runs= i.find_all('td', class_='padAst')
				if len(runs) > 0:
					for x in range(0,len(runs)):
						data.append(runs[x].text)
	return data
def parsebowling(url):
	print(url)
	headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://example.com',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
	}
	data=[]
	response = requests.get(url,headers=headers)
	soup = BeautifulSoup(response.text, 'html.parser')
	# print(soup)
	headlinks=soup.find_all('tr',class_='headlinks')
	if len(headlinks) > 0:
		headlinkstemp=headlinks[0].find_all('th')
		count=0
		for i in range(0,len(headlinkstemp)):
			if headlinkstemp[i].text=='Wkts':
				count=i
				break
		wickets= soup.find_all('tr', class_='data1')
		for i in range(2,len(wickets)-1):
			temp=wickets[i].find_all('td')
			data.append(temp[count].text)
	return data

import random

def weighted_average(scores, recent_weight=0.7):
    if len(scores) == 0:
        return 0

    if len(scores) <= 5:
        return sum(scores) / len(scores)

    recent_matches = scores[-5:]
    older_matches = scores[:-5]
    
    recent_avg = sum(recent_matches) / len(recent_matches)
    older_avg = sum(older_matches) / len(older_matches) if older_matches else 0
    
    return (recent_weight * recent_avg) + ((1 - recent_weight) * older_avg)

def create_dream11_teams(stats):
    batting_scores = {}
    bowling_scores = {}
    teams = []

    for player in stats:
        name = player['player_name']
        print(player)
        if player['team']=='A':
        	batting_first = player['Batting_First']
        	bowling_first = player['Bowling_Second']
        else:
        	batting_first = player['Batting_Second']
        	bowling_first = player['Bowling_First']        	
        
        batting_last_5 = [int(run) for run in batting_first[-5:] if run.isdigit()]
        bowling_last_5 = [int(wkt) for wkt in bowling_first[-5:] if wkt.isdigit()]
        
        batting_last_10 = [int(run) for run in batting_first[-10:] if run.isdigit()]
        bowling_last_10 = [int(wkt) for wkt in bowling_first[-10:] if wkt.isdigit()]
        
        # Consistency and recent form
        batting_avg_5 = sum(batting_last_5) / len(batting_last_5) if batting_last_5 else 0
        bowling_avg_5 = sum(bowling_last_5) / len(bowling_last_5) if bowling_last_5 else 0
        batting_avg_10 = sum(batting_last_10) / len(batting_last_10) if batting_last_10 else 0
        bowling_avg_10 = sum(bowling_last_10) / len(bowling_last_10) if bowling_last_10 else 0

        # Weighted average of last 10 matches
        batting_weighted_avg = weighted_average(batting_last_10)
        bowling_weighted_avg = weighted_average(bowling_last_10)

        # Populate batting and bowling scores
        batting_scores[name] = {
            'last_5': batting_avg_5,
            'last_10': batting_avg_10,
            'weighted': batting_weighted_avg,
            'total': sum(batting_last_10)
        }
        bowling_scores[name] = {
            'last_5': bowling_avg_5,
            'last_10': bowling_avg_10,
            'weighted': bowling_weighted_avg,
            'total': sum(bowling_last_10)
        }

    def select_team(batting_criteria, bowling_criteria):
        """
        Selects a team based on specific batting and bowling criteria.
        Ensures no duplicate players in a single team.
        """
        selected_players = set()
        team = []
        
        for player, score in sorted(batting_scores.items(), key=lambda x: x[1][batting_criteria], reverse=True):
            if player not in selected_players:
                team.append(player)
                selected_players.add(player)
            if len(team) == 6:  # Select 6 batsmen
                break
        
        for player, score in sorted(bowling_scores.items(), key=lambda x: x[1][bowling_criteria], reverse=True):
            if player not in selected_players:
                team.append(player)
                selected_players.add(player)
            if len(team) == 11:  # Select 5 bowlers after 6 batsmen
                break

        return team

    # Team selection based on different logics
    teams.append(select_team('last_5', 'last_5'))  # Best recent form
    teams.append(select_team('last_10', 'last_10'))  # Consistency over 10 matches
    teams.append(select_team('total', 'total'))  # Best in total batting/bowling performance
    teams.append(select_team('weighted', 'weighted'))  # Highest weighted averages
    teams.append(select_team('last_5', 'last_10'))  # Best recent batsmen, consistent bowlers
    teams.append(select_team('weighted', 'total'))  # Best recent weighted performance for batting, total for bowling
    teams.append(select_team('last_10', 'last_5'))  # Consistent batsmen, recent form for bowlers
    teams.append(select_team('total', 'last_5'))  # Top batting, recent bowling form
    teams.append(select_team('last_5', 'weighted'))  # Best in recent batting form, recent weighted bowling
    teams.append(random.sample(list(batting_scores.keys()) + list(bowling_scores.keys()), 11))  # Random team

    # Output 10 teams without duplicates
    for idx, team in enumerate(teams):
        print(f"Team {idx + 1}: {team}")

if __name__ == "__main__":
    app.run(debug=True)