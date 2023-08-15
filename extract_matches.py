import requests
from bs4 import BeautifulSoup
from elo_ratings import EloRatings
from rich_pretty_print import PrettyResults
from config import MAP, user_agents
import pandas as pd
import datetime
import time
import random


class ExtractMatches:
    def __init__(
        self,
        comp,
        start_year,
        confidence=0.6,
        future_predictions=True,
        export_results=False,
        misc_league=False
    ):
        self.matches = {}
        self.future_matches = {}
        self.main_link = f"https://fbref.com/en/comps/{MAP[comp]['comp_id']}"
        self.confidence = confidence
        self.export_path = (
            f"archive/{start_year}-{datetime.date.today().year}-{comp}.csv"
        )

        # get played matches
        self.load_historic_data(start_year, comp)

        # extract current season played and scheduled matches
        self.extract_current_season_data(comp)

        # instantiate the PrettyResults class and pass its instance to pretty_query_interface()
        pretty = PrettyResults()

        # instantiate the EloRatings class and get the scheduled matches winning probability
        elo = EloRatings(matches=self.get_played_matches(), confidence=self.confidence, misc_league=misc_league)
        correct_pred, wrong_pred = elo.get_win_perc()

        if future_predictions:
            scheduled_matches = self.get_scheduled_matches()
            for k, v in scheduled_matches.items():
                try:
                    elo.pretty_query_interface(pretty,
                                               home_team_details=k,
                                               away_team=v,
                                               comp=comp,
                                               confidence=confidence)
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

        for match in matches:
            try:
                date = match.find("td", {"data-stat": "date"}).find("a").text
            except:
                date = None
            try:
                hour = match.find("td", {"data-stat": "start_time"}).find(
                    "span", {"class": "venuetime"}
                )["data-venue-time"]
            except:
                hour = None
            try:
                score = match.find("td", {"data-stat": "score"}).find("a").text
            except:
                score = None
            try:
                home_team = match.find("td", {"data-stat": "home_team"}).find("a").text
            except:
                home_team = None
            try:
                away_team = match.find("td", {"data-stat": "away_team"}).find("a").text
            except:
                away_team = None

            if score:
                key = f"{date} {hour} {home_team}"
                self.matches[key] = {
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": score.replace("–", "-")[0],
                    "away_score": score.replace("–", "-")[2],
                }
            elif date and hour:
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
        # extract or load played matches up until previous season
        try:
            data = pd.read_csv(self.export_path)

            date = data["date"].tolist()
            home_team = data["home_team"].tolist()
            away_team = data["away_team"].tolist()
            home_score = data["home_score"].tolist()
            away_score = data["away_score"].tolist()

            for i in range(len(date)):
                self.matches[f"{date[i]}_({i})"] = {
                    "home_team": home_team[i],
                    "away_team": away_team[i],
                    "home_score": home_score[i],
                    "away_score": away_score[i],
                }

        except OSError:
            self.extract_historic_data(start_year, comp)

    def get_played_matches(self):
        return self.matches

    def get_scheduled_matches(self):
        return self.future_matches
