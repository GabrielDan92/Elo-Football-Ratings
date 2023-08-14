from rich.table import Table
from rich import print


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class PrettyResults(metaclass=Singleton):
    def __init__(self):
        self.matches = {}
        self.table = Table(show_header=True, header_style="bold magenta", show_lines=True, title_justify="center")
        self.table.add_column("Match time", no_wrap=True, style="cyan")
        self.table.add_column("Teams", no_wrap=True, style="cyan")
        self.table.add_column("Prediction", no_wrap=True, justify="center")
        self.table.add_column("<30 played matches", no_wrap=True, style="cyan")
        self.table.add_column("Competition", no_wrap=True, style="cyan")
        self.table.add_column("% of correct predictions", no_wrap=True, style="cyan")

    def save_matches(self, **kwargs):
        time = f"{kwargs['date']}, {kwargs['hour']}"
        teams = f"{kwargs['home_team']} - {kwargs['away_team']}"
        prediction = kwargs['win_prob']
        played_matches = kwargs['matches_count']
        competition = f"{kwargs['comp']} (Conf: {kwargs['confidence']})"
        prediction_percent = f"[bold][green]{str(round(prediction, 2))}%[/green][/bold]"

        try:
            corr_predictions = \
                f"{round((kwargs['correct_pred'] / (kwargs['correct_pred'] + kwargs['wrong_pred'])) * 100)}%"
            corr_predictions += f" (correct: {kwargs['correct_pred']}, wrong: {kwargs['wrong_pred']})"
        except:
            corr_predictions = f" (correct: {kwargs['correct_pred']}, wrong: {kwargs['wrong_pred']})"

        # populate the matches dict
        key = f"{time} {teams}"
        self.matches[key] = {
            "time": time,
            "teams": teams,
            "prediction": prediction_percent,
            "played_matches": played_matches,
            "competition": competition,
            "corr_predictions": corr_predictions
        }

    def order_matches(self):
        # order the matches in ascending order
        sorted_matches = dict(sorted(self.matches.items()))
        self.add_table_rows(matches=sorted_matches)

    def add_table_rows(self, matches):
        for match in matches.values():
            self.table.add_row(
                match["time"],
                match["teams"],
                match["prediction"],
                match["played_matches"],
                match["competition"],
                match["corr_predictions"]
            )

    def see_predictions(self):
        self.order_matches()
        print(self.table)
