from collections import defaultdict
from typing import Dict, Tuple, Optional, Any
from dataclasses import dataclass

from src.config import MIN_CORRECT_GAMES, SIMULATION_START_YR, SIMULATION_END_YR
from src.elo_ratings import EloRatings
from src.extract_matches import ExtractMatches


@dataclass
class SimulationResult:
    start_year: int
    confidence: float
    correct_predictions: int
    wrong_predictions: int
    win_percentage: float


class LeagueSimulation:
    """
    Simulates a league competition over multiple years with varying confidence levels to find
    the optimal parameters for predicting match outcomes based on Elo ratings.
    """

    def __init__(self, comp: str, years_range: range = range(SIMULATION_START_YR, SIMULATION_END_YR), misc_league=False):
        """
        Initializes the LeagueSimulation instance with competition and start years.

        Args:
            comp (str): The competition name.
            years_range (range): A range of start years for the simulation.
        """
        self.years_range = years_range
        self.comp = comp
        self.misc_league = misc_league
        self.results: Dict[Tuple[int, float], SimulationResult] = {}
        self.yearly_best_params: Dict[int, Optional[SimulationResult]] = defaultdict(lambda: None)
        self.extractor = None
        self.matches = None
        self.future_matches = None
        self.matches_from_best_year = None

        # Extract played and future matches
        self._get_all_matches()

    def _get_all_matches(self):
        self.extractor = ExtractMatches(self.comp, start_year=self.years_range[0], use_db=True)
        self.matches = self.extractor.matches
        self.future_matches = self.extractor.future_matches

    def _filter_matches_by_period(self, start_year: int) -> Dict[str, Any]:
        end_year = self.years_range[-1]
        return {
            k: v for k, v in self.matches.items()
            if start_year <= int(k.split(',')[0].split('-')[0]) <= end_year
        }

    def run_simulation(self, start_year: int, confidence: float) -> Tuple[int, int]:
        """
        Runs a single simulation for a specific year and confidence level.

        Args:
            start_year (int): The start year for the simulation.
            confidence (float): The confidence level for the Elo rating predictions.

        Returns:
            Tuple[int, int]: A tuple containing the counts of correct and wrong predictions.
        """

        # get ratings only for matches in the given period
        matches_in_period = self._filter_matches_by_period(start_year)

        elo_ratings = EloRatings(matches=matches_in_period, confidence=confidence, misc_league=self.misc_league)
        return elo_ratings.get_win_perc()

    def run_simulations(self, see_complete_logs=False) -> tuple[int, float]:
        """
        Runs simulations across specified years and a range of confidence levels,
        recording results and returning the best overall and yearly best results.

        Returns:
            Tuple[int, float]: The best start year and confidence level.
        """
        for start_year in self.years_range:
            for local_confidence in [round(0.5 + i * 0.01, 2) for i in range(26)]:
                self._record_simulation_result(start_year, local_confidence)

        best_result = self._get_best_result()

        if see_complete_logs:
            self._group_yearly_best_results()
            self._display_yearly_summary()
            self.final_results()

        if best_result:
            # keep only matches from the best year going forward
            self.matches_from_best_year = self._filter_matches_by_period(best_result.start_year)
            return best_result.start_year, best_result.confidence

    def _record_simulation_result(self, start_year: int, confidence: float) -> None:
        """
        Records the results of a single simulation, including correct and wrong prediction counts.

        Args:
            start_year (int): The start year of the simulation.
            confidence (float): The confidence level used in the simulation.
        """
        try:
            correct, wrong = self.run_simulation(start_year, confidence)
            win_percentage = (correct / (correct + wrong)) * 100 if correct + wrong > 0 else 0
            self.results[(start_year, confidence)] = SimulationResult(
                start_year=start_year,
                confidence=confidence,
                correct_predictions=correct,
                wrong_predictions=wrong,
                win_percentage=round(win_percentage, 2),
            )
        except Exception as e:
            print(str(e))
            # Logs zero predictions if an error occurs
            self.results[(start_year, confidence)] = SimulationResult(
                start_year=start_year,
                confidence=confidence,
                correct_predictions=0,
                wrong_predictions=0,
                win_percentage=0.0,
            )

    def _find_best_params(self) -> Optional[SimulationResult]:
        """
        Finds the best parameters based on the highest win percentage for valid results.

        Returns:
            Optional[SimulationResult]: The best simulation result based on the highest win percentage.
        """
        valid_results = {k: v for k, v in self.results.items() if v.correct_predictions >= MIN_CORRECT_GAMES}

        if not valid_results:
            return None

        return max(valid_results.values(), key=lambda result: result.win_percentage)


    def _get_best_result(self) -> Optional[SimulationResult]:
        """
        Displays the best parameters across all simulations.

        Returns:
            Optional[SimulationResult]: The best simulation result with year, confidence, correct/wrong predictions,
                                        and win percentage.
        """
        best_result = self._find_best_params()

        if best_result:
            print("\n", "-" * 80)
            print(
                f"{self.comp} Best Parameters: start_year={best_result.start_year}, "
                f"confidence={best_result.confidence}, Win Percentage: {best_result.win_percentage}% "
                f"(W: {best_result.correct_predictions} / L: {best_result.wrong_predictions})"
            )
        else:
            print(f"{self.comp} - No valid simulation results found.")

        return best_result

    def _group_yearly_best_results(self) -> None:
        """
        Groups results by year and identifies the best simulation for each year.
        """
        for (year, confidence), result in self.results.items():
            if result.correct_predictions < MIN_CORRECT_GAMES:
                continue

            current_best = self.yearly_best_params[year]
            if not current_best or result.win_percentage > current_best.win_percentage:
                self.yearly_best_params[year] = result

    def _display_yearly_summary(self) -> None:
        """
        Displays a summary of the best simulation parameters and win percentage for each year.
        """
        for year, data in self.yearly_best_params.items():
            print(
                f"{self.comp} Year: {year}, Best Confidence: {data.confidence}, "
                f"Win Percent: {round(data.win_percentage)}%, "
                f"Correct: {data.correct_predictions}, Wrong: {data.wrong_predictions}"
            )

    def final_results(self) -> None:
        """
        Displays a summary of all simulation results, including start year, confidence level,
        correct and wrong predictions, and win percentage for each simulation run.
        """
        for (year, confidence), result in self.results.items():
            # Accessing attributes directly from the SimulationResult instance
            correct = result.correct_predictions
            wrong = result.wrong_predictions
            win_percent = result.win_percentage
            print(
                f"{self.comp} {year}: Confidence={confidence}, Correct={correct}, "
                f"Wrong={wrong}, Win Percent={win_percent}%"
            )
        print("-" * 80, "\n")
