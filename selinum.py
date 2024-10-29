from selenium import webdriver
from selenium.webdriver.chrome.service import Service  # Import the Service class
from bs4 import BeautifulSoup

# Path to ChromeDriver
chrome_driver_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"  # Replace with your correct path

# Set up the service for ChromeDriver
service = Service(chrome_driver_path)

# Initialize WebDriver
driver = webdriver.Chrome(service=service)

# Open the webpage (replace with the actual URL you're scraping)
driver.get('https://www.mykhel.com/kabaddi/pro-kabaddi-arjun-deshwal-p2024/')

# Get the page source after JavaScript is fully loaded
html_content = driver.page_source

# Use BeautifulSoup to parse the dynamically loaded content
soup = BeautifulSoup(html_content, 'html.parser')

# Find all player divs
player_divs = soup.find_all('a', {'data-testid': 'lineups_player'})

# Extract player name and jersey number
players = []
for player in player_divs:
    name_span = player.find('span', {'data-testid': 'lineups_name'})
    number_span = player.find('span', {'data-testid': 'lineups_number'})
    
    if name_span and number_span:
        name = name_span.get_text(strip=True)
        jersey_number = number_span.get_text(strip=True)
        players.append((name, jersey_number))

# Print extracted information
for player in players:
    print(f"Player Name: {player[0]}, Jersey Number: {player[1]}")

# Close the Selenium driver
driver.quit()
