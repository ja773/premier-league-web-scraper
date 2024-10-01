import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from io import StringIO

# Data Scraping from 19/20 season to 23/24 season
years = list(range(2024,2021,-1))
all_matches = []

for year in years:
    standings_url = 'https://fbref.com/en/comps/9/Premier-League-Stats'

    data = requests.get(standings_url, 'lxml')

    # Squads Data for Scores and Fixtures
    soup = BeautifulSoup(data.text, features = 'lxml')

    time.sleep(1)

    print('fetching data for ',year)

    standings_table = soup.select('table.stats_table')[0]
    links = standings_table.find_all('a')
    links = [l.get('href') for l in links]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f'https://fbref.com{l}' for l in links]

    # Finding URL for previous season
    previous_season = soup.select('a.prev')[0].get('href')
    standings_url = f'https://fbref.com{previous_season}'

    # Iterate through all squads
    for team_url in team_urls:
        team_name = team_url.split('/')[-1].replace('-Stats','').replace('-','')

        data = requests.get(team_url, 'lxml')

        matches = pd.read_html(StringIO(data.text), match = 'Scores & Fixtures')[0]

        # Squads Shooting Stats
        soup = BeautifulSoup(data.text,features = 'lxml')
        links = soup.find_all('a')
        links = [l.get('href') for l in links]
        links = [l for l in links if l and 'all_comps/shooting/' in l]

        data = requests.get(f'https://fbref.com{links[0]}', 'lxml')
        try:
            shooting = pd.read_html(StringIO(data.text), match = 'Shooting')[0]
        except ValueError:
            continue

        shooting.columns = shooting.columns.droplevel()

        # Merging Scores and Shooting Data
        try:
            team_data = matches.merge(shooting[['Date', 'Sh', 'SoT', 'Dist', 'FK', 'PK', 'PKatt']], on = 'Date')
        except ValueError:
            continue

        team_data = team_data[team_data['Comp'] == 'Premier League']
        team_data['Season'] = year
        team_data['Team'] = team_name
        all_matches.append(team_data)

        # Delay to prevent scraping too quickly
        time.sleep(5)

# Combining all data frames
match_df = pd.concat(all_matches)

#Export to CSV
match_df.to_csv('matches.csv')

