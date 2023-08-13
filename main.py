from extract_matches import ExtractMatches

if __name__ == "__main__":
    Romania = ExtractMatches(comp="RO-Liga-1", start_year=2018, confidence=0.6)
    Germany = ExtractMatches(comp="DE-Bundesliga", start_year=2017, confidence=0.6)
    Italy = ExtractMatches(comp="IT-Serie-A", start_year=2018, confidence=0.6)
    France = ExtractMatches(comp="FR-Ligue-1", start_year=2019, confidence=0.6)
    UK = ExtractMatches(comp="UK-Premier-League", start_year=2017)
    Spain = ExtractMatches(comp="SP-La-Liga", start_year=2019)
    # Brazil = ExtractMatches(comp="BRZ-Serie-A", start_year=2019)
    Belgium = ExtractMatches(comp="BLG-Pro-League", start_year=2020, confidence=0.59)
    Croatia = ExtractMatches(comp="CROAT-League", start_year=2018)
    Czech = ExtractMatches(comp="CZECH-League", start_year=2020, confidence=0.55)
    Netherlands = ExtractMatches(comp="NETHRL-League", start_year=2020, confidence=0.55)
    Scotland = ExtractMatches(comp="SCOT-League", start_year=2019, confidence=0.55)
