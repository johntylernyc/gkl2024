import requests
import re
import json
from bs4 import BeautifulSoup

def fetch_park_factors():
    url = 'https://baseballsavant.mlb.com/leaderboard/statcast-park-factors'
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    # Optionally write soup to a txt file (uncomment if needed)
    # with open('soup.txt', 'w') as f:
    #     f.write(str(soup))

    match = re.search(r"var data = (\[.*?\]);", str(soup))

    park_factors = {}
    
    if match:
        data_string = match.group(1)
        data_python = json.loads(data_string)
        
        for item in data_python:
            park_factors[item['venue_name']] = item['index_hr']
    else:
        print("No data found")
    
    return park_factors

# The following lines are for testing the function within this script
if __name__ == "__main__":
    park_data = fetch_park_factors()
    for park in park_data:
        print(f"Park Name: {park['Park Name']}, HR Index: {park['HR Index']}")
