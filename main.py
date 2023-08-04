from utils import ExtractMatches, EloRatings


if __name__ == "__main__":
    # Germany_Bundesliga = ExtractMatches(start_year=2017, comp="DE-Bundesliga")
    UK_Premier_League = ExtractMatches(start_year=2017, comp="UK-Premier-League")
    Spain_La_Liga = ExtractMatches(start_year=2017, comp="Spain-La-Liga")
    RO_Liga_1 = ExtractMatches(start_year=2018,
                               comp="RO-Liga-1",
                               confidence=0.6,
                               extract_historic_data=False,
                               export_results=False,
                               future_predictions=True,
                               see_win_perc=False)
