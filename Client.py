import bs4
import pandas as pd
import urllib3
from bs4 import Comment
import time
import json


header_data = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64)'\
    ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 '\
    'Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9'\
    ',image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive'
}

# endpoints
def measurement_url(season):
    return "https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear={}".format(season)


def drills_url(season):
    return "https://stats.nba.com/stats/draftcombinedrillresults?LeagueID=00&SeasonYear={}".format(season)

def extract_table(url, season):
    r = http.request('GET', url, headers=header_data)
    resp = json.loads(r.data.decode('utf-8'))
    results = resp['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    frame = pd.DataFrame(rows)
    frame.columns = headers
    frame["SEASON"] = season
    return frame

years = range(2000, 2019)
seasons = ["{0}-{1}".format(years[i], str(years[i+1])[-2:]) for i in range(len(years)-1)]

http = urllib3.PoolManager()
measuments = []
drills = []
for season in seasons:
    print(season)
    measurement = extract_table(measurement_url(season),season)
    measuments.append(measurement)
    time.sleep(2)

    drill = extract_table(drills_url(season), season)
    drills.append(measurement)
    time.sleep(2)


measurement_frame = pd.concat(measuments)
drills_frame = pd.concat(drills)

measurement_frame.to_csv("data/Player_Combine_Measurements.csv")
drills_frame.to_csv("data/Player_Combine_Drills.csv")