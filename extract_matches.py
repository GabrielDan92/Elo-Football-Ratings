import requests
from bs4 import BeautifulSoup
from elo_ratings import EloRatings
from rich_table import RichTable
from config import MAP, user_agents
import pandas as pd
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
        confidence (float): Match prediction confidence level.
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
        confidence (float): Match prediction confidence level.
        export_results (bool): Export match results to CSV (default: False).
        misc_league (bool): Miscellaneous league indicator (default: False).
    """
    def __init__(
        self,
        comp,
        start_year,
        confidence,
        export_results=False,
        misc_league=False
    ):
        self.matches = {}
        self.future_matches = {}
        self.main_link = f"https://fbref.com/en/comps/{MAP[comp]['comp_id']}"
        self.confidence = confidence
        self.export_path = f"archive/{start_year}-{datetime.date.today().year}-{comp}.csv"

        # get played matches from start year until previous year
        self.load_historic_data(start_year, comp)

        # extract current year's played and future matches
        self.extract_current_season_data(comp)

        # instantiate the EloRatings class, get the future matches winning prob and write the results in a table
        elo = EloRatings(matches=self.get_played_matches(), confidence=self.confidence, misc_league=misc_league)

        for k, v in self.get_future_matches().items():
            try:
                elo.get_win_prob_write_table(
                    RichTable(),
                    home_team_details=k,
                    away_team=v,
                    comp=comp,
                    confidence=confidence
                )
            except:
                continue

        if export_results:
            elo.export_results(competition_name=comp)

    def extract_historic_data(self, start_year, comp):
        curr_year = datetime.date.today().year

        while start_year < curr_year:
            if "custom_link" in MAP[comp].keys():
                years = f"{start_year + 1}"
            else:
                years = f"{start_year}-{start_year + 1}"

            url = f"{self.main_link}/{years}/schedule/{years}-{MAP[comp]['suffix']}"
            self.parse_html(url=url)
            start_year += 1

        # save the extracted matches locally to prevent extracting them in next runs
        self.export_historic_data()

    def extract_current_season_data(self, comp):
        url = f"{self.main_link}/schedule/{MAP[comp]['suffix']}"
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
                # or we don't have a score, so this is a future game *if it has a scheduled date & hour
                self.future_matches[date, hour, home_team] = away_team

        # prevent making more than 20 requests per minute
        time.sleep(3.1)

    def export_historic_data(self):
        pd.DataFrame(
            {
                "date": self.matches.keys(),
                "home_team": [v["home_team"] for v in self.matches.values()],
                "away_team": [v["away_team"] for v in self.matches.values()],
                "home_score": [v["home_score"] for v in self.matches.values()],
                "away_score": [v["away_score"] for v in self.matches.values()],
            }
        ).to_csv(self.export_path, encoding="utf-8-sig")

    def load_historic_data(self, start_year, comp):
        # extract or load played matches from start year until previous year
        try:
            data = pd.read_csv(self.export_path)

            for i, row in data.iterrows():
                date = row["date"]
                home_team = row["home_team"]
                away_team = row["away_team"]
                home_score = row["home_score"]
                away_score = row["away_score"]

                self.matches[f"{date}_({i})"] = {
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                }

        except OSError:
            # extract the matches if they are not already saved locally
            self.extract_historic_data(start_year, comp)

    def get_played_matches(self):
        return self.matches

    def get_future_matches(self):
        return self.future_matches
