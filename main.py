import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime


class EloRatings:
    def __init__(self,
                 comp="RO-Liga-1",
                 start_year=2019,
                 extract_historic_data=False):
        self.date = []
        self.home_team = []
        self.away_team = []
        self.home_score = []
        self.away_score = []
        self.prediction = []
        self.elo_home_bef = []
        self.elo_home_aft = []
        self.elo_away_bef = []
        self.elo_away_aft = []
        self.correct_pred = 0
        self.wrong_pred = 0

        self.map = {
            "RO-Liga-1": {
                "suffix": "Liga-I-Scores-and-Fixtures",
                "comp_id": 47,
                "date_col": 1,
                "home_team_col": 3,
                "score_col": 4,
                "away_team_col": 5,
                "date_col_h": 2,
                "home_team_col_h": 4,
                "score_col_h": 5,
                "away_team_col_h": 6,
                "final_year": datetime.date.today().year
            },
            "UK-Premier-League": {
                "suffix": "Premier-League-Scores-and-Fixtures",
                "comp_id": 9,
                "date_col": 1,
                "home_team_col": 3,
                "score_col": 5,
                "away_team_col": 7,
                "date_col_h": 1,
                "home_team_col_h": 3,
                "score_col_h": 5,
                "away_team_col_h": 7,
                "final_year": datetime.date.today().year - 1
            }
        }

        export_path = f"/Users/{user}/Desktop/Stuff/Football Spark/{start_year}-{self.map[comp]['final_year']}-{comp}.csv"
        main_link = "https://fbref.com/en/comps/"

        if extract_historic_data:
            self.extract_historic_data(export_path=export_path,
                                       start_year=start_year,
                                       final_year=self.map[comp]["final_year"],
                                       competition_id=self.map[comp]["comp_id"],
                                       suffix=self.map[comp]["suffix"],
                                       main_link=main_link,
                                       comp=comp)
        else:
            self.load_historic_data(export_path=export_path)

        self.extract_current_season_data(main_link=main_link,
                                         competition_id=self.map[comp]["comp_id"],
                                         suffix=self.map[comp]["suffix"],
                                         comp=comp)

        self.elo = self.calculate_elo()


    def extract_historic_data(self,
                              export_path,
                              start_year,
                              final_year,
                              main_link,
                              competition_id,
                              suffix,
                              comp):

        while start_year < final_year:
            url = f"{main_link}/{competition_id}/{start_year}-{start_year+1}/schedule/{start_year}-{start_year+1}-{suffix}"
            print(f"Accessing {url}...")

            columns = [self.map[comp]["date_col_h"],
                       self.map[comp]["home_team_col_h"],
                       self.map[comp]["score_col_h"],
                       self.map[comp]["away_team_col_h"]
                       ]
            self.parse_html(requests.get(url=url), columns)
            start_year += 1

        self.export_historic_data(export_path)


    def extract_current_season_data(self,
                                    main_link,
                                    competition_id,
                                    suffix,
                                    comp):
        current_season = f"{main_link}/{competition_id}/schedule/{suffix}"
        print(f"Accessing {current_season}...")

        columns = [self.map[comp]["date_col"],
                   self.map[comp]["home_team_col"],
                   self.map[comp]["score_col"],
                   self.map[comp]["away_team_col"]
                   ]
        self.parse_html(requests.get(url=current_season), columns)


    def parse_html(self, html, columns):
        soup = BeautifulSoup(html.text, "html.parser")
        matches = soup.find("table").find("tbody").find_all("tr")
        for match in matches:
            try:
                if match.find_all("td")[columns[2]].text != '':
                    self.date.append(match.find_all("td")[columns[0]].text)
                    self.home_team.append(match.find_all("td")[columns[1]].text)
                    self.home_score.append(match.find_all("td")[columns[2]].text.replace("–", "-")[0])
                    self.away_score.append(match.find_all("td")[columns[2]].text.replace("–", "-")[2])
                    self.away_team.append(match.find_all("td")[columns[3]].text)
            except Exception:
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
        elo = {"matches": {}, "ratings": {}}

        while counter <= len(self.date) - 1:
            home_t = self.home_team[counter]
            away_t = self.away_team[counter]

            # keep track of matches played
            if home_t not in elo["matches"]:
                elo["matches"][home_t] = 1
            else:
                elo["matches"][home_t] = elo["matches"][home_t] + 1

            if away_t not in elo["matches"]:
                elo["matches"][away_t] = 1
            else:
                elo["matches"][away_t] = elo["matches"][away_t] + 1

            # convert scores to integers
            try:
                home_s = int(self.home_score[counter])
                away_s = int(self.away_score[counter])
            except Exception:
                self.prediction.append(None)
                self.elo_home_bef.append(None)
                self.elo_home_aft.append(None)
                self.elo_away_bef.append(None)
                self.elo_away_aft.append(None)
                counter += 1
                continue

            # add default ratings
            if home_t not in elo["ratings"]:
                elo["ratings"][home_t] = 1500
            if away_t not in elo["ratings"]:
                elo["ratings"][away_t] = 1500

            if elo["matches"][home_t] >= 30 and elo["matches"][away_t] >= 30:
                # probability of winning
                # win_prob = 1 / (1 + pow(10, (elo["ratings"][away_t] - (elo["ratings"][home_t] * 1.12)) / 600))
                win_prob = 1 / (1 + pow(10, (elo["ratings"][away_t] - elo["ratings"][home_t]) / 600))

                self.prediction.append(win_prob)
                self.elo_home_bef.append(elo["ratings"][home_t])
                self.elo_away_bef.append(elo["ratings"][away_t])

                self.measure_win_perc(win_prob=win_prob,
                                      home_t=home_t,
                                      away_t=away_t,
                                      home_s=home_s,
                                      away_s=away_s)

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
                    elo["ratings"][home_t] = round(elo["ratings"][home_t] + k_home * (1 - win_prob))
                    elo["ratings"][away_t] = round(elo["ratings"][away_t] + k_away * (0 - win_prob))

                if home_s < away_s:
                    elo["ratings"][home_t] = round(elo["ratings"][home_t] + k_home * (0 - win_prob))
                    # elo_ratings[away_t] = round(elo["ratings"][away_t] + (k_away * 1.3) * (1 - win_prob))
                    elo["ratings"][away_t] = round(elo["ratings"][away_t] + k_away * (1 - win_prob))

                if home_s == away_s:
                    elo["ratings"][home_t] = round(elo["ratings"][home_t] + k_home * (0.5 - win_prob))
                    elo["ratings"][away_t] = round(elo["ratings"][away_t] + k_away * (0.5 - win_prob))
            else:
                self.prediction.append(None)
                self.elo_home_bef.append(None)
                self.elo_away_bef.append(None)

            self.elo_home_aft.append(elo["ratings"][home_t])
            self.elo_away_aft.append(elo["ratings"][away_t])
            counter += 1

        return elo


    def query_interface(self, home_team, away_team):
        win_prob = 1 / (1 + pow(10, (self.elo["ratings"][away_team] - self.elo["ratings"][home_team]) / 600))
        s = ""

        # print(self.elo_ratings)

        if self.elo["matches"][home_team] < 30:
            s += f"Keep in mind that {home_team} has only {self.elo['matches'][home_team]} matches played. "

        if self.elo["matches"][away_team] < 30:
            s += f"Keep in mind that {away_team} has only {self.elo['matches'][away_team]} matches played."

        print(f"{home_team} [Elo: {self.elo['ratings'][home_team]}] has a {round(win_prob * 100)}% chance to win against "
              f"{away_team} [Elo: {self.elo['ratings'][away_team]}]. {s}")


    def measure_win_perc(self, win_prob, home_t, away_t, home_s, away_s):
        corr_dict = {}
        wrong_dict = {}

        if win_prob >= 0.60 and home_s > away_s:
            corr_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.correct_pred += 1
        elif win_prob >= 0.60 and (home_s < away_s or home_s == away_s):
            wrong_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.wrong_pred += 1

        if win_prob <= 0.3 and home_s < away_s:
            corr_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.correct_pred += 1
        elif win_prob <= 0.3 and (home_s > away_s or home_s == away_s):
            wrong_dict[f"{home_t} vs {away_t} [win prob: {win_prob}]"] = f"{home_s}:{away_s}"
            self.wrong_pred += 1

        # if 0.45 <= win_prob <= 0.55 and home_s == away_s:
        #     self.correct_pred += 1
        # elif 0.45 <= win_prob <= 0.55 and home_s != away_s:
        #     self.wrong_pred += 1

    def see_win_perc(self):
        print(f"Correct predictions: {self.correct_pred}, "
              f"Wrong predictions: {self.wrong_pred}. "
              f"Accurate predictions: {round((self.correct_pred / (self.correct_pred + self.wrong_pred)) * 100)}%")

    def export_results(self):
        df = pd.DataFrame(
            {"date": self.date,
             "home_team": self.home_team,
             "away_team": self.away_team,
             "home_score": self.home_score,
             "away_score": self.away_score,
             "prediction": self.prediction,
             "elo_home_bef": self.elo_home_bef,
             "elo_home_aft": self.elo_home_aft,
             "elo_away_bef": self.elo_away_bef,
             "elo_away_aft": self.elo_away_aft,
             })
        
        df.to_csv("/Users/{user}/Desktop/Stuff/Football Spark/output.csv", encoding="utf-8-sig")


