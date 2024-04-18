from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import datetime as dt
import requests as rq
import csv
import re

### Text and interface

options = [*range(1990, 2050)]
options_update = ["yes", "no"]

print("Welcome to Procyclingstat.com Webscraber!")

while True:
    first_year = int(input("Choose from what year(yyyy) you want start from: "))

    if first_year not in options:
        print (first_year, "is not an option.")
        continue
    else:
        break

while True:
    last_year = int(input("Choose from what year(yyyy) you want end on: "))

    if last_year not in options:
        print (last_year, "is not an option.")
        continue

    elif last_year < first_year:
        print (last_year, "must be bigger or equal to", first_year)
    
    else:
        break

while True:
    full_race_update = input("Do you want a full rider update. Type yes or no: ").lower()

    if full_race_update not in options_update:
        print (full_race_update, "is not an option.")
        continue
    else:
        break

while True:
    full_rider_update = input("Do you want a full rider update. Type yes or no: ").lower()

    if full_rider_update not in options_update:
        print (full_rider_update, "is not an option.")
        continue
    else:
        break

while True:
    full_team_update = input("Do you want a full team update. Type yes or no: ").lower()

    if full_team_update not in options_update:
        print (full_rider_update, "is not an option.")
        continue
    else:
        break

last_year = last_year + 1
years = list(range(first_year,last_year))
years.sort(reverse=True)

### PREPARE TEMPORARY TABLES

