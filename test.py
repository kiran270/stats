import requests
from flask import Flask, render_template
from flask import * 
import operator
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
from prettytable import PrettyTable
import re
import os
# Set headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://example.com',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}

# Send request with headers
url = "https://www.sofascore.com/football/match/fenerbahce-manchester-united/Ksclb#id:12764133,tab:lineups"
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
players_table_rows=soup.find_all('a')
for i in players_table_rows:
	print(i)
	if i.has_attr('data-testid'):
		print(i)

# Find all player divs by class instead of 'data-testid'
print(len(players_table_rows))