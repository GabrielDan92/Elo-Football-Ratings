from rich import print
from rich.table import Table

from src.db.postgres import PostgreSQL
from src.db.queries import INSERT_SCHEDULED_GAMES
from src.db.singleton import Singleton


class RichTable(metaclass=Singleton):
    """
    Singleton class to manage and display match prediction data in a rich table.

    Provides functionality to save match info, calculate correct prediction percentages,
    order matches, and display predictions using `rich` library.
    """

    def __init__(self):
        self.matches = {}
        self.db = PostgreSQL()
        self.table = Table(
            show_header=True, header_style="bold magenta", show_lines=True
        )

        self.table.add_column("Match time", no_wrap=True, style="cyan")
        self.table.add_column("Teams", no_wrap=True, style="cyan")
        self.table.add_column("Prediction", no_wrap=True, justify="center")
        self.table.add_column("Competition", no_wrap=True, style="cyan")
        self.table.add_column("% of correct predictions", no_wrap=True, style="cyan")
        self.table.add_column(
            "% of correct predictions w/ draws", no_wrap=True, style="cyan"
        )

    def save_matches(self, **kwargs):
        time = f"{kwargs['date']}, {kwargs['hour']}"
        teams = f"{kwargs['home_team']} - {kwargs['away_team']}"
        competition = f"{kwargs['comp']} ({round(kwargs['confidence']*100)}% confidence)"
        prediction_percent = f"[bold][green]{str(round(kwargs['win_prob']*100))}%[/green][/bold]"
        prediction_percent_raw = f"{str(round(kwargs['win_prob']*100))}%"
        corr_predictions = self.calculate_correct_predictions(kwargs, "correct_pred", "wrong_pred")
        corr_predictions_draw = self.calculate_correct_predictions(kwargs, "correct_pred_draw", "wrong_pred_draw")

        # populate the matches dict
        key = f"{time} {teams}"
        self.matches[key] = {
            "time": time,
            "teams": teams,
            "prediction": prediction_percent,
            "prediction_raw": prediction_percent_raw,
            "competition": competition,
            "corr_predictions": corr_predictions,
            "corr_predictions_draw": corr_predictions_draw,
        }

    def calculate_correct_predictions(self, kwargs, correct_key, wrong_key):
        try:
            correct_percentage = (kwargs[correct_key] / (kwargs[correct_key] + kwargs[wrong_key])) * 100
            return f"{round(correct_percentage)}% (correct {kwargs[correct_key]}, wrong {kwargs[wrong_key]})"
        except ZeroDivisionError:
            return f" (correct {kwargs[correct_key]}, wrong {kwargs[wrong_key]})"

    def order_matches(self):
        # order the matches in ascending date order
        sorted_matches = dict(sorted(self.matches.items()))
        self.add_table_rows(matches=sorted_matches)

    def add_table_rows(self, matches):
        for match in matches.values():
            self.table.add_row(
                match["time"],
                match["teams"],
                match["prediction"],
                match["competition"],
                match["corr_predictions"],
                match["corr_predictions_draw"],
            )

        values = [
            (
                match["time"],
                match["teams"],
                match["prediction_raw"],
                match["competition"],
                match["corr_predictions"],
                match["corr_predictions_draw"],
            )
            for match in matches.values()
        ]

        self.db.batch_insert(INSERT_SCHEDULED_GAMES, values)

    def see_predictions(self):
        self.order_matches()
        print(self.table)
