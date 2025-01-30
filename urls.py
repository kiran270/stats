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
	html_files = [f for f in os.listdir("templates/Match_pages/") if f.endswith('.html')]
	print("HTML files:", html_files)
	return render_template("matches.html",html_files=html_files)

@app.route("/addmatch")
def addmatch():
	return render_template("index.html")

@app.route("/viewdetails",methods = ["POST"])
def viewdetails():
	filename=request.form.get("viewdetails_filename")
	return render_template("Match_pages/"+filename)

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
	if ground_url!="":
		reports,summarystats=groundstats(ground_url)
		session_scores=sessionData(ground_url)
	else:
		reports=[]
		summarystats=[]
		session_scores=[]
	sorted_data = sorted(stats, key=lambda x: x["team"])
	squad_url_split=squad_url.split("/")
	dreamteams=dreamstats(ground_url)
	rendered_html = render_template('urls3.html', stats=sorted_data,reports=reports,summary=summarystats,session_scores=session_scores,dreamteams=dreamteams)
	with open("templates/Match_pages/"+squad_url_split[5]+".html", "w", encoding="utf-8") as file:
		file.write(rendered_html)
	return rendered_html

def getDreamteam(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://example.com',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }

    # Sending the request to fetch the webpage content
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find_all('tr', class_='ds-text-right')
    player_stats = []
    for row in rows:
        td_elements = row.find_all('td')
        if len(td_elements) >= 7:
            player_name_tag = row.find('span')
            if player_name_tag:
                player_name = player_name_tag.text.strip()
            else:
                player_name = 'N/A'  # If no name found, set a default value
            runs_str = td_elements[3].text.strip()
            if runs_str == '-' or not runs_str.split('(')[0].strip().isdigit():
                runs = 0  # If no valid runs, set runs to 0
            else:
                runs = int(runs_str.split('(')[0].strip())  # Extract only the runs (e.g., 47 from "47(31)")
            wickets_str = td_elements[6].text.strip()
            if wickets_str == '-' or not '/' in wickets_str:
                wickets = 0  # If no valid wickets, set wickets to 0
            else:
                wickets = int(wickets_str.split('/')[0].strip())
            fantasy_points = runs + (wickets * 25)
            team = td_elements[1].text.strip()
            player_stats.append({
                'player_name': player_name,
                'team': team,
                'runs': runs,
                'wickets': wickets,
                'fantasy_points': fantasy_points
            })
        else:
            continue
    sorted_player_stats = sorted(player_stats, key=lambda x: x['fantasy_points'], reverse=True)[:11]
    return sorted_player_stats

def dreamstats(ground_url):
    dreamteams=[]
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
            batting_win_count=batting_win_count+1
            winning_team=tds[2].text
            print(winning_team+"Won Batting First")
        elif 'wickets' in tds[3].text:
            chasing_win_count=chasing_win_count+1
            winning_team=tds[2].text
            print(winning_team+"Won Chasing")
        urls=i.find_all('a')
        for x in urls:
            if x.has_attr('href'):
                if "full-scorecard" in x["href"]:
                    temp=x["href"].replace("full-scorecard","match-impact-player")
                    tempurl="https://www.espncricinfo.com"+temp
                    x=getDreamteam(tempurl)
                    if len(x) > 0:
                    	dreamteams.append(getDreamteam(tempurl))
    return dreamteams

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