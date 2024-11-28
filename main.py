from src.methods.elo_ratings import EloRatings
from src.config import DEFAULT_CONFIDENCE, leagues
from src.db.postgres import PostgreSQL
from src.db.rich_table import RichTable
from src.methods.simulation_runner import LeagueSimulation


def process_league(league):
    # get the year/confidence combination that yields the highest number of correct predictions
    misc_league = league.get("misc_league", None)
    simulation = LeagueSimulation(competition=league["comp"], misc_league=misc_league)

    try:
        start_year, confidence = simulation.run_simulations(see_complete_logs=False)
    except Exception as e:
        print(f"Error: <{str(e)}> for competition: {league['comp']}")
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

    # export the results to a CSV
    elo.export_results(competition_name=league["comp"], matches=simulation.matches)

    return True


def main():
    try:
        failed_leagues = [league["comp"] for league in leagues if not process_league(league)]
        RichTable().see_predictions()
    finally:
        PostgreSQL().close_conn()

    if failed_leagues:
        print(f"The following leagues failed to run: {failed_leagues}")


if __name__ == "__main__":
    main()
