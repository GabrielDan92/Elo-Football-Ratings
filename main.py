from utils import ExtractMatches, EloRatings


if __name__ == "__main__":
    matches = ExtractMatches(start_year=2019)
    played_matches = matches.get_played_matches()
    scheduled_matches = matches.get_scheduled_matches()

    e = EloRatings(played_matches)

    for k, v in scheduled_matches.items():
        e.query_interface(home_team=k, away_team=v)

    e.export_results()
    e.see_win_perc()
