from flask import Flask, render_template
from flask import * 
import operator
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from prettytable import PrettyTable
import re
import os
import csv

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
	
	print(player_ids)
	stats=[]
	output_file = "output.csv"
	with open(output_file, mode='w', newline='') as file:
		writer = csv.writer(file)  
		writer.writerow(["player","Innings","Runs","wickets"])
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
		    for x, y in zip(batting_first_data, bowling_second_data):
		    	writer.writerow([i["name"],"1",x, y])
		    for x, y in zip(batting_second_data, bowling_first_data):
		    	writer.writerow([i["name"],"2",x, y])
	# # Specify the filename
	# filename = 'player_performance_data.csv'

	# # Extract the keys from the first dictionary in the stats list to use as headers
	# if stats:
	#     headers = stats[0].keys()

	# # Write the data to a CSV file
	# with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
	#     writer = csv.DictWriter(csvfile, fieldnames=headers)
	#     writer.writeheader()  # Write the header row
	#     writer.writerows(stats)  # Write all rows

	# print(f"Data successfully written to {filename}")
	# # create_dream11_teams(stats)
	# # print(stats)
	if ground_url!="":
		reports,summarystats=groundstats(ground_url)
		session_scores=sessionData(ground_url)
	else:
		reports=[]
		summarystats=[]
		session_scores=[]
	sorted_data = sorted(stats, key=lambda x: x["team"])
	return render_template("urls3.html",stats=sorted_data,reports=reports,summary=summarystats,session_scores=session_scores)
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
	batting_win_count=0
	chasing_win_count=0
	summarystats={}
	trs=soup.find_all('tr')
	for i in trs:
		tds=i.find_all('td')
		if 'runs' in tds[3].text:
			print(tds[3].text)
			batting_win_count=batting_win_count+1
			print(batting_win_count)
		elif 'wickets' in tds[3].text:
			print(tds[3].text)
			chasing_win_count=chasing_win_count+1
			print(chasing_win_count)
	summarystats["batting_win_count"]=batting_win_count
	summarystats["chasing_win_count"]=chasing_win_count
	print(summarystats)
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
	return reports,summarystats

def sessionData(ground_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://example.com',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }

    response = requests.get(ground_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    report_urls_set = {
        "https://www.espncricinfo.com" + i["href"].replace("full-scorecard", "match-overs-comparison")
        for i in soup.find_all('a', href=True) if "full-scorecard" in i["href"]
    }
    report_urls = list(report_urls_set)

    session_scores = []
    for url in report_urls:
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        scores = soup.find_all('tbody')[0].find_all('tr') if soup.find_all('tbody') else []
        
        # Initialize scores
        teamA = teamB = []
        if len(scores) > 5:
            tds = scores[5].find_all('td')
            if len(tds) > 2:
                teamA = re.findall(r'\d+/\d+', tds[1].text)
                teamB = re.findall(r'\d+/\d+', tds[2].text)

        # Initialize session scores
        session_score = {
            "teamA_6": teamA[0] if teamA else "N/A",
            "teamB_6": teamB[0] if teamB else "N/A",
            "teamA_lambi": extract_final_score(scores, 1),
            "teamB_lambi": extract_final_score(scores, 2)
        }
        session_scores.append(session_score)

    return session_scores

def extract_final_score(scores, index):
    for row in reversed(scores):
        tds = row.find_all('td')
        if len(tds) > index:
            final_score = re.findall(r'\d+/\d+', tds[index].text)
            if final_score:
                return final_score[0]
    return "N/A"

def detect_match_outcome(summary):
    """
    Detects whether a match was won by batting first or chasing.
    """
    # Regex pattern to match scores
    score_pattern = r"(\d+ for \d+|\d+)"
    
    # Find all scores in the match summary
    scores = re.findall(score_pattern, summary)
    
    # Determine teams based on score order
    first_team = scores[0] if scores else None
    second_team = scores[1] if len(scores) > 1 else None
    
    # Outcome determination logic
    if "beat" in summary:
        beat_pos = summary.index("beat")
        if beat_pos < summary.index(scores[0]):
            return "Batting Win"
        else:
            return "Chasing Win"
    return "Outcome Undetermined"


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

def fantasy_points(runs, wickets):
    return runs + (wickets * 25)

def weighted_average(scores, recent_weight=0.7):
    if not scores:
        return 0
    if len(scores) <= 5:
        return sum(scores) / len(scores)
    recent_matches = scores[-5:]
    older_matches = scores[:-5]
    recent_avg = sum(recent_matches) / len(recent_matches)
    older_avg = sum(older_matches) / len(older_matches) if older_matches else 0
    return (recent_weight * recent_avg) + ((1 - recent_weight) * older_avg)

def create_dream11_teams(stats):
    fantasy_scores = {}
    teams = []

    for player in stats:
        name = player['player_name']
        team = player['team']
        
        # Calculate fantasy points based on recent games
        batting_scores = [int(run) if run.isdigit() else 0 for run in player.get('Batting_First' if team == 'A' else 'Batting_Second', [])]
        bowling_scores = [int(wkt) if wkt.isdigit() else 0 for wkt in player.get('Bowling_Second' if team == 'A' else 'Bowling_First', [])]
        
        # Fantasy points over different time frames
        fantasy_scores[name] = {
            'last_3': fantasy_points(sum(batting_scores[-3:]), sum(bowling_scores[-3:])),
            'last_5': fantasy_points(sum(batting_scores[-5:]), sum(bowling_scores[-5:])),
            'last_10': fantasy_points(sum(batting_scores[-10:]), sum(bowling_scores[-10:])),
            'total': fantasy_points(sum(batting_scores), sum(bowling_scores)),
            'weighted': fantasy_points(weighted_average(batting_scores), weighted_average(bowling_scores))
        }

    def select_team(criteria, team_a_count=7, team_b_count=4):
        """
        Selects a team based on fantasy points criteria and team count constraints.
        Ensures no duplicate players in a single team.
        """
        team = []
        selected = set()
        
        for player, scores in sorted(fantasy_scores.items(), key=lambda x: x[1][criteria], reverse=True):
            team_criteria = stats[[p['player_name'] for p in stats].index(player)]['team']
            if (team_criteria == 'A' and team_a_count > 0) or (team_criteria == 'B' and team_b_count > 0):
                team.append(player)
                selected.add(player)
                if team_criteria == 'A':
                    team_a_count -= 1
                else:
                    team_b_count -= 1
            if len(team) == 11:
                break
        return team

    # Team selections based on criteria
    teams.append(select_team('last_3'))  # Best last 3 matches
    teams.append(select_team('last_5'))  # Best last 5 matches
    teams.append(select_team('last_10')) # Consistent over 10 matches
    teams.append(select_team('total'))   # Top overall fantasy points
    teams.append(select_team('weighted'))  # Weighted average performance
    teams.append(select_team('last_5', team_a_count=6, team_b_count=5))  # Alternate A-B distribution

    # Output 10 teams without duplicates
    for idx, team in enumerate(teams):
        print(f"Team {idx + 1}: {team}")

if __name__ == "__main__":
    app.run(debug=True,port=8000)