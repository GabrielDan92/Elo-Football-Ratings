import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


class ExtractMatches:

    def __init__(self, comp="RO-Liga-1", start_year=2019, extract_historic_data=False):
        self.matches = {}
        self.future_matches = {}
        self.map = {
            "RO-Liga-1": {
                "suffix": "Liga-I-Scores-and-Fixtures",
                "comp_id": 47,
                "date_col": 1,
                "hour_col": 2,
                "home_team_col": 3,
                "score_col": 4,
                "away_team_col": 5,
                "date_col_h": 2,
                "hour_col_h": 3,
                "home_team_col_h": 4,
                "score_col_h": 5,
                "away_team_col_h": 6
            },
            "UK-Premier-League": {
                "suffix": "Premier-League-Scores-and-Fixtures",
                "comp_id": 9,
                "date_col": 1,
                "hour_col": 2,
                "home_team_col": 3,
                "score_col": 5,
                "away_team_col": 7,
                "date_col_h": 1,
                "hour_col_h": 2,
                "home_team_col_h": 3,
                "score_col_h": 5,
                "away_team_col_h": 7
            },
        }

        self.main_link = "https://fbref.com/en/comps/"
        self.export_path = "/Users/{user}/Desktop/Stuff/Football Spark/" \
                           f"{start_year}-{datetime.date.today().year}-{comp}.csv"

        if extract_historic_data:
            self.extract_historic_data(
                start_year=start_year,
                competition_id=self.map[comp]["comp_id"],
                suffix=self.map[comp]["suffix"],
                comp=comp
            )
        else:
            self.load_historic_data()

        self.extract_current_season_data(
            competition_id=self.map[comp]["comp_id"],
            suffix=self.map[comp]["suffix"],
            comp=comp
        )

    def extract_historic_data(
        self,
        start_year,
        competition_id,
        suffix,
        comp
    ):

        while start_year < datetime.date.today().year:
            url = f"{self.main_link}/{competition_id}/{start_year}-{start_year + 1}" \
                  f"/schedule/{start_year}-{start_year + 1}-{suffix}"
            print(f"Accessing {url}...")

            columns = [
                self.map[comp]["date_col_h"],
                self.map[comp]["home_team_col_h"],
                self.map[comp]["score_col_h"],
                self.map[comp]["away_team_col_h"],
                self.map[comp]["hour_col_h"]
            ]

            self.parse_html(requests.get(url=url), columns)
            start_year += 1

        self.export_historic_data()

    def extract_current_season_data(self, competition_id, suffix, comp):
        current_season = f"{self.main_link}/{competition_id}/schedule/{suffix}"
        print(f"Accessing {current_season}...")

        columns = [
            self.map[comp]["date_col"],
            self.map[comp]["home_team_col"],
            self.map[comp]["score_col"],
            self.map[comp]["away_team_col"],
            self.map[comp]["hour_col"]
        ]

        self.parse_html(requests.get(url=current_season), columns)

    def parse_html(self, html, columns):
        soup = BeautifulSoup(html.text, "html.parser")
        matches = soup.find("table").find("tbody").find_all("tr")

        for match in matches:
            try:
                date = match.find_all("td")[columns[0]].text
                hour = match.find_all("td")[columns[4]].text
                score = match.find_all("td")[columns[2]].text

                if score:
                    key = f'{date} {hour}'
                    self.matches[key] = {
                        "home_team": match.find_all("td")[columns[1]].text,
                        "away_team": match.find_all("td")[columns[3]].text,
                        "home_score": score.replace("–", "-")[0],
                        "away_score": score.replace("–", "-")[2],
                    }
                else:
                    if date and hour:
                        self.future_matches[match.find_all("td")[columns[1]].text] = match.find_all("td")[columns[3]].text
            except:
                continue

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

    def load_historic_data(self):
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
            
    def get_matches(self):
        return self.matches
    
    def get_future_matches(self):
        return self.future_matches


