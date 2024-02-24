MAP = {
    "RO Liga 1": {
        "suffix": "Liga-I-Scores-and-Fixtures",
        "comp_id": 47,
    },
    "UK Premier League": {
        "suffix": "Premier-League-Scores-and-Fixtures",
        "comp_id": 9,
    },
    "SPAIN La Liga": {
        "suffix": "La-Liga-Scores-and-Fixtures",
        "comp_id": 12,
    },
    "DE Bundesliga": {
        "suffix": "Bundesliga-Scores-and-Fixtures",
        "comp_id": 20,
    },
    "IT Serie A": {
        "suffix": "Serie-A-Scores-and-Fixtures",
        "comp_id": 11,
    },
    "FRANCE Ligue 1": {
        "suffix": "Ligue-1-Scores-and-Fixtures",
        "comp_id": 13,
    },
    "BELGIA Pro League": {
        "suffix": "Belgian-Pro-League-Scores-and-Fixtures",
        "comp_id": 37,
    },
    "BRAZIL Serie A": {
        "suffix": "Serie-A-Scores-and-Fixtures",
        "comp_id": 24,
        "custom_link": True,
    },
    "CROATIA League": {
        "suffix": "Hrvatska-NL-Scores-and-Fixtures",
        "comp_id": 63,
    },
    "CZECH League": {
        "suffix": "Czech-First-League-Scores-and-Fixtures",
        "comp_id": 66,
    },
    "NETHERL League": {
        "suffix": "Eredivisie-Scores-and-Fixtures",
        "comp_id": 23,
    },
    "SCOTLAND Premiership": {
        "suffix": "Scottish-Premiership-Scores-and-Fixtures",
        "comp_id": 40,
    },
    "ARG Primera Division": {
        "suffix": "Primera-Division-Scores-and-Fixtures",
        "comp_id": 21,
        "custom_link": True,
    },
    "AUSTRALIA League": {
        "suffix": "A-League-Men-Scores-and-Fixtures",
        "comp_id": 65,
    },
    "AUSTRIA Bundesliga": {
        "suffix": "Austrian-Bundesliga-Scores-and-Fixtures",
        "comp_id": 56,
    },
    "DENMRK Superliga": {
        "suffix": "Superliga-Scores-and-Fixtures",
        "comp_id": 50,
    },
    "FINLAND Veikkausliiga": {
        "suffix": "Veikkausliiga-Scores-and-Fixtures",
        "comp_id": 43,
        "custom_link": True,
    },
    "GREEK Superliga": {
        "suffix": "Super-League-Greece-Scores-and-Fixtures",
        "comp_id": 27,
    },
    "PORTUGAL Superliga": {
        "suffix": "Primeira-Liga-Scores-and-Fixtures",
        "comp_id": 32,
    },
    "POLAND Ekstraklasa": {
        "suffix": "Ekstraklasa-Scores-and-Fixtures",
        "comp_id": 36,
    },
    "NORWAY Eliteserien": {
        "suffix": "Eliteserien-Scores-and-Fixtures",
        "comp_id": 28,
        "custom_link": True,
    },
    "SWEDEN Allsvenskan": {
        "suffix": "Allsvenskan-Scores-and-Fixtures",
        "comp_id": 29,
        "custom_link": True,
    },
    "Champions League": {
        "suffix": "Champions-League-Scores-and-Fixtures",
        "comp_id": 8,
    },
    "Europa League": {
        "suffix": "Europa-League-Scores-and-Fixtures",
        "comp_id": 19,
    },
    "Europa Conf League": {
        "suffix": "Europa-Conference-League-Scores-and-Fixtures",
        "comp_id": 882,
    },
    "Korea League 1": {
        "suffix": "K-League-1-Scores-and-Fixtures",
        "comp_id": 55,
        "custom_link": True,
    },
    "Japan J1 League": {
        "suffix": "J1-League-Scores-and-Fixtures",
        "comp_id": 25,
        "custom_link": True,
    },
    "Saudi Prof League": {
        "suffix": "Saudi-Professional-League-Scores-and-Fixtures",
        "comp_id": 70,
    },
    "Mexic Liga MX": {
        "suffix": "Liga-MX-Scores-and-Fixtures",
        "comp_id": 31,
    },
    "Bulgaria First League": {
        "suffix": "Bulgarian-First-League-Scores-and-Fixtures",
        "comp_id": 67,
    },
    "Turkey SuperLiga": {
        "suffix": "Super-Lig-Scores-and-Fixtures",
        "comp_id": 26,
    },
    "Serbia SuperLiga": {
        "suffix": "Serbian-SuperLiga-Scores-and-Fixtures",
        "comp_id": 54,
    },
    "Hungary NB1": {
        "suffix": "NB-I-Scores-and-Fixtures",
        "comp_id": 46,
    },
}


INITIAL_ELO_RATING = 1500
ELO_LOWER_BRACKET = 1300
ELO_UPPER_BRACKET = 1550
WIN_PROB_DIVISOR_DOMESTIC = 600
WIN_PROB_DIVISOR_INT = 400
FIRST_MATCH = 30


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
