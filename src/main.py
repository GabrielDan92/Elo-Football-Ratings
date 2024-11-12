from elo_ratings import EloRatings
from extract_matches import ExtractMatches
from src.db.postgres import PostgreSQL
from src.db.rich_table import RichTable
from src.simulation_runner import LeagueSimulation


leagues = [
    {"comp": "Korea League 1", "start_year": 2018, "confidence": 0.62},  # 68%
    {"comp": "Japan J1 League", "start_year": 2020, "confidence": 0.6},  # 65%
    {"comp": "Saudi Prof League", "start_year": 2021, "confidence": 0.6},  # 88%
    {"comp": "Mexic Liga MX", "start_year": 2020, "confidence": 0.65},  # 67%
    {"comp": "AUSTRALIA League", "start_year": 2017, "confidence": 0.6},
    {"comp": "GREEK Superliga", "start_year": 2018, "confidence": 0.6},  # 74%
    {"comp": "RO Liga 1", "start_year": 2021, "confidence": 0.61},  # 72%
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
    {"comp": "SCOTLAND Premiership", "start_year": 2019, "confidence": 0.55},  # 74%
    {"comp": "AUSTRIA Bundesliga", "start_year": 2018, "confidence": 0.62},  # 70%
    {"comp": "DENMRK Superliga", "start_year": 2018, "confidence": 0.65},  # 67%
    {"comp": "FINLAND Veikkausliiga", "start_year": 2018, "confidence": 0.58},  # 64%
    {"comp": "PORTUGAL Superliga", "start_year": 2019, "confidence": 0.6},  # 83%
    {"comp": "POLAND Ekstraklasa", "start_year": 2019, "confidence": 0.6},  # 74%
    {"comp": "NORWAY Eliteserien", "start_year": 2018, "confidence": 0.6},  # 70%
    {"comp": "SWEDEN Allsvenskan", "start_year": 2019, "confidence": 0.6},  # 73%
    {"comp": "Bulgaria First League", "start_year": 2020, "confidence": 0.57},  # 71%
    {"comp": "Turkey SuperLiga", "start_year": 2020, "confidence": 0.6},  # 79%
    {"comp": "Serbia SuperLiga", "start_year": 2021, "confidence": 0.6},  # 79%
    {"comp": "Hungary NB1", "start_year": 2019, "confidence": 0.6},  # 71%
    # {"comp": "Champions League", "start_year": 2017, "confidence": 0.58, "misc_league": True},  # 74%
    # {"comp": "Europa League", "start_year": 2017, "confidence": 0.58, "misc_league": True,},  # 74%
    # {"comp": "Europa Conf League", "start_year": 2021, "confidence": 0.57, "misc_league": True,},
]


def process_league(league):
    # get the year/confidence combination that yields the highest number of correct predictions
    simulation = LeagueSimulation(league["comp"])
    try:
        start_year, confidence = simulation.run_simulations()
    except:
        start_year = league["start_year"]
        confidence = league["confidence"]

    # Extract played and future matches
    match_extractor = ExtractMatches(
        comp=league["comp"],
        start_year=start_year,
        use_db=league.get("use_db", True),
        get_future_matches=True,
    )

    # Calculate Elo ratings for played matches
    elo = EloRatings(
        matches=match_extractor.get_played_matches(),
        confidence=confidence,
        misc_league=league.get("misc_league", ""),
    )

    # Process future matches and save results
    for home_team, away_team in match_extractor.get_future_matches().items():
        try:
            elo.get_win_prob_write_table(
                RichTable(),
                home_team_details=home_team,
                away_team=away_team,
                comp=league["comp"],
            )
        except Exception as e:
            print(str(e))
            continue

    # Optionally export the results to a CSV
    if league.get("export_results", ""):
        elo.export_results(competition_name=league["comp"])


def main():
    for league in leagues:
        process_league(league)

    RichTable().see_predictions()

    # Commit and close database connection
    db = PostgreSQL()
    db.close_conn()


if __name__ == "__main__":
    main()
