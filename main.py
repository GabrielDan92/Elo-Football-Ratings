from utils import ExtractMatches, EloRatings


if __name__ == "__main__":
    matches = ExtractMatches(start_year=2019, extract_historic_data=True)
    future_matches = matches.get_future_matches()
    e = EloRatings(matches.get_matches())

    for k, v in future_matches.items():
        e.query_interface(home_team=k, away_team=v)

    e.export_results()
    e.see_win_perc()
