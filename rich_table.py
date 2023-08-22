from rich.table import Table
from rich import print


class Singleton(type):
    """
    Implements the Singleton design pattern for the ExtractMatches class.

    This metaclass ensures that each competition has its own instance of the ExtractMatches class, and it manages
    sending scheduled matches to a shared rich table. By using the Singleton approach, all matches are consolidated
    into a single table, which is only printed at the end. This approach eliminates the need for multiple tables for
    each competition.

    Attributes:
        _instances (dict): A dictionary to store instances of classes using this metaclass.

    Methods:
        __call__(*args, **kwargs): Creates and returns a new instance if it doesn't exist, otherwise returns the
        existing instance.

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RichTable(metaclass=Singleton):
    """
    Singleton class to manage and display match prediction data in a rich table.

    Provides functionality to save match info, calculate correct prediction percentages,
    order matches, and display predictions using `rich` library.

    Attributes:
        matches (dict): Store match predictions.
        table (Table): Rich Table object for display.

    Methods:
        save_matches(**kwargs): Save match info in matches dict.
        calculate_correct_predictions(kwargs, correct_key, wrong_key): Calculate and format correct prediction %.
        order_matches(): Order matches based on time.
        add_table_rows(matches): Add rows to rich Table.
        see_predictions(): Display predictions in formatted table.
    """

    def __init__(self):
        self.matches = {}
        self.table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        self.table.add_column("Match time", no_wrap=True, style="cyan")
        self.table.add_column("Teams", no_wrap=True, style="cyan")
        self.table.add_column("Prediction", no_wrap=True, justify="center")
        self.table.add_column("<30 played matches", no_wrap=True, style="cyan")
        self.table.add_column("Competition", no_wrap=True, style="cyan")
        self.table.add_column("% of correct predictions", no_wrap=True, style="cyan")
        self.table.add_column("% of correct predictions w/ draws", no_wrap=True, style="cyan")

    def save_matches(self, **kwargs):
        time = f"{kwargs['date']}, {kwargs['hour']}"
        teams = f"{kwargs['home_team']} - {kwargs['away_team']}"
        played_matches = kwargs['matches_count']
        competition = f"{kwargs['comp']} (conf: {kwargs['confidence']})"
        prediction_percent = f"[bold][green]{str(round(kwargs['win_prob'], 2))}%[/green][/bold]"
        corr_predictions = self.calculate_correct_predictions(kwargs, 'correct_pred', 'wrong_pred')
        corr_predictions_draw = self.calculate_correct_predictions(kwargs, 'correct_pred_draw', 'wrong_pred_draw')

        # populate the matches dict
        key = f"{time} {teams}"
        self.matches[key] = {
            "time": time,
            "teams": teams,
            "prediction": prediction_percent,
            "played_matches": played_matches,
            "competition": competition,
            "corr_predictions": corr_predictions,
            "corr_predictions_draw": corr_predictions_draw
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
                match["played_matches"],
                match["competition"],
                match["corr_predictions"],
                match["corr_predictions_draw"]
            )

    def see_predictions(self):
        self.order_matches()
        print(self.table)
