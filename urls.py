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
	ftype=request.form.get("type")
	if ftype=="WT20":
		ftype="23"
	elif ftype=="MT20":
		ftype="6"
	elif ftype=="MTEST":
		ftype="1"
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
	    Batting_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    Bowling_First="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    Batting_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=2;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=batting;view=innings"
	    Bowling_Second="https://stats.espncricinfo.com/ci/engine/player/"+tempsplit[len(tempsplit)-1]+".html?batting_fielding_first=1;class="+ftype+";filter=advanced;orderby=start;orderbyad=reverse;template=results;type=bowling;view=innings"
	    batting_first_data=parsebatting(Batting_First)
	    batting_second_data=parsebatting(Batting_Second)
	    bowling_first_data=parsebowling(Bowling_First)
	    bowling_second_data=parsebowling(Bowling_Second)
	    tempdata["player_name"]=i["name"]
	    tempdata["Batting_First"]=batting_first_data
	    tempdata["Bowling_First"]=bowling_first_data
	    tempdata["Batting_Second"]=batting_second_data
	    tempdata["Bowling_Second"]=bowling_second_data
	    stats.append(tempdata)
	return render_template("urls3.html",stats=stats)
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
	# print(soup)
	runs= soup.find_all('td', class_='padAst')
	for i in range(2,len(runs)-1):
		data.append(runs[i].text)
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


if __name__ == "__main__":
    app.run(debug=True)