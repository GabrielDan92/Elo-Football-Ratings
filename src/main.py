from elo_ratings import EloRatings
from src.config import DEFAULT_START_YEAR, DEFAULT_CONFIDENCE, leagues
from src.db.postgres import PostgreSQL
from src.db.rich_table import RichTable
from src.simulation_runner import LeagueSimulation


def process_league(league):
    misc_league = league.get("misc_league", None)
    # get the year/confidence combination that yields the highest number of correct predictions
    simulation = LeagueSimulation(competition=league["comp"], misc_league=misc_league)
    try:
        start_year, confidence = simulation.run_simulations(see_complete_logs=False)
    except Exception as e:
        print(f"Error: <{str(e)}> for competition: {league["comp"]}")
        confidence = DEFAULT_CONFIDENCE
        return False

    # Calculate Elo ratings for played matches
    elo = EloRatings(
        matches=simulation.matches_from_best_year,
        confidence=confidence,
        misc_league=misc_league,
    )

    # Process future matches and save results
    for home_team, away_team in simulation.future_matches.items():
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

    return True


def main():
    failed_leagues = []

    for league in leagues:
        succesful_run = process_league(league)
        if not succesful_run:
            failed_leagues.append(league["comp"])

    RichTable().see_predictions()

    # Commit and close database connection
    db = PostgreSQL()
    db.close_conn()

    if failed_leagues:
        print(f"The following leagues failed to run: {failed_leagues}")


if __name__ == "__main__":
    main()
