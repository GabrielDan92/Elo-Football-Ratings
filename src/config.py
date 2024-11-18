INITIAL_ELO_RATING = 1500
ELO_LOWER_BRACKET = 1300
ELO_UPPER_BRACKET = 1550
WIN_PROB_DIVISOR_DOMESTIC = 600  # weights
WIN_PROB_DIVISOR_INT = 400  # weights
FIRST_MATCH = 30
MIN_CORRECT_GAMES = 45
SIMULATION_START_YR = 2016
SIMULATION_END_YR = 2022
DEFAULT_START_YEAR = 2018
DEFAULT_CONFIDENCE = 0.6

MAP = {
    "RO Liga 1": {"suffix": "Liga-I-Scores-and-Fixtures", "comp_id": 47},
    "UK Premier League": {"suffix": "Premier-League-Scores-and-Fixtures", "comp_id": 9},
    "SPAIN La Liga": {"suffix": "La-Liga-Scores-and-Fixtures", "comp_id": 12},
    "DE Bundesliga": {"suffix": "Bundesliga-Scores-and-Fixtures", "comp_id": 20},
    "IT Serie A": {"suffix": "Serie-A-Scores-and-Fixtures", "comp_id": 11},
    "FRANCE Ligue 1": {"suffix": "Ligue-1-Scores-and-Fixtures", "comp_id": 13},
    "BELGIA Pro League": {"suffix": "Belgian-Pro-League-Scores-and-Fixtures", "comp_id": 37},
    "BRAZIL Serie A": {"suffix": "Serie-A-Scores-and-Fixtures", "comp_id": 24, "custom_link": True},
    "CROATIA League": {"suffix": "Hrvatska-NL-Scores-and-Fixtures", "comp_id": 63},
    "CZECH League": {"suffix": "Czech-First-League-Scores-and-Fixtures", "comp_id": 66},
    "NETHERL League": {"suffix": "Eredivisie-Scores-and-Fixtures", "comp_id": 23},
    "SCOTLAND Premiership": {"suffix": "Scottish-Premiership-Scores-and-Fixtures", "comp_id": 40},
    "ARG Liga Profesional": {"suffix": "Liga-Profesional-Argentina-Scores-and-Fixtures", "comp_id": 21, "custom_link": True},
    "AUSTRALIA League": {"suffix": "A-League-Men-Scores-and-Fixtures", "comp_id": 65},
    "AUSTRIA Bundesliga": {"suffix": "Austrian-Bundesliga-Scores-and-Fixtures", "comp_id": 56},
    "DENMRK Superliga": {"suffix": "Superliga-Scores-and-Fixtures", "comp_id": 50},
    "FINLAND Veikkausliiga": {"suffix": "Veikkausliiga-Scores-and-Fixtures", "comp_id": 43, "custom_link": True},
    "GREEK Superliga": {"suffix": "Super-League-Greece-Scores-and-Fixtures", "comp_id": 27},
    "PORTUGAL Superliga": {"suffix": "Primeira-Liga-Scores-and-Fixtures", "comp_id": 32},
    "POLAND Ekstraklasa": {"suffix": "Ekstraklasa-Scores-and-Fixtures", "comp_id": 36},
    "NORWAY Eliteserien": {"suffix": "Eliteserien-Scores-and-Fixtures", "comp_id": 28, "custom_link": True},
    "SWEDEN Allsvenskan": {"suffix": "Allsvenskan-Scores-and-Fixtures", "comp_id": 29, "custom_link": True},
    "Champions League": {"suffix": "Champions-League-Scores-and-Fixtures", "comp_id": 8},
    "Europa League": {"suffix": "Europa-League-Scores-and-Fixtures", "comp_id": 19},
    "Europa Conf League": {"suffix": "Europa-Conference-League-Scores-and-Fixtures", "comp_id": 882},
    "Korea League 1": {"suffix": "K-League-1-Scores-and-Fixtures", "comp_id": 55, "custom_link": True},
    "Japan J1 League": {"suffix": "J1-League-Scores-and-Fixtures", "comp_id": 25, "custom_link": True},
    "Saudi Prof League": {"suffix": "Saudi-Professional-League-Scores-and-Fixtures", "comp_id": 70},
    "Mexic Liga MX": {"suffix": "Liga-MX-Scores-and-Fixtures", "comp_id": 31},
    "Bulgaria First League": {"suffix": "Bulgarian-First-League-Scores-and-Fixtures", "comp_id": 67},
    "Turkey SuperLiga": {"suffix": "Super-Lig-Scores-and-Fixtures", "comp_id": 26},
    "Serbia SuperLiga": {"suffix": "Serbian-SuperLiga-Scores-and-Fixtures", "comp_id": 54},
    "Hungary NB1": {"suffix": "NB-I-Scores-and-Fixtures", "comp_id": 46},
    "SPAIN La Liga 2": {"suffix": "Segunda-Division-Scores-and-Fixtures", "comp_id": 17},
    "UK League 1": {"suffix": "League-One-Scores-and-Fixtures", "comp_id": 15},
    "UK EFL Championship": {"suffix": "Championship-Scores-and-Fixtures", "comp_id": 10},
    "FRANCE Ligue 2": {"suffix": "Ligue-2-Scores-and-Fixtures", "comp_id": 60},
    "UEFA Nations League": {"suffix": "UEFA-Nations-League-Scores-and-Fixtures", "comp_id": 677},
}

