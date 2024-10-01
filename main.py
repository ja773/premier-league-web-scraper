import requests
from bs4 import BeautifulSoup
import pandas as pd

# Data Scraping from 19/20 season to 23/24 season
standings_url = 'https://fbref.com/en/comps/9/2023-2024/2023-2024-Premier-League-Stats'

data = requests.get(standings_url)

# Squads Data for Scores and Fixtures
soup = BeautifulSoup(data.text, features = 'html.parser')
standings_table = soup.select('table.stats_table')[0]
links = standings_table.find_all('a')
links = [l.get('href') for l in links]
links = [l for l in links if '/squads/' in l]
team_urls = [f'https://fbref.com{l}' for l in links]

team_url = team_urls[0]
data = requests.get(team_url)

matches = pd.read_html(data.text, match = 'Scores & Fixtures')[0]

# Squads Shooting Stats
soup = BeautifulSoup(data.text)
links = soup.find_all('a')
links = [l.get('href') for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]

data = requests.get(f'https://fbref.com{links[0]}')
shooting = pd.read_html(data.text, match = 'Shooting')[0]

shooting.columns = shooting.columns.droplevel()

# Merging Scores and Shooting Data
team_data = matches.merge(shooting[['Date', 'Sh', 'SoT', 'Dist', 'FK', 'PK', 'PKatt']], on = 'Date')

