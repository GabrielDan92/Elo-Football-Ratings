import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


class EloRatings:
    def __init__(self,
                 start_year=2019,
                 extract_historic_data=False):
        self.date = []
        self.home_team = []
        self.away_team = []
        self.home_score = []
        self.away_score = []
        self.correct_pred = 0
        self.wrong_pred = 0

        final_year = datetime.date.today().year
        export_path = f"/Users/{user}/Desktop/Stuff/Football Spark/{start_year}-{final_year}-Romania.csv"
        main_link = "https://fbref.com/en/comps/"

        if extract_historic_data:
            self.extract_historic_data(export_path=export_path,
                                       start_year=start_year,
                                       final_year=final_year,
                                       main_link=main_link)
        else:
            self.load_historic_data(export_path=export_path)

        self.extract_current_season_data(main_link=main_link)

        self.elo_ratings = self.calculate_elo()

    def extract_historic_data(self,
                              export_path,
                              start_year,
                              final_year,
                              main_link,
                              competition_id=47,
                              suffix="Liga-I-Scores-and-Fixtures"):

        while start_year < final_year:
            url = f"{main_link}/{competition_id}/{start_year}-{start_year+1}/schedule/{start_year}-{start_year+1}-{suffix}"
            html = requests.get(url=url)
            print(f"Accessing {url}...")
            self.parse_html(html, 2)
            start_year += 1

        self.export_historic_data(export_path)

    def extract_current_season_data(self,
                                    main_link,
                                    competition_id=47,
                                    suffix="Liga-I-Scores-and-Fixtures"):
        current_season = f"{main_link}/{competition_id}/schedule/{suffix}"
        html = requests.get(url=current_season)
        print(f"Accessing {current_season}...")
        self.parse_html(html, 1)

    def parse_html(self, html, col):
        soup = BeautifulSoup(html.text, "html.parser")
        matches = soup.find("table").find("tbody").find_all("tr")
        for match in matches:
            try:
                if match.find_all("td")[col+3].text != '':
                    self.date.append(match.find_all("td")[col].text)
                    self.home_team.append(match.find_all("td")[col+2].text)
                    self.home_score.append(match.find_all("td")[col+3].text.replace("–", "-")[0])
                    self.away_score.append(match.find_all("td")[col+3].text.replace("–", "-")[2])
                    self.away_team.append(match.find_all("td")[col+4].text)
            except Exception as e:
                # print(str(e))
                continue

    def export_historic_data(self, export_path):
        df = pd.DataFrame(
            {"date": self.date,
             "home_team": self.home_team,
             "away_team": self.away_team,
             "home_score": self.home_score,
             "away_score": self.away_score})

        df.to_csv(export_path, encoding="utf-8-sig")

    def load_historic_data(self, export_path):
        data = pd.read_csv(export_path)

        self.date = data["date"].tolist()
        self.home_team = data["home_team"].tolist()
        self.away_team = data["away_team"].tolist()
        self.home_score = data["home_score"].tolist()
        self.away_score = data["away_score"].tolist()

    def calculate_elo(self):
        counter = 0
        matches_played = {}
        elo_ratings = {}

        while counter <= len(self.date) - 1:
            home_t = self.home_team[counter]
            away_t = self.away_team[counter]

            # keep track of matches played
            if home_t not in matches_played:
                matches_played[home_t] = 1
            else:
                matches_played[home_t] = matches_played[home_t] + 1

            if away_t not in matches_played:
                matches_played[away_t] = 1
            else:
                matches_played[away_t] = matches_played[away_t] + 1

            # convert scores to integers
            try:
                home_s = int(self.home_score[counter])
                away_s = int(self.away_score[counter])
            except Exception as e:
                # print(str(e))
                counter += 1
                continue

            # add default ratings
            if home_t not in elo_ratings:
                elo_ratings[home_t] = 1500
            if away_t not in elo_ratings:
                elo_ratings[away_t] = 1500

            if matches_played[home_t] >= 30 and matches_played[away_t] >= 30:
                # probability of winning
                win_prob = 1 / (1 + pow(10, (elo_ratings[away_t] - elo_ratings[home_t]) / 600))
                self.measure_win_perc(win_prob=win_prob,
                                      home_t=home_t,
                                      away_t=away_t,
                                      home_s=home_s,
                                      away_s=away_s)

                # prevent rating inflation
                if elo_ratings[home_t] < 1000:
                    k_home = 40
                if 1000 <= elo_ratings[home_t] <= 1500:
                    k_home = 20
                if elo_ratings[home_t] > 1500:
                    k_home = 10

                if elo_ratings[away_t] < 1000:
                    k_away = 40
                if 1000 <= elo_ratings[away_t] <= 1500:
                    k_away = 20
                if elo_ratings[away_t] > 1500:
                    k_away = 10

                if home_s > away_s:
                    elo_ratings[home_t] = round(elo_ratings[home_t] + k_home * (1 - win_prob))
                    elo_ratings[away_t] = round(elo_ratings[away_t] + k_away * (0 - win_prob))

                if home_s < away_s:
                    elo_ratings[home_t] = round(elo_ratings[home_t] + k_home * (0 - win_prob))
                    elo_ratings[away_t] = round(elo_ratings[away_t] + (k_away * 1.3) * (1 - win_prob))

                if home_s == away_s:
                    elo_ratings[home_t] = round(elo_ratings[home_t] + k_home * (0.5 - win_prob))
                    elo_ratings[away_t] = round(elo_ratings[away_t] + k_away * (0.5 - win_prob))

            counter += 1

        return elo_ratings

    def query_interface(self, home_team, away_team):
        win_prob = 1 / (1 + pow(10, (self.elo_ratings[away_team] - self.elo_ratings[home_team]) / 600))
        # print(self.elo_ratings)
        print(f"{home_team} [Elo: {self.elo_ratings[home_team]}] has a {round(win_prob * 100)}% chance to win against "
              f"{away_team} [Elo: {self.elo_ratings[away_team]}]")

    def measure_win_perc(self, win_prob, home_t, away_t, home_s, away_s):
        corr_dict = {}
        wrong_dict = {}

        if win_prob >= 0.7 and home_s > away_s:
            corr_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.correct_pred += 1
        elif win_prob >= 0.7 and (home_s < away_s or home_s == away_s):
            wrong_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.wrong_pred += 1

        if win_prob <= 0.3 and home_s < away_s:
            corr_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.correct_pred += 1
        elif win_prob <= 0.3 and (home_s > away_s or home_s == away_s):
            wrong_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.wrong_pred += 1

    def see_win_perc(self):
        print(f"Correct predictions: {self.correct_pred}, "
              f"Wrong predictions: {self.wrong_pred}. "
              f"Accurate predictions: {round((self.correct_pred / (self.correct_pred + self.wrong_pred)) * 100)}%")


if __name__ == '__main__':
    # e = EloRatings(extract_historic_data=True, start_year=2017)
    e = EloRatings(start_year=2019)
    e.query_interface(home_team="CFR Cluj",
                      away_team="FCSB")
    e.query_interface(home_team="FCSB",
                      away_team="CFR Cluj")
    e.query_interface(home_team="FCSB",
                      away_team="Dinamo")
    e.query_interface(home_team="Farul Constanța",
                      away_team="Voluntari")

    e.see_win_perc()
