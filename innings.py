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
	    tempsplit=i["name"].split("-")
	    local_html_path = './data/'+tempsplit[len(tempsplit)-1]+'.html'
	    if os.path.exists(local_html_path):
	        with open(local_html_path, 'r', encoding='utf-8') as file:
	            html_content = file.read()
	        soup = BeautifulSoup(html_content, 'html.parser')
	        innings_table = soup.find('table', class_='engineTable')
	        if innings_table:
	            rows = soup.find_all('tr', class_='data1')
	            innings_data = {"1": [], "2": []}
	            for row in rows:
	                columns = row.find_all('td')
	                if len(columns) >= 12:  # Ensure we have enough columns
	                    innings_number = columns[7].text.strip()  # 'Inns' column
	                    innings_info = {
				 			'Overs': columns[0].text.strip(),
				            'BPO': columns[1].text.strip(),
				            'Mdns': columns[2].text.strip(),
				            'Runs': columns[3].text.strip(),
				            'Wkts': columns[4].text.strip(),
				            'Econ': columns[5].text.strip(),
				            'Pos': columns[6].text.strip(),
				            'Opposition': columns[9].text.strip(),
				            'Ground': columns[10].text.strip(),
				            'Start Date': columns[11].text.strip()
	                    }
	                    innings_data[innings_number].append(innings_info)
	                print("First Innings Data:")
	            for inning in innings_data["1"]:
	                print(inning)
	                print("\nSecond Innings Data:")
	            for inning in innings_data["2"]:
	                print(inning)
	        else:	
	            print("Innings table not found in the HTML.")

if __name__ == "__main__":
    app.run(debug=True)