if __name__ == '__main__':
    # e = EloRatings(extract_historic_data=True, start_year=2019, comp="UK-Premier-League")
    e = EloRatings(start_year=2019)
    e.query_interface(home_team="FC U Craiova",
                      away_team="Universitatea Cluj")
    e.query_interface(home_team="Rapid București",
                      away_team="Botoșani")
    e.query_interface(home_team="Hermannstadt",
                      away_team="UTA Arad")
    e.query_interface(home_team="Oțelul Galați",
                      away_team="FCSB")
    e.query_interface(home_team="Farul Constanța",
                      away_team="Poli Iași")
    e.query_interface(home_team="CFR Cluj",
                      away_team="CS U Craiova")
    e.query_interface(home_team="Petrolul Ploiești",
                      away_team="Voluntari")
    e.query_interface(home_team="Dinamo",
                      away_team="Sepsi")

    # e.export_results()
    e.see_win_perc()


"""
TODO: home advantage
	    win	lose	games	win_perc	adv
home	525	700	    1225	43%	        12%
away	378	847	    1225	31%	        -12%


FC U Craiova [Elo: 1512] has a 50% chance to win against Universitatea Cluj [Elo: 1510]. 
Rapid București [Elo: 1557] has a 53% chance to win against Botoșani [Elo: 1530]. 
Hermannstadt [Elo: 1494] has a 56% chance to win against UTA Arad [Elo: 1432]. 
Oțelul Galați [Elo: 1500] has a 31% chance to win against FCSB [Elo: 1709]. Keep in mind that Oțelul Galați has only 2 matches played. 
Farul Constanța [Elo: 1569] has a 71% chance to win against Poli Iași [Elo: 1338]. 
CFR Cluj [Elo: 1754] has a 60% chance to win against CS U Craiova [Elo: 1648]. 
Petrolul Ploiești [Elo: 1523] has a 52% chance to win against Voluntari [Elo: 1504]. 
Dinamo [Elo: 1301] has a 29% chance to win against Sepsi [Elo: 1530].
"""
