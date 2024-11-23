from bs4 import BeautifulSoup
import requests
import re
headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
'Referer': 'https://example.com',
'Accept-Language': 'en-US,en;q=0.9',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}
response = requests.get("https://stats.espncricinfo.com/ci/engine/ground/56407.html?class=23;template=results;type=aggregate;view=results",headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
print(soup)
# Find all elements with class 'ds-text-typo'
scores = soup.find_all('tbody', class_='')[0].find_all('tr')
print(len(scores))
temp=scores[5].find_all('td')[1].text
temp2=scores[5].find_all('td')[2].text
teamA = re.findall(r'\d+/\d+', temp)
teamB = re.findall(r'\d+/\d+', temp2)
for row in reversed(scores):
    score_text = row.find_all('td')[1].text
    final_score = re.findall(r'\d+/\d+', score_text)
    if final_score:
        teamA_lambi=final_score[0]
        break
for row in reversed(scores):
    score_text = row.find_all('td')[2].text
    final_score = re.findall(r'\d+/\d+', score_text)
    if final_score:
        teamB_lambi=final_score[0]
        break
print(teamA_lambi)
print(teamB_lambi)
