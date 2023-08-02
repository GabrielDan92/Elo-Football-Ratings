import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


class ExtractMatches:
    def __init__(self, comp, start_year, extract_historic_data=False):
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
                "score_col": 4,
                "away_team_col": 5,
                "date_col_h": 1,
                "hour_col_h": 2,
                "home_team_col_h": 3,
                "score_col_h": 5,
                "away_team_col_h": 7
            },
            "Spain-La-Liga": {
                "suffix": "La-Liga-Scores-and-Fixtures",
                "comp_id": 12,
                "date_col": 1,
                "hour_col": 2,
                "home_team_col": 3,
                "score_col": 4,
                "away_team_col": 5,
                "date_col_h": 1,
                "hour_col_h": 2,
                "home_team_col_h": 3,
                "score_col_h": 5,
                "away_team_col_h": 7
            },
            "DE-Bundesliga": {
                "suffix": "Bundesliga-Scores-and-Fixtures",
                "comp_id": 20,
                "date_col": 1,
                "hour_col": 2,
                "home_team_col": 3,
                "score_col": 4,
                "away_team_col": 5,
                "date_col_h": 2,
                "hour_col_h": 3,
                "home_team_col_h": 4,
                "score_col_h": 6,
                "away_team_col_h": 8
            },
        }
        self.main_link = f"https://fbref.com/en/comps/{self.map[comp]['comp_id']}"
        self.export_path = f"{start_year}-{datetime.date.today().year}-{comp}.csv"

        # extract or load played matches up until previous season
        if extract_historic_data:
            self.extract_historic_data(start_year, comp)
        else:
            self.load_historic_data()

        # extract current season played and scheduled matches
        self.extract_current_season_data(comp)

    def extract_historic_data(self, start_year, comp):
        curr_year = datetime.date.today().year

        while start_year < curr_year:
            years = f"{start_year}-{start_year+1}"
            url = f"{self.main_link}/{years}/schedule/{years}-{self.map[comp]['suffix']}"
            print(f"Accessing {url}...")
            
            self.parse_html(requests.get(url=url), comp, historic=True)
            start_year += 1

        self.export_historic_data()

    def extract_current_season_data(self, comp):
        current_season = f"{self.main_link}/schedule/{self.map[comp]['suffix']}"
        print(f"Accessing {current_season}...")
        self.parse_html(requests.get(url=current_season), comp)

    def parse_html(self, html, comp, historic=False):
        d_col = self.map[comp]["date_col_h"] if historic else self.map[comp]["date_col"]
        h_team_col = self.map[comp]["home_team_col_h"] if historic else self.map[comp]["home_team_col"]
        score_col = self.map[comp]["score_col_h"] if historic else self.map[comp]["score_col"]
        a_team_col = self.map[comp]["away_team_col_h"] if historic else self.map[comp]["away_team_col"]
        hour_col = self.map[comp]["hour_col_h"] if historic else self.map[comp]["hour_col"]

        soup = BeautifulSoup(html.text, "html.parser")
        matches = soup.find("table").find("tbody").find_all("tr")

        for match in matches:
            try:
                date = match.find_all("td")[d_col].text
                hour = match.find_all("td")[hour_col].text
                score = match.find_all("td")[score_col].text
                home_team = match.find_all("td")[h_team_col].text
                away_team = match.find_all("td")[a_team_col].text

                if score:
                    key = f'{date} {hour}'
                    self.matches[key] = {
                        "home_team": home_team,
                        "away_team": away_team,
                        "home_score": score.replace("–", "-")[0],
                        "away_score": score.replace("–", "-")[2]
                    }
                elif date and hour:
                    self.future_matches[home_team] = away_team
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
            
    def get_played_matches(self):
        return self.matches
    
    def get_scheduled_matches(self):
        return self.future_matches


