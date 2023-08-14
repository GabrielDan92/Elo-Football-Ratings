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
        self.table.add_column("Played Matches", no_wrap=True, style="cyan")
        self.table.add_column("Competition", no_wrap=True, style="cyan")
        self.table.add_column("% of correct predictions", no_wrap=True, style="cyan")

    def add_row(self, **kwargs):
        date = f"{kwargs['date']}, {kwargs['hour']}"
        teams = f"{kwargs['home_team']} - {kwargs['away_team']}"
        prediction = kwargs['win_prob']
        played_matches = kwargs['matches_count']
        competition = f"{kwargs['comp']} (Conf: {kwargs['confidence']})"
        pred_percent = f"[bold][green]{str(round(prediction, 2))}%[/green][/bold]"

        try:
            perc_corr_predictions = \
                f"{round((kwargs['correct_pred'] / (kwargs['correct_pred'] + kwargs['wrong_pred'])) * 100)}%"
            perc_corr_predictions += f" (correct: {kwargs['correct_pred']}, wrong: {kwargs['wrong_pred']})"
        except:
            perc_corr_predictions = f" (correct: {kwargs['correct_pred']}, wrong: {kwargs['wrong_pred']})"

        self.table.add_row(
            date,
            teams,
            pred_percent,
            played_matches,
            competition,
            perc_corr_predictions
        )

    def see_predictions(self):
        print(self.table)
