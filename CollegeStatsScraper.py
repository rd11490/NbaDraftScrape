import re

import bs4
import pandas as pd
import urllib3
from bs4 import Comment

import MapOfList

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def extract_column_names(table, cbb_id = False):
    columns = [col["data-stat"] for col in table.find_all("thead")[0].find_all("th")]
    columns.append("id")
    if cbb_id:
        columns.append("cbb_id")
    return [col for i, col in enumerate(columns)]


def extract_rows(table, id, cbb_id = None):
    rows = table.find_all("tbody")[0].find_all("tr")
    return [parse_row(r, id, cbb_id) for r in rows]


def parse_row(row, id, cbb_id = None):
    rank = row.find_all("th")[0].string
    other_data = row.find_all("td")
    row_data = [td.string for i, td in enumerate(other_data)]
    row_data.insert(0, rank)
    row_data.append(id)
    if cbb_id:
        row_data.append(cbb_id)
    return row_data


def extract_cbb_link(id):
    r = http.request('GET', player_page(id))
    soup = bs4.BeautifulSoup(r.data, 'html')
    nav = soup.find_all("div", {"id": "bottom_nav"})[0]
    links = [l['href'] for l in nav.find_all("a") if l.has_attr('href') and "cbb/players" in l['href']]
    return links


def extract_per_100_pos_cbb(soup, id, cbb_id):
    f = soup.find_all("div", {"id": "all_players_per_poss"})
    if len(f) > 0:
        div = f[0]
        table = div.find_all(string=lambda text: isinstance(text, Comment))[0]
        new_soup = bs4.BeautifulSoup(table, 'html')
        new_table = new_soup.find_all("table")[0]

        return extract_column_names(new_table, True), extract_rows(new_table, id, cbb_id)
    return None, None


def extract_advanced_cbb(soup, id, cbb_id):
    f = soup.find_all("div", {"id": "all_players_advanced"})
    if len(f) > 0:
        div = f[0]
        table = div.find_all(string=lambda text: isinstance(text, Comment))[0]
        new_soup = bs4.BeautifulSoup(table, 'html')

        new_table = new_soup.find_all("table")[0]
        return extract_column_names(new_table, True), extract_rows(new_table, id, cbb_id)
    return None, None


def extract_per_100_pos_nba(soup, id):
    f = soup.find_all("div", {"id": "all_per_poss"})
    if len(f) > 0:
        div = f[0]
        table = div.find_all(string=lambda text: isinstance(text, Comment))[0]
        new_soup = bs4.BeautifulSoup(table, 'html')
        new_table = new_soup.find_all("table")[0]

        return extract_column_names(new_table), extract_rows(new_table, id)
    return None, None


def extract_advanced_nba(soup, id):
    f = soup.find_all("div", {"id": "all_advanced"})
    if len(f) > 0:
        div = f[0]
        table = div.find_all(string=lambda text: isinstance(text, Comment))[0]
        new_soup = bs4.BeautifulSoup(table, 'html')

        new_table = new_soup.find_all("table")[0]
        return extract_column_names(new_table), extract_rows(new_table, id)
    return None, None


def parse_id_from_cbb_link(link):
    return re.search('players/(.*).html', link, re.IGNORECASE).group(1)


def player_page(id):
    return "https://www.basketball-reference.com/players/{0}/{1}.html".format(id[0], id)


http = urllib3.PoolManager()

players = pd.read_csv("data/PlayerList.csv")
player_ids = players[["First year", "Last year", "id"]]

player_map = {}
for index, row in player_ids.iterrows():
    player_map[row["id"]] = (row["First year"], row["Last year"])

ids = list(player_ids["id"])

columns_cbb_100_pos = {}
rows_cbb_100_pos = MapOfList.MapOfList()

columns_cbb_adv = {}
rows_cbb_adv = MapOfList.MapOfList()

columns_nba_adv = {}
rows_nba_adv = MapOfList.MapOfList()

columns_nba_100_pos = {}
rows_nba_100_pos = MapOfList.MapOfList()

for id in ids:
    print(id)
    links = extract_cbb_link(id)

    r = http.request('GET', player_page(id))
    soup = bs4.BeautifulSoup(r.data, 'html')

    columns, rows = extract_advanced_nba(soup, id)
    if columns:
        columns_nba_adv[len(columns)] = columns
    if rows and len(rows) > 0:
        rows_nba_adv.add(len(rows[0]), rows)

    columns, rows = extract_per_100_pos_nba(soup, id)
    if columns:
        columns_nba_100_pos[len(columns)] = columns
    if rows and len(rows) > 0:
        rows_nba_100_pos.add(len(rows[0]), rows)

    if len(links) > 0:
        cbb_link = links[0]
        cbb_id = parse_id_from_cbb_link(cbb_link)

        r = http.request('GET', cbb_link)
        soup = bs4.BeautifulSoup(r.data, 'html')
        columns, rows = extract_per_100_pos_cbb(soup, id, cbb_id)
        if columns:
            columns_cbb_100_pos[len(columns)] = columns
        if rows and len(rows) > 0:
            rows_cbb_100_pos.add(len(rows[0]), rows)

        columns, rows = extract_advanced_cbb(soup, id, cbb_id)
        if columns:
            columns_cbb_adv[len(columns)] = columns
        if rows and len(rows) > 0:
            rows_cbb_adv.add(len(rows[0]), rows)

for k in rows_cbb_100_pos.map_collection.keys():
    frame_100_pos = pd.DataFrame()

    for r in rows_cbb_100_pos.map_collection[k]:
        frame_100_pos = frame_100_pos.append(pd.Series(r), ignore_index=True)

    frame_100_pos.columns = columns_cbb_100_pos[k]
    frame_100_pos.to_csv("data/Per100PosCollegeNumbers_{}_columns.csv".format(k))

for k in rows_cbb_adv.map_collection.keys():
    frame_adv = pd.DataFrame()

    for r in rows_cbb_adv.map_collection[k]:
        frame_adv = frame_adv.append(pd.Series(r), ignore_index=True)

    frame_adv.columns = columns_cbb_adv[k]
    frame_adv.to_csv("data/AdvancedCollegeNumbers_{}_columns.csv".format(k))

for k in rows_nba_100_pos.map_collection.keys():
    frame_100_pos = pd.DataFrame()

    for r in rows_nba_100_pos.map_collection[k]:
        frame_100_pos = frame_100_pos.append(pd.Series(r), ignore_index=True)

    frame_100_pos.columns = columns_nba_100_pos[k]
    frame_100_pos.to_csv("data/Per100PosNBANumbers_{}_columns.csv".format(k))

for k in rows_nba_adv.map_collection.keys():
    frame_adv = pd.DataFrame()

    for r in rows_nba_adv.map_collection[k]:
        frame_adv = frame_adv.append(pd.Series(r), ignore_index=True)

    frame_adv.columns = columns_nba_adv[k]
    frame_adv.to_csv("data/AdvancedNBANumbers_{}_columns.csv".format(k))
