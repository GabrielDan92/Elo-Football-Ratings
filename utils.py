import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time


class ExtractMatches:
    def __init__(self,
                 comp,
                 start_year,
                 confidence=0.6,
                 future_predictions=True,
                 see_win_perc=True,
                 export_results=False):
        self.matches = {}
        self.future_matches = {}
        self.main_link = f"https://fbref.com/en/comps/{MAP[comp]['comp_id']}"
        self.export_path = f"{start_year}-{datetime.date.today().year}-{comp}.csv"
        self.confidence = confidence

        # get played matches
        self.load_historic_data(start_year, comp)

        # extract current season played and scheduled matches
        self.extract_current_season_data(comp)

        # instantiate the EloRatings class and get the scheduled matches winning probability
        elo = EloRatings(matches=self.get_played_matches(), confidence=self.confidence)

        if future_predictions:
            scheduled_matches = self.get_scheduled_matches()
            for k, v in scheduled_matches.items():
                try:
                    elo.query_interface(home_team_details=k, away_team=v)
                except:
                    continue
        if see_win_perc:
            elo.see_win_perc(competition_name=comp)
        if export_results:
            elo.export_results(competition_name=comp)

    def extract_historic_data(self, start_year, comp):
        curr_year = datetime.date.today().year

        while start_year < curr_year:
            years = f"{start_year}-{start_year + 1}"
            url = f"{self.main_link}/{years}/schedule/{years}-{MAP[comp]['suffix']}"
            self.parse_html(url=url)
            start_year += 1
            time.sleep(1)

        self.export_historic_data()

    def extract_current_season_data(self, comp):
        url = f"{self.main_link}/schedule/{MAP[comp]['suffix']}"
        self.parse_html(url=url)

    def parse_html(self, url):
        print(f"\nAccess {url}")
        html = requests.get(url=url)
        soup = BeautifulSoup(html.text, "html.parser")
        matches = soup.find("table").find("tbody").find_all("tr")

        for match in matches:
            try:
                date = match.find("td", {"data-stat": "date"}).find("a").text
            except:
                date = None
            try:
                hour = match.find("td", {"data-stat": "start_time"}).find("span", {"class": "venuetime"})["data-venue-time"]
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
                key = f'{date} {hour}'
                self.matches[key] = {
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": score.replace("–", "-")[0],
                    "away_score": score.replace("–", "-")[2]
                }
            elif date and hour:
                self.future_matches[date, hour, home_team] = away_team

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


class EloRatings:
    def __init__(self, matches, confidence):
        self.matches = matches
        self.correct_pred = 0
        self.wrong_pred = 0
        self.correct_pred_draw = 0
        self.wrong_pred_draw = 0
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
                self.measure_win_perc_with_draw(win_prob=win_prob, home_s=home_s, away_s=away_s)

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
                elo["ratings"][away_t] = round(elo["ratings"][away_t] + k_away * (away_weight - (1 - win_prob)))

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
        return 1 / (1 + pow(10, (away_rating - home_rating) / 600))

    def query_interface(self, home_team_details, away_team):
        date, hour, home_team = home_team_details
        win_prob = self.winning_prob(self.elo["ratings"][home_team], self.elo["ratings"][away_team])
        s = ""

        if self.elo["teams"][home_team] < 30:
            s += f" Keep in mind that {home_team} has only {self.elo['teams'][home_team]} matches played."
        if self.elo["teams"][away_team] < 30:
            s += f" Keep in mind that {away_team} has only {self.elo['teams'][away_team]} matches played."

        print(
            f"{date} {hour} - {home_team} [Elo {self.elo['ratings'][home_team]}] has a {round(win_prob * 100)}% "
            f"chance to win against {away_team} [Elo {self.elo['ratings'][away_team]}].{s}"
        )

    def measure_win_perc(self, win_prob, home_s, away_s):
        if win_prob >= self.confidence and home_s > away_s:
            self.correct_pred += 1
        elif win_prob >= self.confidence and (home_s < away_s or home_s == away_s):
            self.wrong_pred += 1
        if win_prob <= 0.3 and home_s < away_s:
            self.correct_pred += 1
        elif win_prob <= 0.3 and (home_s > away_s or home_s == away_s):
            self.wrong_pred += 1

    def measure_win_perc_with_draw(self, win_prob, home_s, away_s):
        if win_prob >= self.confidence and (home_s > away_s or home_s == away_s):
            self.correct_pred_draw += 1
        elif win_prob >= self.confidence and home_s < away_s:
            self.wrong_pred_draw += 1
        if win_prob <= 0.3 and (home_s < away_s or home_s == away_s):
            self.correct_pred_draw += 1
        elif win_prob <= 0.3 and home_s > away_s:
            self.wrong_pred_draw += 1

    def see_win_perc(self, competition_name):
        print(f"{competition_name.upper()}: Correct predictions: {self.correct_pred}, "
              f"Wrong predictions: {self.wrong_pred}. ")
        if min(self.correct_pred, self.wrong_pred) == 0:
            print(f"Accurate predictions: God knows.")
        else:
            print(f"Accurate predictions: {round((self.correct_pred / (self.correct_pred + self.wrong_pred)) * 100)}%")

        print(f"{competition_name.upper()}: Correct predictions with draws: {self.correct_pred_draw}, "
              f"Wrong predictions: {self.wrong_pred_draw}. ")
        if min(self.correct_pred_draw, self.wrong_pred_draw) == 0:
            print(f"Accurate predictions: God knows.")
        else:
            print(f"Accurate predictions: {round((self.correct_pred_draw / (self.correct_pred_draw + self.wrong_pred_draw)) * 100)}%\n")

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


MAP = {
    "RO-Liga-1": {
        "suffix": "Liga-I-Scores-and-Fixtures",
        "comp_id": 47,
    },
    "UK-Premier-League": {
        "suffix": "Premier-League-Scores-and-Fixtures",
        "comp_id": 9,
    },
    "SP-La-Liga": {
        "suffix": "La-Liga-Scores-and-Fixtures",
        "comp_id": 12,
    },
    "DE-Bundesliga": {
        "suffix": "Bundesliga-Scores-and-Fixtures",
        "comp_id": 20,
    },
    "IT-Serie-A": {
        "suffix": "Serie-A-Scores-and-Fixtures",
        "comp_id": 11,
    },
    "FR-Ligue-1": {
        "suffix": "Ligue-1-Scores-and-Fixtures",
        "comp_id": 13,
    },
    "BLG-Pro-League": {
        "suffix": "Belgian-Pro-League-Scores-and-Fixtures",
        "comp_id": 37,
    },
    "BRZ-Serie-A": {
        "suffix": "Serie-A-Scores-and-Fixtures",
        "comp_id": 24,
    },
    "CROAT-League": {
        "suffix": "Hrvatska-NL-Scores-and-Fixtures",
        "comp_id": 63,
    },
    "CZECH-League": {
        "suffix": "Czech-First-League-Scores-and-Fixtures",
        "comp_id": 66,
    },
    "NETHRL-League": {
        "suffix": "Eredivisie-Scores-and-Fixtures",
        "comp_id": 23,
    },
    "SCOT-League": {
        "suffix": "Scottish-Premiership-Scores-and-Fixtures",
        "comp_id": 40,
    },
}
