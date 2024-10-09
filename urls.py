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
	    tempdata={}
	    tempsplit=i["name"].split("-")
	    T20_Batting_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class=6;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    T20_Bowling_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class=6;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    T20_Batting_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class=6;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    T20_Bowling_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class=6;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    ODI_Batting_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class=2;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    ODI_Bowling_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class=2;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    ODI_Batting_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class=2;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    ODI_Bowling_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class=2;filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    tempdata["player_name"]=i["name"]
	    tempdata["T20_Batting_First"]=T20_Batting_First
	    tempdata["T20_Bowling_First"]=T20_Bowling_First
	    tempdata["T20_Batting_Second"]=T20_Batting_Second
	    tempdata["T20_Bowling_Second"]=T20_Bowling_Second
	    tempdata["ODI_Batting_First"]=ODI_Batting_First
	    tempdata["ODI_Bowling_First"]=ODI_Bowling_First
	    tempdata["ODI_Batting_Second"]=ODI_Batting_Second
	    tempdata["ODI_Bowling_Second"]=ODI_Bowling_Second
	    stats.append(tempdata)
	return render_template("urls.html",stats=stats)

if __name__ == "__main__":
    app.run(debug=True)