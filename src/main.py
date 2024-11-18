from elo_ratings import EloRatings
from extract_matches import ExtractMatches
from src.config import DEFAULT_START_YEAR, DEFAULT_CONFIDENCE, leagues
from src.db.postgres import PostgreSQL
from src.db.rich_table import RichTable
from src.simulation_runner import LeagueSimulation


def process_league(league, misc_league=False):
    # get the year/confidence combination that yields the highest number of correct predictions
    simulation = LeagueSimulation(league["comp"], range(2018, 2024), misc_league=misc_league)
    try:
        start_year, confidence = simulation.run_simulations(see_complete_logs=False)
    except:
        start_year = DEFAULT_START_YEAR
        confidence = DEFAULT_CONFIDENCE

    # Extract played and future matches
    extractor = ExtractMatches(
        comp=league["comp"],
        start_year=start_year,
        use_db=league.get("use_db", True),
        get_future_matches=True,
    )

    # Calculate Elo ratings for played matches
    elo = EloRatings(
        matches=extractor.get_played_matches(),
        confidence=confidence,
        misc_league=league.get("misc_league", ""),
    )

    # Process future matches and save results
    for home_team, away_team in extractor.get_future_matches().items():
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
        process_league(league, league.get('misc_league', None))

    RichTable().see_predictions()

    # Commit and close database connection
    db = PostgreSQL()
    db.close_conn()


if __name__ == "__main__":
    main()
