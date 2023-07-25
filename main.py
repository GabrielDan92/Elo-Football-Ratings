from utils import ExtractMatches, EloRatings


if __name__ == "__main__":
    e = EloRatings(ExtractMatches(start_year=2019).get_matches())
    
    e.query_interface(home_team="FC U Craiova", away_team="Universitatea Cluj")
    e.query_interface(home_team="Rapid București", away_team="Botoșani")
    e.query_interface(home_team="Hermannstadt", away_team="UTA Arad")
    e.query_interface(home_team="Oțelul Galați", away_team="FCSB")
    e.query_interface(home_team="Farul Constanța", away_team="Poli Iași")
    e.query_interface(home_team="CFR Cluj", away_team="CS U Craiova")
    e.query_interface(home_team="Petrolul Ploiești", away_team="Voluntari")
    e.query_interface(home_team="Dinamo", away_team="Sepsi")

    # e.export_results()
    e.see_win_perc()