leagues = [
    # {"comp": "UEFA Nations League", "start_year": 2018, "confidence": 0.6, "misc_league": True},
    # {"comp": "SPAIN La Liga 2", "start_year": 2018, "confidence": 0.6},
    # {"comp": "UK League 1", "start_year": 2018, "confidence": 0.6},
    # {"comp": "UK EFL Championship", "start_year": 2018, "confidence": 0.6},
    # {"comp": "FRANCE Ligue 2", "start_year": 2018, "confidence": 0.6},
    # {"comp": "ARG Liga Profesional", "start_year": 2018, "confidence": 0.6},
    # {"comp": "Korea League 1", "start_year": 2018, "confidence": 0.62},  # 68%
    # {"comp": "Japan J1 League", "start_year": 2020, "confidence": 0.6},  # 65%
    # {"comp": "Saudi Prof League", "start_year": 2021, "confidence": 0.6},  # 88%
    # {"comp": "Mexic Liga MX", "start_year": 2020, "confidence": 0.65},  # 67%
    # {"comp": "AUSTRALIA League", "start_year": 2017, "confidence": 0.6},
    # {"comp": "GREEK Superliga", "start_year": 2018, "confidence": 0.6},  # 74%
    {"comp": "RO Liga 1", "start_year": 2021, "confidence": 0.61},  # 72%
    # {"comp": "DE Bundesliga", "start_year": 2017, "confidence": 0.6},  # 69%
    # {"comp": "IT Serie A", "start_year": 2018, "confidence": 0.6},  # 68%
    # {"comp": "FRANCE Ligue 1", "start_year": 2018, "confidence": 0.63},  # 71%
    # {"comp": "UK Premier League", "start_year": 2017, "confidence": 0.6},  # 70%
    # {"comp": "SPAIN La Liga", "start_year": 2018, "confidence": 0.6},  # 67%
    # {"comp": "BRAZIL Serie A", "start_year": 2019, "confidence": 0.6},  # 74%
    # {"comp": "BELGIA Pro League", "start_year": 2020, "confidence": 0.59},  # 78%
    # {"comp": "CROATIA League", "start_year": 2018, "confidence": 0.6},  # 70%
    # {"comp": "CZECH League", "start_year": 2020, "confidence": 0.55},  # 69%
    # {"comp": "NETHERL League", "start_year": 2020, "confidence": 0.57},  # 73%
    # {"comp": "SCOTLAND Premiership", "start_year": 2019, "confidence": 0.55},  # 74%
    # {"comp": "AUSTRIA Bundesliga", "start_year": 2018, "confidence": 0.62},  # 70%
    # {"comp": "DENMRK Superliga", "start_year": 2018, "confidence": 0.65},  # 67%
    # {"comp": "FINLAND Veikkausliiga", "start_year": 2018, "confidence": 0.58},  # 64%
    # {"comp": "PORTUGAL Superliga", "start_year": 2019, "confidence": 0.6},  # 83%
    # {"comp": "POLAND Ekstraklasa", "start_year": 2019, "confidence": 0.6},  # 74%
    # {"comp": "NORWAY Eliteserien", "start_year": 2018, "confidence": 0.6},  # 70%
    # {"comp": "SWEDEN Allsvenskan", "start_year": 2019, "confidence": 0.6},  # 73%
    # {"comp": "Bulgaria First League", "start_year": 2020, "confidence": 0.57},  # 71%
    # {"comp": "Turkey SuperLiga", "start_year": 2020, "confidence": 0.6},  # 79%
    # {"comp": "Serbia SuperLiga", "start_year": 2021, "confidence": 0.6},  # 79%
    # {"comp": "Hungary NB1", "start_year": 2019, "confidence": 0.6},  # 71%
    # {"comp": "Champions League", "start_year": 2017, "confidence": 0.58, "misc_league": True},  # 74%
    # {"comp": "Europa League", "start_year": 2017, "confidence": 0.58, "misc_league": True,},  # 74%
    # {"comp": "Europa Conf League", "start_year": 2021, "confidence": 0.57, "misc_league": True,},
]

user_agents = [
    "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Falkon/22.12.1 QtWebEngine/5.15.13 Chrome/87.0.4280.144 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.43",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) SalamWeb/1.0.0.20 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.130 Safari/537.36",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_46_93) AppleWebKit/532.87.34 (KHTML, like Gecko) Chrome/56.3.7581.2219 Safari/533.27 Edge/36.11305",
    "Mozilla/5.0 (X11; CrOS aarch64 15117.17.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.107.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 8_0) AppleWebKit/557.54 (KHTML, like Gecko) Chrome/99.0.716 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 9_0_2) AppleWebKit/566.38 (KHTML, like Gecko) Chrome/99.0.2519 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 17.1.2) AppleWebKit/800.6.25 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 17.1.2) AppleWebKit/800.6.25 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_18_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]
