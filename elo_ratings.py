import pandas as pd


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
                win_prob = self.winning_prob(
                    elo["ratings"][home_t], elo["ratings"][away_t]
                )
                self.measure_win_perc(win_prob=win_prob, home_s=home_s, away_s=away_s)
                self.measure_win_perc_with_draw(
                    win_prob=win_prob, home_s=home_s, away_s=away_s
                )

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

                elo["ratings"][home_t] = round(
                    elo["ratings"][home_t] + k_home * (home_weight - win_prob)
                )
                elo["ratings"][away_t] = round(
                    elo["ratings"][away_t] + k_away * (away_weight - (1 - win_prob))
                )

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
        win_prob = self.winning_prob(
            self.elo["ratings"][home_team], self.elo["ratings"][away_team]
        )
        s = ""

        if win_prob <= 0.3 or win_prob >= self.confidence:
            if self.elo["teams"][home_team] < 30:
                s += f" Keep in mind that {home_team} has only {self.elo['teams'][home_team]} matches played."
            if self.elo["teams"][away_team] < 30:
                s += f" Keep in mind that {away_team} has only {self.elo['teams'][away_team]} matches played."

            print(f"{date} {hour} - {home_team} [Elo {self.elo['ratings'][home_team]}] has a {round(win_prob * 100)}% "
                  f"chance to win against {away_team} [Elo {self.elo['ratings'][away_team]}].{s}")

    def pretty_query_interface(self, pretty, home_team_details, away_team, comp, correct_pred, wrong_pred, confidence):
        date, hour, home_team = home_team_details
        win_prob = self.winning_prob(self.elo["ratings"][home_team], self.elo["ratings"][away_team])
        msg = ""

        if self.elo["teams"][home_team] < 30:
            msg += f'{home_team} ({self.elo["teams"][home_team]})'
        if self.elo["teams"][away_team] < 30:
            msg += f'{away_team} ({self.elo["teams"][away_team]})'

        if win_prob <= 0.3 or win_prob >= self.confidence:
            pretty.save_matches(
                date=date,
                hour=hour,
                home_team=home_team,
                away_team=away_team,
                win_prob=win_prob,
                matches_count=msg,
                comp=comp,
                confidence=confidence,
                correct_pred=correct_pred,
                wrong_pred=wrong_pred
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
        msg = f"{competition_name.upper()}:\n" \
              f"Correct predictions w/out draws: {self.correct_pred}, " \
              f"Wrong predictions: {self.wrong_pred}.\n" \
              f"Correct predictions w/ draws: {self.correct_pred_draw}, " \
              f"Wrong predictions: {self.wrong_pred_draw}.\n"

        if not min(self.correct_pred, self.wrong_pred) == 0:
            msg += f"Accurate predictions w/out draws: " \
                   f"{round((self.correct_pred / (self.correct_pred + self.wrong_pred)) * 100)}%\n"
        if not min(self.correct_pred_draw, self.wrong_pred_draw) == 0:
            msg += f"Accurate predictions w/ draws: " \
                   f"{round((self.correct_pred_draw / (self.correct_pred_draw + self.wrong_pred_draw)) * 100)}%\n"

        print(msg)

    def get_win_perc(self):
        return self.correct_pred, self.wrong_pred

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
