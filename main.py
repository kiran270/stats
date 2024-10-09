from flask import Flask, render_template
from flask import * 
import operator
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from prettytable import PrettyTable
import re

app = Flask(__name__)

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/getstats",methods = ["POST","GET"])
def stats():
	squad_url=request.form.get("url")
	print(squad_url)
	response = requests.get(squad_url)
	soup = BeautifulSoup(response.text, 'html.parser')
	players= soup.find_all('a', class_='ds-inline-flex ds-items-start ds-leading-none')
	player_ids=[]
	for x in players:
	    temp={}
	    if x.has_attr('href'):
	        if "cricketers" in x["href"]:
	            z=x["href"].split("/")
	            temp["name"]=z[2]
	            temp["role"]="ALL"
	            if temp not in player_ids:
	            	player_ids.append(temp)
	stats=[]
	for i in player_ids:
	    print(i)
	    url = 'https://www.espncricinfo.com/cricketers/' + i["name"] + '/matches'
	    response = requests.get(url)
	    soup = BeautifulSoup(response.text, 'html.parser')
	    latest_scores = soup.find_all('tr', class_='ds-text-tight-m')
	    text_parts = eliminate_numbers_and_hyphens(i["name"])
	    row = [text_parts]
	    for x in range(0,10):
	        if len(latest_scores) > x:
	            tds = latest_scores[x].find_all('td', class_='ds-min-w-max')
	            # href=tds[0].find_all('a')
	            # full_scorecard_url='https://www.espncricinfo.com'+href[0]["href"]
	            # response = requests.get(full_scorecard_url)
	            # soup = BeautifulSoup(response.text, 'html.parser')
	            # inningwin = soup.find_all('p', class_='ds-text-tight-m ds-font-regular ds-truncate ds-text-typo')
	            # temp=inningwin[0].text.strip()
	            # innings=""
	            # if "Wickets" in temp:
	            # 	innings=2
	            # else:
	            # 	innings=1
	            Bat = tds[1].text.strip()
	            Bowl = tds[2].text.strip()
	            if "Jan" in Bowl or "Feb" in Bowl or "Mar" in Bowl or "Apr" in Bowl or "May" in Bowl or "Jun" in Bowl or "Jul" in Bowl or "Aug" in Bowl or "Sep" in Bowl or "Oct" in Bowl or"Nov" in Bowl or"Dec" in Bowl:
	                Bowl="--"
	            if i["role"] == "ALL":
	                row.append(f"{Bat} : {Bowl}")
	            else:
	                row.append(f"{Bat}")
	        else:
	            row.append("DNP")
	    fantasy_points_1_10=calculate_fantasy_points(row)
	    fantasy_points_1_5=calculate_fantasy_points(row[0:6])
	    fantasy_points_1_3=calculate_fantasy_points(row[0:4])
	    row.append(fantasy_points_1_10)
	    row.append(fantasy_points_1_5)
	    row.append(fantasy_points_1_3)
	    # calculatepoints(row)
	    stats.append(row)
	    # sorted_data = sorted(stats, key=lambda x: x[11],reverse=True)
	return render_template("finalteams.html",stats=stats)

def calculate_fantasy_points(player_data):
    fantasy_points = 0
    for entry in player_data[1:]:
        if " : " in entry and "&" not in entry:
            stats = entry.split(" : ")
            try:
                runs_scored = 0
                if stats[0] != '--':
                    if "*" in stats[0]:
                        runs_scored = int(stats[0].replace("*", ""))
                    else:
                        runs_scored = int(stats[0])
                wickets_taken = 0
                if stats[1].split("/")[0] != '--' and "c" not in stats[1] and "s" not in stats[1]:
                    wickets_taken_parts = stats[1].split("/")[0].split(" & ")
                    if wickets_taken_parts[0] != '':
                        wickets_taken = int(wickets_taken_parts[0])
                fantasy_points += runs_scored + (wickets_taken * 20)
            except ValueError:
                pass  # Skip the entry if runs_scored cannot be converted to an integer
    return fantasy_points


def eliminate_numbers_and_hyphens(input_string):
    return re.sub(r'[0-9-]', ' ', input_string)

if __name__ == "__main__":
    app.run(debug=True)