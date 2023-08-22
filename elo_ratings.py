import pandas as pd


class EloRatings:
    """
    A class for managing Elo ratings and match predictions.

    This class provides methods to calculate Elo ratings, winning probabilities,
    measure prediction performance, display match probabilities, and export results.

        Attributes:
        matches (dict): Match data.
        correct_pred (int): Correct predictions (no draws).
        wrong_pred (int): Wrong predictions.
        correct_pred_draw (int): Correct predictions (with draws).
        wrong_pred_draw (int): Wrong predictions (with draws).
        confidence (float): Confidence threshold for predictions.
        misc_league (bool): Miscellaneous league.

    Methods:
        calculate_elo(): Calculate Elo ratings and probabilities.
        winning_prob(home_rating, away_rating): Calculate win probability.
        get_win_prob_write_table(table, home_team_details, away_team, comp, confidence): Send to rich table.
        measure_win_perc(win_prob, home_s, away_s): Measure prediction performance.
        see_win_perc(competition_name): Display prediction performance.
        export_results(competition_name): Export results to CSV.

    Parameters:
        matches (dict): Match data.
        confidence (float): Confidence threshold for predictions.
        misc_league (bool): Miscellaneous league.
    """
    def __init__(self, matches, confidence, misc_league):
        self.matches = matches
        self.correct_pred = 0
        self.wrong_pred = 0
        self.correct_pred_draw = 0
        self.wrong_pred_draw = 0
        self.confidence = confidence
        self.misc_league = misc_league

        # calculate the winning probability
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

            # add a default starting rating
            elo["ratings"].setdefault(home_t, 1500)
            elo["ratings"].setdefault(away_t, 1500)

            # calculate the winning probability for the home team
            if self.misc_league:
                # target all teams in international leagues (Champions League, etc.)
                first_match = 0
            else:
                # only target teams w/ >30 played matches in domestic leagues
                first_match = 30

            if elo["teams"][home_t] >= first_match and elo["teams"][away_t] >= first_match:
                win_prob = self.winning_prob(elo["ratings"][home_t], elo["ratings"][away_t])

                self.measure_win_perc(win_prob=win_prob, home_s=home_s, away_s=away_s)

                self.matches[k]["prediction"] = round(win_prob, 2)
                self.matches[k]["elo_home_bef"] = elo["ratings"][home_t]
                self.matches[k]["elo_away_bef"] = elo["ratings"][away_t]

                # prevent rating inflation
                k_home = self.get_k_value(elo["ratings"][home_t])
                k_away = self.get_k_value(elo["ratings"][away_t])

                # recalculate the ratings based on the match result
                outcome_weights = {
                    "win": {"home": 1, "away": 0},
                    "loss": {"home": 0, "away": 1},
                    "tie": {"home": 0.5, "away": 0.5}
                }
                if home_s > away_s:
                    outcome = "win"
                elif home_s < away_s:
                    outcome = "loss"
                else:
                    outcome = "tie"

                home_weight = outcome_weights[outcome]["home"]
                away_weight = outcome_weights[outcome]["away"]
                # home advantage?
                # home_weight = outcome_weights[outcome]["home"] * 0.92
                # away_weight = outcome_weights[outcome]["away"] * 1.08

                # TODO: rewrite to use one if 
                
                # award +50% if home team won with <= 30% predicted chance of winning
                # penalize +50% if home team lost with >= 70% predicted chance of winning
                k_home *= 1.5 if (outcome == "win" and win_prob <= 0.3) or (outcome == "loss" and win_prob >= 0.7) else 1
                
                # award +50% if away team won with <= 30% predicted chance of winning
                # penalize +50% if away team lost with >= 70% predicted chance of winning
                k_away *= 1.5 if (outcome == "loss" and win_prob >= 0.7) or (outcome == "win" and win_prob <= 0.3) else 1

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

                # add 10 points for each win between matches 15-29 for domestic leagues (no Champions League, etc.)
                # TODO: penalize teams for lost games
                if not self.misc_league:
                    home_played_games = elo["teams"][home_t]
                    away_played_games = elo["teams"][away_t]

                    if 15 <= home_played_games < 30 and home_s > away_s:
                        elo["ratings"][home_t] += 10
                        self.matches[k]["elo_home_aft"] = elo["ratings"][home_t]

                    if 15 <= away_played_games < 30 and home_s < away_s:
                        elo["ratings"][away_t] += 10
                        self.matches[k]["elo_away_aft"] = elo["ratings"][away_t]

        return elo

    def get_k_value(self, rating: int) -> int:
        """
        Prevent rating inflation: calculate the K-value for Elo rating adjustments based on the given rating.
        The K-value determines the magnitude of rating adjustments based on the current rating.
        Higher K-values lead to larger adjustments and vice versa.

        Parameters:
            rating (int): The Elo rating for which to determine the K-value.

        Returns:
            int: The calculated K-value based on the rating.

        """
        if rating < 1300:
            return 40
        elif rating <= 1550:
            return 20
        else:
            return 10

    def winning_prob(self, home_rating, away_rating):
        # probability of winning
        divisor = 600 if not self.misc_league else 400
        
        return 1 / (1 + pow(10, (away_rating - home_rating) / divisor))

    def get_win_prob_write_table(self, table, home_team_details, away_team, comp, confidence):
        date, hour, home_team = home_team_details
        win_prob = self.winning_prob(self.elo["ratings"][home_team], self.elo["ratings"][away_team])
        msg = ""

        # identify teams with <30 played games
        if self.elo["teams"][home_team] < 30:
            msg += f'{home_team} ({self.elo["teams"][home_team]})'
            if self.elo["teams"][away_team] < 30:
                msg += ", "
        if self.elo["teams"][away_team] < 30:
            msg += f'{away_team} ({self.elo["teams"][away_team]})'

        kwargs_dict = {
            "date": date,
            "hour": hour,
            "home_team": home_team,
            "away_team": away_team,
            "win_prob": win_prob,
            "matches_count": msg,
            "comp": comp,
            "confidence": confidence,
            "correct_pred": self.correct_pred,
            "wrong_pred": self.wrong_pred,
            "correct_pred_draw": self.correct_pred_draw,
            "wrong_pred_draw": self.wrong_pred_draw
        }

        if self.misc_league or (win_prob <= 0.3 or win_prob >= self.confidence):
            # save all Champions League, Europa League etc. matches in the table
            # save only domestic leagues matches with a specific win_prob
            table.save_matches(**kwargs_dict)

    def measure_win_perc(self, win_prob, home_s, away_s):
        if win_prob >= self.confidence:
            if home_s == away_s:
                # draw
                self.correct_pred_draw += 1
                self.wrong_pred += 1

            if home_s > away_s:
                # home team won, expected based on win_probability
                self.correct_pred += 1
                self.correct_pred_draw += 1

            if home_s < away_s:
                # home team lost, unexpected based on win_probability
                self.wrong_pred += 1
                self.wrong_pred_draw += 1
        elif win_prob <= 0.3:
            if home_s == away_s:
                # draw
                self.correct_pred_draw += 1
                self.wrong_pred += 1

            if home_s < away_s:
                # home team lost, expected based on win_probability
                self.correct_pred += 1
                self.correct_pred_draw += 1

            if home_s > away_s:
                # home team won, unexpected based on win_probability
                self.wrong_pred += 1
                self.wrong_pred_draw += 1

    def get_win_perc(self):
        return self.correct_pred, self.wrong_pred

    def export_results(self, competition_name: str) -> None:
        """
        Export match results, incl. date, teams, scores, predictions, and Elo ratings to a CSV.

        Params:
            competition_name (str): Name for CSV file.

        Notes:
            CSV columns:
            - date, home_team, away_team, home_score, away_score
            - prediction, elo_home_bef, elo_home_aft, elo_away_bef, elo_away_aft

        Returns:
            None
        """
        df = pd.DataFrame(self.matches.values())
        df["date"] = self.matches.keys()
        df = df.reindex(columns=["date"] + list(df.columns[:-1]))
        df.to_csv(f"archive/{competition_name}.csv", encoding="utf-8-sig", index=False)
