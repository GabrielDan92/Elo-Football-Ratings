import requests
from bs4 import BeautifulSoup
from config import MAP, user_agents
from postgres import PostgreSQL
import datetime
import time
import random


class ExtractMatches:
    """
    A class to extract and manage match data for domestic and international leagues.

    This class provides methods to extract and store historic and future match data for a given competition.
    It supports HTML parsing, exporting data to CSV, and loading data from previous extractions.

    Attributes:
        matches (dict): Played match data dictionary.
        future_matches (dict): Future match data dictionary.
        main_link (str): Base URL for fetching competition data.
        export_path (str): Path for exporting match data to CSV.

    Methods:
        extract_historic_data(start_year, comp): Extract historic match data.
        extract_current_season_data(comp): Extract current season match data.
        parse_html(url): Parse HTML content and extract match information.
        export_historic_data(): Export played match data to CSV.
        load_historic_data(start_year, comp): Load historic match data.
        get_played_matches(): Get played match data dictionary.
        get_future_matches(): Get future match data dictionary.

    Parameters:
        comp (str): Competition name.
        start_year (int): Starting year for data extraction.
    """
    def __init__(self, comp, start_year):
        self.matches = {}
        self.future_matches = {}
        self.main_link = f"https://fbref.com/en/comps/{MAP[comp]['comp_id']}"
        self.export_path = f"archive/{start_year}-{datetime.date.today().year}-{comp}.csv"
        self.comp = comp
        self.db = PostgreSQL()

        # get played matches from start year until previous year
        self.load_historic_data(start_year)

        # extract current year's played and future matches
        self.extract_current_season_data()
        
    def load_historic_data(self, start_year):
        query_records_count = "SELECT count(*) from played_games WHERE date_hour LIKE %s AND competition = %s"
        values = (f"{start_year}%", self.comp)
        records_count = self.db.query(query_records_count, values)[0][0]

        if records_count == 0:
            # extract the matches if they are not already saved in the db
            self.extract_historic_data(start_year)
        else:
            # load the matches from the db
            query = f"""SELECT * from played_games WHERE competition = '{self.comp}'"""

            records = self.db.query(query)

            for i, record in enumerate(records):
                self.matches[f"{record[0]}_({i})"] = {
                    "home_team": record[1],
                    "away_team": record[2],
                    "home_score": record[3],
                    "away_score": record[4],
                }

    def extract_historic_data(self, start_year):
        curr_year = datetime.date.today().year

        while start_year < curr_year:
            if "custom_link" in MAP[self.comp].keys():
                years = f"{start_year + 1}"
                if start_year == curr_year - 1:
                    break
            else:
                years = f"{start_year}-{start_year + 1}"

            url = f"{self.main_link}/{years}/schedule/{years}-{MAP[self.comp]['suffix']}"
            self.parse_html(url=url)
            start_year += 1

        # save the extracted matches locally to prevent extracting them in next runs
        self.export_historic_data()

    def extract_current_season_data(self):
        url = f"{self.main_link}/schedule/{MAP[self.comp]['suffix']}"
        self.parse_html(url=url)

    def parse_html(self, url):
        print(f"Access {url}")
        headers = {'User-Agent': random.choice(user_agents)}
        html = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(html.text, "html.parser")
        matches = soup.find("table").find("tbody").find_all("tr")

        def find_info(element, stat, sub_stat=None, sub_attr=None):
            try:
                info = element.find("td", {"data-stat": stat})
                if sub_stat and sub_attr:
                    sub_info = info.find(sub_stat)
                    return sub_info[sub_attr] if sub_info and sub_attr in sub_info.attrs else None
                else:
                    return info.find("a").text
            except:
                return None

        for match in matches:
            date = find_info(match, "date")
            hour = find_info(match, "start_time", "span", "data-venue-time")
            score = find_info(match, "score")
            home_team = find_info(match, "home_team")
            away_team = find_info(match, "away_team")

            if score:
                # we either have a score, so this is a played game
                key = f"{date} {hour} {home_team}"
                self.matches[key] = {
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": score.replace("–", "-")[0],
                    "away_score": score.replace("–", "-")[2],
                }
            elif date and hour:
                if datetime.datetime.strptime(date, "%Y-%m-%d").date() >= datetime.date.today():
                    # or we don't have a score, so this is a future game *if it has a scheduled date & hour
                    self.future_matches[date, hour, home_team] = away_team

        # prevent making more than 20 requests per minute
        time.sleep(3.1)
                
    def export_historic_data(self):
        # TODO: move the queries in queries.py
        query = """
            INSERT INTO played_games (date_hour, home_team, away_team, home_score, away_score, competition)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (date_hour, home_team) DO NOTHING
        """

        values = [(
            f"{date.split(' ')[0]}, {date.split(' ')[1]}",
            v["home_team"],
            v["away_team"],
            v["home_score"],
            v["away_score"],
            self.comp)
            for date, v in self.matches.items()]

        self.db.batch_insert(query, values)

    def get_played_matches(self):
        return self.matches

    def get_future_matches(self):
        return self.future_matches