class EloRatings:
    def __init__(self, matches, confidence):
        self.matches = matches
        self.correct_pred = 0
        self.wrong_pred = 0
        self.confidence = confidence
        self.elo = self.calculate_elo()

    def calculate_elo(self):
        elo = {"teams": {}, "ratings": {}}

        for k in self.matches.keys():
            home_t = self.matches[k]["home_team"]
            away_t = self.matches[k]["away_team"]

            # increment played matches count
            elo["teams"][home_t] = elo["teams"].get(home_t, 0) + 1
            elo["teams"][away_t] = elo["teams"].get(away_t, 0) + 1

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

            # calculate the probability for teams w/ more than 30 played matches
            if elo["teams"][home_t] >= 30 and elo["teams"][away_t] >= 30:
                win_prob = self.winning_prob(elo["ratings"][home_t], elo["ratings"][away_t])
                self.measure_win_perc(win_prob=win_prob, home_s=home_s, away_s=away_s)

                self.matches[k]["prediction"] = round(win_prob, 2)
                self.matches[k]["elo_home_bef"] = elo["ratings"][home_t]
                self.matches[k]["elo_away_bef"] = elo["ratings"][away_t]

                # prevent rating inflation
                k_home = self.get_k_value(elo["ratings"][home_t])
                k_away = self.get_k_value(elo["ratings"][away_t])
                
                # recalculate the ratings based on the match result
                if home_s > away_s:
                    home_weight = 1
                    away_weight = 0
                    if win_prob <= 0.3:
                        k_home *= 1.5  # if the home team had <= 30% chances of winning and won, award it 50% more
                        k_away *= 1.5  # if the away team had >= 70% chances of winning and lost, penalize it 50% more

                if home_s < away_s:
                    home_weight = 0
                    away_weight = 1
                    if win_prob >= 0.7:
                        k_home *= 1.5  # if the home team had >= 70% chances of winning and lost, penalize it 50% more
                        k_away *= 1.5  # if the away team had <= 30% chances of winning and won, award it 50% more

                if home_s == away_s:
                    home_weight = 0.5
                    away_weight = 0.5

                elo["ratings"][home_t] = round(elo["ratings"][home_t] + k_home * (home_weight - win_prob))
                elo["ratings"][away_t] = round(elo["ratings"][away_t] + k_away * (away_weight - (1-win_prob)))

                self.matches[k]["elo_home_aft"] = elo["ratings"][home_t]
                self.matches[k]["elo_away_aft"] = elo["ratings"][away_t]
            else:
                self.matches[k]["prediction"] = None
                self.matches[k]["elo_home_aft"] = None
                self.matches[k]["elo_away_aft"] = None
                self.matches[k]["elo_home_bef"] = elo["ratings"][home_t]
                self.matches[k]["elo_away_bef"] = elo["ratings"][away_t]

                # add 10 points for each win between matches 15-30
                if 15 <= elo["teams"][home_t] < 30:
                    if home_s > away_s:
                        elo["ratings"][home_t] += 10
                    self.matches[k]["elo_home_aft"] = elo["ratings"][home_t]

                if 15 <= elo["teams"][away_t] < 30:
                    if home_s < away_s:
                        elo["ratings"][away_t] += 10
                    self.matches[k]["elo_away_aft"] = elo["ratings"][away_t]

        return elo

    def get_k_value(self, rating):
        # prevent rating inflation
        if rating < 1300:
            return 40
        if 1300 <= rating <= 1550:
            return 20
        if rating > 1550:
            return 10

    def winning_prob(self, home_rating, away_rating):
        # probability of winning
        return 1 / (1+pow(10, (away_rating - home_rating) / 600))

    def query_interface(self, home_team, away_team):
        win_prob = self.winning_prob(self.elo["ratings"][home_team], self.elo["ratings"][away_team])
        s = ""

        if self.elo["teams"][home_team] < 30:
            s += f" Keep in mind that {home_team} has only {self.elo['teams'][home_team]} matches played."
        if self.elo["teams"][away_team] < 30:
            s += f" Keep in mind that {away_team} has only {self.elo['teams'][away_team]} matches played."

        print(f"{home_team} [Elo: {self.elo['ratings'][home_team]}] has a {round(win_prob * 100)}% chance to win against "
              f"{away_team} [Elo: {self.elo['ratings'][away_team]}].{s}")

    def measure_win_perc(self, win_prob, home_s, away_s):
        if win_prob >= self.confidence and home_s > away_s:
            self.correct_pred += 1
        elif win_prob >= self.confidence and (home_s < away_s or home_s == away_s):
            self.wrong_pred += 1
        if win_prob <= 0.3 and home_s < away_s:
            self.correct_pred += 1
        elif win_prob <= 0.3 and (home_s > away_s or home_s == away_s):
            self.wrong_pred += 1

    def see_win_perc(self, competition_name):
        print(f"For {competition_name}:\n"
              f"Correct predictions: {self.correct_pred}, "
              f"Wrong predictions: {self.wrong_pred}. "
              f"Accurate predictions: {round((self.correct_pred / (self.correct_pred + self.wrong_pred)) * 100)}%\n")

    def export_results(self, competition_name):
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

        df.to_csv(f"{competition_name}.csv", encoding="utf-8-sig")
