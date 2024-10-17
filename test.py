import requests

# Set headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://example.com',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
}

# Send request with headers
url = "https://www.screener.in/screen/raw/?sort=&order=&source_id=440753&query=Volume+1week+average+%3E+Volume+1year+average+*+5+AND%0D%0AReturn+over+1week+%3E+0+AND%0D%0AMarket+Capitalization+%3E+500"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Success! You're able to scrape the page.")
    print(response.text)
else:
    print(f"Failed with status code {response.status_code}")
