import pandas as pd

from config import (
    INITIAL_ELO_RATING,
    FIRST_MATCH,
    ELO_LOWER_BRACKET,
    ELO_UPPER_BRACKET,
    WIN_PROB_DIVISOR_DOMESTIC,
    WIN_PROB_DIVISOR_INT,
)


class EloRatings:
    """
    A class for managing Elo ratings and match predictions.

    This class provides methods to calculate Elo ratings, winning probabilities,
    measure prediction performance, display match probabilities, and export results.
    """

    def __init__(self, matches, confidence, misc_league):
        self.matches = matches
        self.confidence = confidence
        self.misc_league = misc_league
        self.correct_pred = 0
        self.wrong_pred = 0
        self.correct_pred_draw = 0
        self.wrong_pred_draw = 0

        # calculate the winning probability
        self.elo = self.calculate_elo()

    def calculate_elo(self):
        elo = {"teams": {}, "ratings": {}}

        # calculate winning prob for each played game
        for match in self.matches.keys():
            home_t = self.matches[match]["home_team"]
            away_t = self.matches[match]["away_team"]

            # increment played games count
            elo["teams"][home_t] = elo["teams"].get(home_t, 0) + 1
            elo["teams"][away_t] = elo["teams"].get(away_t, 0) + 1

            # add an initial Elo rating or get the existing rating
            elo["ratings"].setdefault(home_t, INITIAL_ELO_RATING)
            elo["ratings"].setdefault(away_t, INITIAL_ELO_RATING)

            try:
                home_s = int(self.matches[match]["home_score"])
                away_s = int(self.matches[match]["away_score"])
            except:
                self.matches[match]["prediction"] = None
                self.matches[match]["elo_home_bef"] = None
                self.matches[match]["elo_home_aft"] = None
                self.matches[match]["elo_away_bef"] = None
                self.matches[match]["elo_away_aft"] = None
                continue

            # calculate win prob for all games in international leagues (Champions League, etc.)
            # calculate win prob for teams w/ >= 30 played games in domestic leagues
            first_match = 0 if self.misc_league else FIRST_MATCH

            if elo["teams"][home_t] >= first_match and elo["teams"][away_t] >= first_match:
                # calculate winning probability for home team and check if the prediction was correct
                win_prob = self.winning_prob(elo["ratings"][home_t], elo["ratings"][away_t])
                self.measure_win_perc(win_prob=win_prob, home_s=home_s, away_s=away_s)

                self.matches[match]["prediction"] = round(win_prob, 2)
                self.matches[match]["elo_home_bef"] = elo["ratings"][home_t]
                self.matches[match]["elo_away_bef"] = elo["ratings"][away_t]

                # prevent rating inflation
                k_home = self.get_k_value(elo["ratings"][home_t])
                k_away = self.get_k_value(elo["ratings"][away_t])

                # recalculate the ratings based on the match result
                outcome_weights = {
                    "win": {"home": 1, "away": 0},
                    "loss": {"home": 0, "away": 1},
                    "tie": {"home": 0.5, "away": 0.5},
                }
                outcome = "win" if home_s > away_s else "loss" if home_s < away_s else "tie"

                home_weight = outcome_weights[outcome]["home"]
                away_weight = outcome_weights[outcome]["away"]

                # award or penalize the teams +50% if the outcome was not expected
                if (outcome == "win" and win_prob <= 0.3) or (outcome == "loss" and win_prob >= 0.7):
                    k_home *= 1.5
                    k_away *= 1.5

                elo["ratings"][home_t] = round(elo["ratings"][home_t] + k_home * (home_weight - win_prob))
                elo["ratings"][away_t] = round(elo["ratings"][away_t] + k_away * (away_weight - (1 - win_prob)))

                self.matches[match]["elo_home_aft"] = elo["ratings"][home_t]
                self.matches[match]["elo_away_aft"] = elo["ratings"][away_t]
            else:
                self.matches[match]["prediction"] = None
                self.matches[match]["elo_home_aft"] = None
                self.matches[match]["elo_away_aft"] = None
                self.matches[match]["elo_home_bef"] = elo["ratings"][home_t]
                self.matches[match]["elo_away_bef"] = elo["ratings"][away_t]

                # add 10 points for each win between matches 15-29 for domestic leagues (no Champions League, etc.)
                if not self.misc_league:
                    home_played_games = elo["teams"][home_t]
                    away_played_games = elo["teams"][away_t]

                    if 15 <= home_played_games < FIRST_MATCH and home_s > away_s:
                        elo["ratings"][home_t] += 10
                        self.matches[match]["elo_home_aft"] = elo["ratings"][home_t]

                    if 15 <= away_played_games < FIRST_MATCH and home_s < away_s:
                        elo["ratings"][away_t] += 10
                        self.matches[match]["elo_away_aft"] = elo["ratings"][away_t]

        return elo

    def get_k_value(self, rating: int) -> int:
        """
        Prevent rating inflation: calculate the K-value for Elo rating adjustments based on the given rating.
        The K-value determines the magnitude of rating adjustments based on the current rating.
        Higher K-values lead to larger adjustments and vice versa.
        """
        if rating < ELO_LOWER_BRACKET:
            return 40
        elif rating <= ELO_UPPER_BRACKET:
            return 20
        else:
            return 10

    def winning_prob(self, home_rating, away_rating):
        divisor = WIN_PROB_DIVISOR_DOMESTIC if not self.misc_league else WIN_PROB_DIVISOR_INT

        return 1 / (1 + pow(10, (away_rating - home_rating) / divisor))

    def get_win_prob_write_table(self, table, home_team_details, away_team, comp):
        date, hour, home_team = home_team_details
        win_prob = self.winning_prob(self.elo["ratings"][home_team], self.elo["ratings"][away_team])

        # identify teams with <30 played games
        if self.elo["teams"][home_team] < 30:
            home_team += f' ({self.elo["teams"][home_team]})'
        if self.elo["teams"][away_team] < 30:
            away_team += f' ({self.elo["teams"][away_team]})'

        kwargs_dict = {
            "date": date,
            "hour": hour,
            "home_team": home_team,
            "away_team": away_team,
            "win_prob": win_prob,
            "comp": comp,
            "confidence": self.confidence,
            "correct_pred": self.correct_pred,
            "wrong_pred": self.wrong_pred,
            "correct_pred_draw": self.correct_pred_draw,
            "wrong_pred_draw": self.wrong_pred_draw,
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
        Export played matches results, including date, teams, scores, predictions, and Elo ratings to a CSV.
        """
        df = pd.DataFrame(self.matches.values())
        df["date"] = self.matches.keys()
        df = df.reindex(columns=["date"] + list(df.columns[:-1]))
        df.to_csv(f"archive/{competition_name}.csv", encoding="utf-8-sig", index=False)
