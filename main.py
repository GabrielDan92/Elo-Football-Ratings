import os
from rich import print
from extract_matches import ExtractMatches
from elo_ratings import EloRatings
from postgres import PostgreSQL
from rich_table import RichTable

leagues = [
    {"comp": "AUSTRALIA League", "start_year": 2017, "confidence": 0.6},
    {"comp": "GREEK Superliga", "start_year": 2018, "confidence": 0.6},  # 74%
    {"comp": "RO Liga 1", "start_year": 2019, "confidence": 0.6},  # 72%
    {"comp": "DE Bundesliga", "start_year": 2017, "confidence": 0.6},  # 69%
    {"comp": "IT Serie A", "start_year": 2018, "confidence": 0.6},  # 68%
    {"comp": "FRANCE Ligue 1", "start_year": 2018, "confidence": 0.63},  # 71%
    {"comp": "UK Premier League", "start_year": 2017, "confidence": 0.6},  # 70%
    {"comp": "SPAIN La Liga", "start_year": 2018, "confidence": 0.6},  # 67%
    {"comp": "BRAZIL Serie A", "start_year": 2019, "confidence": 0.6},  # 74%
    {"comp": "BELGIA Pro League", "start_year": 2020, "confidence": 0.59},  # 78%
    {"comp": "CROATIA League", "start_year": 2018, "confidence": 0.6},  # 70%
    {"comp": "CZECH League", "start_year": 2020, "confidence": 0.55},  # 69%
    {"comp": "NETHERL League", "start_year": 2020, "confidence": 0.57},  # 73%
    {
        "comp": "SCOTLAND Premiership",
        "start_year": 2019,
        "confidence": 0.55,
        # "use_db": False,
        "export_results": False,
    },  # 74%
    {"comp": "AUSTRIA Bundesliga", "start_year": 2018, "confidence": 0.62},  # 70%
    {"comp": "DENMRK Superliga", "start_year": 2018, "confidence": 0.65},  # 67%
    {"comp": "FINLAND Veikkausliiga", "start_year": 2018, "confidence": 0.58},  # 64%
    {"comp": "PORTUGAL Superliga", "start_year": 2019, "confidence": 0.6},  # 83%
    {"comp": "POLAND Ekstraklasa", "start_year": 2019, "confidence": 0.6},  # 74%
    {"comp": "NORWAY Eliteserien", "start_year": 2018, "confidence": 0.6},  # 70%
    {"comp": "SWEDEN Allsvenskan", "start_year": 2019, "confidence": 0.6},  # 73%
    {
        "comp": "Champions League",
        "start_year": 2017,
        "confidence": 0.58,
        "misc_league": True,
    },  # 74%
    {
        "comp": "Europa League",
        "start_year": 2017,
        "confidence": 0.58,
        "misc_league": True,
    },  # 74%
    {
        "comp": "Europa Conf League",
        "start_year": 2021,
        "confidence": 0.57,
        "misc_league": True,
    },
]

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    for league in leagues:
        # get the played and scheduled games
        cls = ExtractMatches(
            comp=league["comp"],
            start_year=league["start_year"],
            use_db=league.get("use_db", True),
        )

        # calculate the future games winning probability
        elo = EloRatings(
            matches=cls.get_played_matches(),
            confidence=league["confidence"],
            misc_league=league.get("misc_league", ""),
        )

        # save the findings in the rich table and postgresql
        for k, v in cls.get_future_matches().items():
            try:
                elo.get_win_prob_write_table(
                    RichTable(), home_team_details=k, away_team=v, comp=league["comp"]
                )
            except Exception as e:
                continue

        # export the played games results and Elo ratings to a CSV file
        if league.get("export_results", ""):
            elo.export_results(competition_name=league["comp"])

    RichTable().see_predictions()

    db = PostgreSQL()
    db.close_conn()
    print("[bold magenta]Press any key to end[/bold magenta]")
    input()
