from collections import defaultdict

from src.config import MIN_CORRECT_GAMES
from src.elo_ratings import EloRatings
from src.extract_matches import ExtractMatches


class LeagueSimulation:
    def __init__(self, comp):
        self.comp = comp
        self.results = {}
        self.yearly_best_params = defaultdict(lambda: None)
        self.run_simulations(range(2016, 2022))  # Assuming the range of start years is (2016, 2022)
        self.print_results()
        self.group_results_by_year()
        self.display_yearly_summary()
        print("-" * 20, "\n")

    def run_simulation(self, start_year, confidence):
        extractor = ExtractMatches(self.comp, start_year=start_year, use_db=True)
        elo_ratings = EloRatings(matches=extractor.matches, confidence=confidence, misc_league=False)

        # Calculate correct predictions and return the result
        return elo_ratings.get_win_perc()

    def run_simulations(self, start_years):
        for start_year in start_years:
            local_confidence = 0.5
            while local_confidence <= 0.75:
                correct_predictions, wrong_predictions = self.run_simulation(start_year, local_confidence)
                try:
                    correct_percentage = (correct_predictions / (correct_predictions + wrong_predictions)) * 100
                    self.results[(start_year, local_confidence)] = {
                        "Predictions": (correct_predictions, wrong_predictions),
                        "Win Percentage": round(correct_percentage, 2),
                    }
                except:
                    self.results[(start_year, local_confidence)] = {
                        "Predictions": (0, 0),
                        "Win Percentage": 0,
                    }
                local_confidence += 0.01
                local_confidence = round(local_confidence, 2)

    def find_best_params(self):
        best_params = max(
            (x for x in self.results if self.results[x]["Predictions"][0] >= MIN_CORRECT_GAMES),
            key=lambda x: self.results[x]["Predictions"][0] / (
                        self.results[x]["Predictions"][0] + self.results[x]["Predictions"][1]),
            default=None
        )
        if not best_params:
            best_params = (0, 0)
            correct_predictions = 0
            wrong_predictions = 0
            win_percentage = 0
        else:
            correct_predictions = self.results[best_params]['Predictions'][0]
            wrong_predictions = self.results[best_params]['Predictions'][1]
            win_percentage = self.results[best_params]['Win Percentage']

        return best_params, correct_predictions, wrong_predictions, win_percentage

    def print_results(self):
        print("-" * 20)
        # for r in self.results:
        #     print(
        #         f"{self.comp} {r[0]}: confidence: {r[1]}, correct: {self.results[r]['Predictions'][0]}, wrong: {self.results[r]['Predictions'][1]}, win percent: {self.results[r]['Win Percentage']}")

        best_params, correct_predictions, wrong_predictions, win_percentage = self.find_best_params()
        print(
            f"{self.comp} best parameters: start_year={best_params[0]}, confidence={best_params[1]} with a win percentage of {round(win_percentage)}% (W: {correct_predictions} / L: {wrong_predictions}).")

    def group_results_by_year(self):
        for key in self.results:
            year = key[0]  # Assuming `key[0]` contains the year
            confidence_yearly = key[1]  # Assuming `key[1]` contains the confidence level
            correct, wrong = self.results[key]["Predictions"]

            if correct < MIN_CORRECT_GAMES:
                continue  # Skip entries with fewer than 45 correct predictions

            win_percent = correct / (correct + wrong)

            # Check if this is the best entry for the year
            if (self.yearly_best_params[year] is None) or (win_percent > self.yearly_best_params[year]["win_percent"]):
                self.yearly_best_params[year] = {
                    "confidence": confidence_yearly,
                    "win_percent": win_percent,
                    "correct": correct,
                    "wrong": wrong
                }

    def display_yearly_summary(self):
        for year, data in self.yearly_best_params.items():
            print(
                f"{self.comp} year: {year}, Best Confidence: {data['confidence']}, Win Percent: {round(data['win_percent'] * 100)}%, Correct: {data['correct']}, Wrong: {data['wrong']}")
