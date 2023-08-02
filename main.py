from utils import ExtractMatches, EloRatings


if __name__ == "__main__":
    competitions = {
        "UK Premier League": ExtractMatches(start_year=2017, comp="UK-Premier-League"),
        "Spain La Liga": ExtractMatches(start_year=2017, comp="Spain-La-Liga"),
        # "Germany Bundesliga": ExtractMatches(start_year=2017, comp="DE-Bundesliga"),
        "RO Liga 1": ExtractMatches(start_year=2018, comp="RO-Liga-1"),
    }

    for name, competition in competitions.items():
        played_matches = competition.get_played_matches()
        scheduled_matches = competition.get_scheduled_matches()

        e = EloRatings(matches=played_matches, confidence=0.6)

        for k, v in scheduled_matches.items():
            try:
                e.query_interface(home_team=k, away_team=v)
            except:
                continue

        # e.export_results(competition_name=name)
        e.see_win_perc(competition_name=name)
