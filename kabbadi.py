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
teams={
	"Jaipur": "1",
	"Telugu": "2"
}

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
				if "cricketers" in x["href"]:
					z=y["href"].split("/")
					temp["name"]=z[2]
					temp["team"]="B"
					if temp not in player_ids:
						player_ids.append(temp)