class EloRatings:
    def __init__(self, matches_dict):
        self.matches = matches_dict
        self.correct_pred = 0
        self.wrong_pred = 0
        self.elo = self.calculate_elo()

    def calculate_elo(self):
        elo = {"teams": {}, "ratings": {}}

        for k in self.matches.keys():
            home_t = self.matches[k]["home_team"]
            away_t = self.matches[k]["away_team"]

            # keep track of matches played
            if home_t not in elo["teams"]:
                elo["teams"][home_t] = 1
            else:
                elo["teams"][home_t] = elo["teams"][home_t] + 1

            if away_t not in elo["teams"]:
                elo["teams"][away_t] = 1
            else:
                elo["teams"][away_t] = elo["teams"][away_t] + 1

            try:
                home_s = int(self.matches[k]["home_score"])
                away_s = int(self.matches[k]["away_score"])
            except:
                self.matches[k]["prediction"] = None
                self.matches[k]["elo_home_bef"] = None
                self.matches[k]["elo_home_aft"] = None
                self.matches[k]["elo_away_bef"] = None
                self.matches[k]["elo_away_aft"] = None
                continue

            # add default ratings
            if home_t not in elo["ratings"]:
                elo["ratings"][home_t] = 1500
            if away_t not in elo["ratings"]:
                elo["ratings"][away_t] = 1500

            if elo["teams"][home_t] >= 30 and elo["teams"][away_t] >= 30:
                win_prob = self.winning_prob(elo["ratings"][home_t], elo["ratings"][away_t])
                
                self.matches[k]["prediction"] = round(win_prob, 2)
                self.matches[k]["elo_home_bef"] = elo["ratings"][home_t]
                self.matches[k]["elo_away_bef"] = elo["ratings"][away_t]
                
                self.measure_win_perc(win_prob=win_prob, home_s=home_s, away_s=away_s)

                # prevent rating inflation
                if elo["ratings"][home_t] < 1000:
                    k_home = 40
                if 1000 <= elo["ratings"][home_t] <= 1500:
                    k_home = 20
                if elo["ratings"][home_t] > 1500:
                    k_home = 10

                if elo["ratings"][away_t] < 1000:
                    k_away = 40
                if 1000 <= elo["ratings"][away_t] <= 1500:
                    k_away = 20
                if elo["ratings"][away_t] > 1500:
                    k_away = 10

                if home_s > away_s:
                    elo["ratings"][home_t] = round(
                        elo["ratings"][home_t] + k_home * (1 - win_prob)
                    )
                    elo["ratings"][away_t] = round(
                        elo["ratings"][away_t] + k_away * (0 - win_prob)
                    )

                if home_s < away_s:
                    elo["ratings"][home_t] = round(
                        elo["ratings"][home_t] + k_home * (0 - win_prob)
                    )
                    elo["ratings"][away_t] = round(
                        elo["ratings"][away_t] + k_away * (1 - win_prob)
                    )

                if home_s == away_s:
                    elo["ratings"][home_t] = round(
                        elo["ratings"][home_t] + k_home * (0.5 - win_prob)
                    )
                    elo["ratings"][away_t] = round(
                        elo["ratings"][away_t] + k_away * (0.5 - win_prob)
                    )

                self.matches[k]["elo_home_aft"] = elo["ratings"][home_t]
                self.matches[k]["elo_away_aft"] = elo["ratings"][away_t]
            else:
                self.matches[k]["prediction"] = None
                self.matches[k]["elo_home_bef"] = None
                self.matches[k]["elo_home_aft"] = None
                self.matches[k]["elo_away_bef"] = None
                self.matches[k]["elo_away_aft"] = None

        return elo

    def winning_prob(self, home_rating, away_rating):
        # probability of winning
        return 1 / (1+pow(10,(away_rating - home_rating) / 600))

    def query_interface(self, home_team, away_team):
        win_prob = self.winning_prob(self.elo["ratings"][home_team], self.elo["ratings"][away_team])

        s = ""
        if self.elo["teams"][home_team] < 30:
            s += f"Keep in mind that {home_team} has only {self.elo['teams'][home_team]} matches played. "

        if self.elo["teams"][away_team] < 30:
            s += f"Keep in mind that {away_team} has only {self.elo['teams'][away_team]} matches played."

        print(
            f"{home_team} [Elo: {self.elo['ratings'][home_team]}] has a {round(win_prob * 100)}% chance to win against "
            f"{away_team} [Elo: {self.elo['ratings'][away_team]}]. {s}"
        )

    def measure_win_perc(self, win_prob, home_s, away_s):
        if win_prob >= 0.6 and home_s > away_s:
            self.correct_pred += 1
        elif win_prob >= 0.6 and (home_s < away_s or home_s == away_s):
            self.wrong_pred += 1
        if win_prob <= 0.3 and home_s < away_s:
            self.correct_pred += 1
        elif win_prob <= 0.3 and (home_s > away_s or home_s == away_s):
            self.wrong_pred += 1

    def see_win_perc(self):
        print(
            f"Correct predictions: {self.correct_pred}, "
            f"Wrong predictions: {self.wrong_pred}. "
            f"Accurate predictions: {round((self.correct_pred / (self.correct_pred + self.wrong_pred)) * 100)}%"
        )

    def export_results(self):
        df = pd.DataFrame(
            {
                "date": self.matches.keys(),
                "home_team": [v["home_team"] for v in self.matches.values()],
                "away_team": [v["away_team"] for v in self.matches.values()],
                "home_score": [v["home_score"] for v in self.matches.values()],
                "away_score": [v["away_score"] for v in self.matches.values()],
                "prediction": [v["prediction"] for v in self.matches.values()],
                "elo_home_bef": [v["elo_home_bef"] for v in self.matches.values()],
                "elo_home_aft": [v["elo_home_aft"] for v in self.matches.values()],
                "elo_away_bef": [v["elo_away_bef"] for v in self.matches.values()],
                "elo_away_aft": [v["elo_away_aft"] for v in self.matches.values()],
            }
        )

        df.to_csv(
            "/Users/{user}/Desktop/Stuff/Football Spark/output.csv",
            encoding="utf-8-sig",
        )