csv_riders_races = open(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\riders_races.csv", "w", newline='', encoding='utf-16')
csv_races = open(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\races.csv", "w", newline='', encoding='utf-16')
csv_riders = open(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\riders.csv", "w", newline='', encoding='utf-16')
csv_riders_teams = open(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\riders_teams.csv", "w", newline='')
csv_teams = open(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\teams.csv", "w", newline='', encoding='utf-16')
csv_teams_teams = open(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\teams_teams.csv", "w", newline='', encoding='utf-16')

csv_writer_riders_races = csv.writer(csv_riders_races, delimiter=';')
csv_writer_races = csv.writer(csv_races, delimiter=';')
csv_writer_riders = csv.writer(csv_riders, delimiter=';')
csv_writer_riders_teams = csv.writer(csv_riders_teams, delimiter=';')
csv_writer_teams = csv.writer(csv_teams, delimiter=';')
csv_writer_teams_teams = csv.writer(csv_teams_teams, delimiter=';')

csv_writer_riders_races.writerow(["rider_tag", "race_tag", "team_tag", "rank"])
csv_writer_races.writerow(["race_tag", "race_start_date", "race_end_date", "date", "race_name", "avg_speed", "distance", "points_scale",
                            "uci_scale", "profilescore", "vert_meters", "race_ranking", "startlist_score", "won_how"])
csv_writer_riders.writerow(["rider_tag", "name", "team", "team_contract", "date_of_birth", "nationality", "weight", "height"])
csv_writer_riders_teams.writerow(["rider_tag", "team_tag"])
csv_writer_teams.writerow(["team_tag", "team_name", "team_status", "team_abbreviation", "bike_brand"])
csv_writer_teams_teams.writerow(["team_tag", "team_differenser"])

### SET PROXY

proxy = {"http" : "14acffbd295b7:07331a2d41@212.236.216.101:12323",
            "https" : "14acffbd295b7:07331a2d41@212.236.216.101:12323"}

### RACE AND RESULT EXTRACT BY YEAR

try:
    races_library = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\races.csv", sep=';', encoding='utf-16')

except:
    riders_library = pd.DataFrame()
    riders_library["race_tag"] = []

def transform_races(url_tag, race_start_date, race_end_date, race_category):
    url = f"https://www.procyclingstats.com/{url_tag}"
    site = rq.get(url, proxies=proxy)
    doc = bs(site.text, "html.parser")

    race = doc.find("ul", class_ = "infolist")

    race_tag = url.split("https://www.procyclingstats.com/race/", 1) [1]
    date = race.find_all("li")[0].text.split(": ", 1) [1]
    race_name = doc.find("h1").text
    avg_speed = race.find_all("li")[2].text.split(": ", 1) [1].split("km/h", 1) [0]
    distance = race.find_all("li")[4].text.split(":  ", 1) [1].split("km", 1) [0]
    points_scale = race.find_all("li")[5].find("a").text
    if len(points_scale) == 0:
        if "points" in race_tag:
            points_scale = race_category + ".Points"
        elif "kom" in race_tag:
            points_scale = race_category + ".Kom"
        elif "youth" in race_tag:
            points_scale = race_category + ".Youth"
        else:
            print("error")
    uci_scale = race.find_all("li")[6].text.split(": ", 1) [1]
    profilescore = race.find_all("li")[8].text.split(":  ", 1) [1]
    vert_meters = race.find_all("li")[9].text.split(": ", 1) [1]
    race_ranking = race.find_all("li")[12].text.split(": ", 1) [1]
    startlist_score = race.find_all("li")[13].text.split(": ", 1) [1]
    won_how = race.find_all("li")[14].text.split(":  ", 1) [1]
    csv_writer_races.writerow([race_tag, race_start_date, race_end_date, date, race_name, avg_speed, distance, points_scale, uci_scale, 
                                profilescore, vert_meters, race_ranking, startlist_score, won_how])

    sorting = doc.find_all(lambda tag: tag.name == "div" and tag.get("class") == ["result-cont"])
    results = sorting[0].find("tbody")

    try:
        for result in results.find_all("tr"):
            rider_tag = result.find_all("a")[0].get("href").split("rider/", 1)[1]
            try:
                team_tag = result.find_all("a")[1].get("href").split("team/", 1)[1]
            except:
                team_tag = "-"
            race_tag = url.split("https://www.procyclingstats.com/race/", 1) [1]
            rank = result.find_all("td")[0].text.strip()
            csv_writer_riders_races.writerow([rider_tag, race_tag, team_tag, rank])
        print(url_tag + " OK")
    except:
        for result in results.find_all("tr"):
            if "team" in result.attrs["class"]:
                rank = result.find_all("td")[0].text.strip()
                team_tag = result.find_all("td")[1].find("a").get("href").split("team/", 1)[1]
                continue
            rider_tag = result.find_all("a")[0].get("href").split("rider/", 1)[1]
            race_tag = url.split("https://www.procyclingstats.com/race/", 1) [1]
            csv_writer_riders_races.writerow([rider_tag, race_tag, team_tag, rank])
        print(url_tag + " OK")
def extract_2(race_url):
    site = rq.get(f"https://www.procyclingstats.com/{race_url}", proxies=proxy)
    doc = bs(site.text, "html.parser")
    race = doc.find("ul", class_ = "infolist")
    race_start_date = race.find_all("li")[0].text.split(": ", 1) [1]
    race_end_date = race.find_all("li")[0].text.split(": ", 1) [1]
    race_category = race.find_all("li")[5].find("a").text

    stagefind = doc.find("form", style= "  max-width: 250px; width: 100%;  ")
    try:
        first_stage = stagefind.find("option").get("value")
        site = rq.get(f"https://www.procyclingstats.com/{first_stage}", proxies=proxy)
        doc = bs(site.text, "html.parser")
        race = doc.find("ul", class_ = "infolist")
        race_start_date = race.find_all("li")[0].text.split(": ", 1) [1]

        for stage in stagefind.find_all("option"):
            if stage.text =="Teams classification":
                continue
            stage_tag = stage.get("value")
            transform_races(stage_tag, race_start_date, race_end_date, race_category)
    except:
        transform_races(race_url, race_start_date, race_end_date, race_category)
def extract_1(year):
    race_categories = ["1", "2", "13", "21", "26"]
    """UCI-PRO-series er 26, senere end 2020'erne"""
    """Junior er 15"""
    for sites in race_categories:
        site = rq.get(f"https://www.procyclingstats.com/races.php?year={year}&circuit={sites}&class=&filter=Filter", proxies=proxy)
        doc = bs(site.text, "html.parser")
        races = doc.find("tbody")

        for race in races.find_all("tr"):
            if "startlist/preview" in race.find("a").get("href"):
                continue
            elif "/nc-" in race.find("a").get("href"):
                continue
            elif (full_race_update == "no" and
                len(races_library[races_library["race_tag"].str.contains(race.find_all("a")[0].get("href").split("race/")[1])]) > 0):
                continue
            race_site = race.find_all("a")[0].get("href")
            extract_2(race_site)

for year in years:
    extract_1(year)

csv_riders_races.close()
csv_races.close()

races_extract = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\races.csv", sep=';', encoding='utf-16')

try:
    races_library = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\races.csv", sep=';', encoding='utf-16')
    races = pd.concat([races_extract, races_library])
    races = races.drop_duplicates()
except:
    races = races_extract

races.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\races.csv", index=False,  sep=';', encoding='utf-16')

riders_races_extract = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\riders_races.csv", sep=';', encoding='utf-16')

try:
    riders_races_library = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\riders_races.csv", sep=';', encoding='utf-16')
    riders_races = pd.concat([riders_races_extract, riders_races_library])
    riders_races = riders_races.drop_duplicates()
except:
    riders_races = riders_races_extract

riders_races.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\riders_races.csv", index=False,  sep=';', encoding='utf-16')


### FIND RIDERS FROM THE RACE RESULTS

riders_races_gb = riders_races['rider_tag'].value_counts().to_frame('count').rename_axis('rider_tag').reset_index()
del riders_races_gb["count"]

if full_rider_update == "no":
    try:
        rider = pd.read_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\riders.csv", sep=';', encoding='utf-16')
        riders_gb = rider['rider_tag'].value_counts().to_frame('count').rename_axis('rider_tag').reset_index()
        del riders_gb["count"]
        new_riders = pd.concat([riders_races_gb, riders_gb, riders_gb])
        new_riders.drop_duplicates(keep=False, inplace=True)
        new_riders = new_riders.reset_index(drop = True)
    except:
        new_riders = riders_races_gb
else:
    new_riders = riders_races_gb

for riders in range(len(new_riders)):
    rider_tag = new_riders["rider_tag"][riders]
    url = f"https://www.procyclingstats.com/rider/{rider_tag}"
    site = rq.get(url, proxies=proxy)
    doc = bs(site.text, "html.parser")

    rider_doc = doc.find("div", class_="rdr-info-cont")

    name_with_spaces = doc.find("h1").text
    name = " ".join(name_with_spaces.split())
    try:
        team = doc.find("span", class_="red hideIfMobile").text
    except:
        team = "-"
    try:
        team_contract = doc.find("div", class_="right w25 mb_w100 mb_mt10").find("li").find("a").get("href").split("team/", 1)[1]
    except:
        team_contract = "-"
    try:
        date = rider_doc.b.next_sibling.strip()
        month = rider_doc.sup.next_sibling.strip().split(" (", 1)[0]
        date_of_birth = f"{date} {month}".lower()
    except:
        date_of_birth = "-"
    try:    
        nationality = rider_doc.find("a").text
    except:
        nationality = "-"
    weight = "-"
    height = "TEST"
    try:
        if rider_doc.find_all("b")[2].text.lower() == "weight:":
            weight = rider_doc.find_all("b")[2].next_sibling.strip().split(" kg", 1)[0]
        elif rider_doc.find_all("b")[2].text.lower() == "height:":
            height = rider_doc.find_all("b")[2].next_sibling.strip().split(" m", 1)[0]
    except:
        weight = "-"
    if height == "TEST":
        try:
            height = rider_doc.find_all("b")[3].next_sibling.strip().split(" m", 1)[0]
        except:
            height = "-"
    csv_writer_riders.writerow([rider_tag, name, team, team_contract, date_of_birth, nationality, weight, height])
    print(name + " OK")

csv_riders.close()
riders = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\riders.csv", sep=';', encoding='utf-16')

try:
    riders_finish = pd.concat([rider, riders])
    riders_finish = riders_finish.drop_duplicates()
except:
    riders_finish = riders

riders_finish.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\riders.csv", index=False,  sep=';', encoding='utf-16')

### FIND TEAMS AND RIDERS TEAMS FROM RACE RESULTS

riders = pd.read_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\riders_races.csv", sep=';', encoding='utf-16')
teams_gb = riders['team_tag'].value_counts().to_frame('count').rename_axis('team_tag').reset_index()
del teams_gb["count"]

if full_team_update == "no":
    try:
        team = pd.read_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\teams.csv", sep=';', encoding='utf-16')
        team_gb = team["team_tag"].value_counts().to_frame('count').rename_axis('team_tag').reset_index()
        del team_gb["count"]
        new_teams = pd.concat([teams_gb, team_gb, team_gb])
        new_teams.drop_duplicates(keep=False, inplace=True)
        new_teams = new_teams.reset_index(drop = True)
    except:
        new_teams = teams_gb
else:
    new_teams = teams_gb

for teams in range(len(new_teams)):
    if len(new_teams["team_tag"][teams]) < 2:
        continue
    team_tag = new_teams["team_tag"][teams]
    url = f"https://www.procyclingstats.com/team/{team_tag}"
    site = rq.get(url, proxies=proxy)
    doc = bs(site.text, "html.parser")
    team_name = doc.find("h1").text
    if "(NAT)" in team_name:
        continue
    team_name = doc.find("h1").text.split(" (")[0]
    team_info = doc.find("ul", class_="infolist")
    try:
        team_status = team_info.find("li").text.split("Team status: ")[1]
    except:
        team_status = "-"
    try:
        team_abbreviation = team_info.find_all("li")[1].text.split(":  ")[1]
    except:
        team_abbreviation = "-"
    try:
        bike_brand = team_info.find_all("li")[2].text.split(": ")[1]
    except:
        bike_brand = "-"
    csv_writer_teams.writerow([team_tag, team_name, team_status, team_abbreviation, bike_brand])
    print(team_tag + " OK")
    rider_find = doc.find("ul", class_="list pad2")

    for rider in rider_find.find_all("li"):
        rider_tag = rider.find_all("a")[0].get("href").split("rider/", 1)[1]
        csv_writer_riders_teams.writerow([rider_tag, team_tag])

csv_teams.close()
csv_riders_teams.close()

teams = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\teams.csv", sep=';', encoding='utf-16')

try:
    teams_finish = pd.concat([team, teams])
    teams_finish = teams_finish.drop_duplicates()
except:
    teams_finish = teams

teams_finish.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\teams.csv", index=False,  sep=';', encoding='utf-16')

riders_teams = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\riders_teams.csv", sep=';')

try:
    rider_team = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\riders_teams.csv", sep=';')
    riders_teams_finish = pd.concat([rider_team, riders_teams])
    riders_teams_finish = riders_teams_finish.drop_duplicates()
except:
    riders_teams_finish = riders_teams

riders_teams_finish.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\riders_teams.csv", index=False,  sep=';')


### Connecting teams from year to year to each other

teams = pd.read_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\teams.csv", sep=';', encoding='utf-16')
teams_gb = teams['team_tag'].value_counts().to_frame('count').rename_axis('team_tag').reset_index()
del teams_gb["count"]

if full_team_update == "no":
    try:
        teams_teams = pd.read_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\teams_teams.csv", sep=';', encoding='utf-16')
        teams_teams_gb = teams_teams['team_differenser'].value_counts().to_frame('count').rename_axis('team_tag').reset_index()
        del teams_teams_gb["count"]
        new_teams = pd.concat([teams_gb, teams_teams_gb, teams_teams_gb])
        new_teams.drop_duplicates(keep=False, inplace=True)
        new_teams = new_teams.reset_index(drop = True)
    except:
        new_teams = teams_gb
else:
    new_teams = teams_gb

for teams in range(len(new_teams)):
    team_differenser = new_teams["team_tag"][teams]
    url = f"https://www.procyclingstats.com/team/{team_differenser}"
    site = rq.get(url, proxies=proxy)
    doc = bs(site.text, "html.parser")
    for team in doc.find("div", class_="pageSelectNav").find_all("option"):
        team_tag = team.get("value").split("team/")[1].split("/overview/")[0]
        csv_writer_teams_teams.writerow([team_tag, team_differenser])
    print(team_differenser)

csv_teams_teams.close()

team_team = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_extract\teams_teams.csv", sep=';', encoding='utf-16')

try:
    teams_teams_finish = pd.concat([teams_teams, team_team])
    teams_teams_finish = teams_teams_finish.drop_duplicates()

except:
    teams_teams_finish = team_team

teams_teams_finish = teams_teams_finish.sort_values(["team_differenser"], ascending=False)
teams_teams_finish = teams_teams_finish.drop_duplicates(subset=["team_tag"])

teams_teams_finish.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_library\teams_teams.csv", index=False,  sep=';', encoding='utf-16')

print("team_differenser OK")

### FINALIZE TRANSFORM AND LOAD

teams_teams = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\teams_teams.csv", sep=';', encoding='utf-16')
teams_teams["team_differenser_id"] = pd.factorize(teams_teams["team_differenser"])[0]

teams = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\teams.csv", sep=';', encoding='utf-16')
teams["team_id"] = pd.factorize(teams["team_tag"])[0]
teams = pd.merge(teams, teams_teams, on="team_tag", how="left")
teams = teams[["team_id", "team_differenser_id", "team_name", "team_tag", "team_status", "bike_brand", "team_abbreviation"]]
teams.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_finish\teams.csv", index=False,  sep=';', encoding='utf-16')
print("teams.csv OK")

riders = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\riders.csv", sep=';', encoding='utf-16')
riders["rider_id"] = pd.factorize(riders["rider_tag"])[0]
riders = riders[["rider_id", "name", "team", "date_of_birth", "nationality", "weight", "height", "team_contract", "rider_tag"]]
riders.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_finish\riders.csv", index=False,  sep=';', encoding='utf-16')
print("riders.csv OK")

races = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\races.csv", sep=';', encoding='utf-16')
races["race_id"] = pd.factorize(races["race_tag"])[0]
races = races[["race_id", "race_start_date", "race_end_date", "date", "race_name", "avg_speed", "distance", "points_scale",
                            "profilescore", "vert_meters", "race_ranking", "startlist_score", "won_how", "race_tag"]]
races.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_finish\races.csv", index=False,  sep=';', encoding='utf-16')
print("races.csv OK")

riders_races = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\riders_races.csv", sep=';', encoding='utf-16')
riders_races = pd.merge(riders, riders_races, on="rider_tag", how="outer")
riders_races = riders_races[["rider_id", "race_tag", "rank"]]
riders_races = pd.merge(races, riders_races, on="race_tag", how="outer")
riders_races = riders_races[["rider_id", "race_id", "rank"]]
riders_races.loc[riders_races["rank"] == "DNS", "rank"] = "666"
riders_races.loc[riders_races["rank"] == "DNF", "rank"] = "777"
riders_races.loc[riders_races["rank"] == "OTL", "rank"] = "888"
riders_races.loc[riders_races["rank"] == "DSQ", "rank"] = "999"
riders_races.loc[riders_races["rank"] == "DF", "rank"] = "998"
riders_races.loc[riders_races["rank"] == "-", "rank"] = "997"
riders_races = riders_races.dropna(subset="rank")
riders_races.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_finish\riders_races.csv", index=False,  sep=";")
print("riders_races.csv OK")

riders_teams = pd.read_csv(r"C:\\Users\\clemm\\Desktop\\Python\\Procycling\\csv_library\riders_teams.csv", sep=';')
riders_teams = pd.merge(riders_teams, riders, on="rider_tag", how="right")
riders_teams = pd.merge(riders_teams, teams, on="team_tag", how="left")
riders_teams = riders_teams[["rider_id", "team_id"]]
riders_teams.to_csv(r"C:\\Users\clemm\Desktop\Python\Procycling\csv_finish\riders_teams.csv", index=False,  sep=';')
print("riders_teams.csv OK")