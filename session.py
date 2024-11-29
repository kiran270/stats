import requests
from bs4 import BeautifulSoup
import re
import csv

def sessionData(ground_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(ground_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    report_urls_set = {
        "https://www.espncricinfo.com" + i["href"].replace("full-scorecard", "match-overs-comparison")
        for i in soup.find_all('a', href=True) if "full-scorecard" in i["href"]
    }
    report_urls = list(report_urls_set)

    session_scores = []
    count = 0
    for url in report_urls:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        scores = soup.find_all('tbody')[0].find_all('tr') if soup.find_all('tbody') else []

        over_by_over_scores_teamA = []

        for row in scores:
            tds = row.find_all('td')
            if len(tds) > 2:
                teamA_score = re.findall(r'\d+/\d+', tds[1].text)
                # Append score or "N/A" if not found
                over_by_over_scores_teamA.append(teamA_score[0] if teamA_score else "N/A")

        session_scores.append(over_by_over_scores_teamA)
        count += 1
        if count > 400:
            break

    return session_scores

def write_to_csv(over_by_over_data):
    with open("Women_BIGBASH.csv", "w", newline="") as file:
        writer = csv.writer(file)  
        max_overs = max(len(match_data) for match_data in over_by_over_data)
        header = ["Match"] + [f"Over {i+1}" for i in range(max_overs)]
        writer.writerow(header)

        for match_idx, match_data in enumerate(over_by_over_data, start=1):
            # Add formula-like input to prevent date conversion in Excel
            row = [f"Match {match_idx}"] + [f'="{score}"' for score in match_data] + ["N/A"] * (max_overs - len(match_data))
            writer.writerow(row)

# Example usage:
ground_url = "https://www.espncricinfo.com/records/trophy/team-match-results/women-s-big-bash-league-720"
results = sessionData(ground_url)
write_to_csv(results)

print("CSV file written successfully.")
