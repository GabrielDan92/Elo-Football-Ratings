CREATE_PLAYED_GAMES_TABLE = """
    CREATE TABLE IF NOT EXISTS played_games (
        date_hour       varchar(200),
        home_team       varchar(100),
        away_team       varchar(100),
        home_score      int,
        away_score      int,
        competition     varchar(100),
        added_at        timestamp DEFAULT current_timestamp,
        PRIMARY KEY (date_hour, home_team)
    )
"""
CREATE_SCHEDULED_GAMES_TABLE = f"""
    CREATE TABLE IF NOT EXISTS scheduled_games (
        match_time                          varchar(200),
        teams                               varchar(200),
        prediction                          varchar(200),
        competition                         varchar(200),
        correct_predictions                 varchar(200),
        correct_predictions_with_draws      varchar(200),
        added_at                            timestamp DEFAULT current_timestamp,
        PRIMARY KEY (match_time, teams)
    )
"""

CREATE_STAGING_TABLE = """
"""

# TODO: add staging/future matches table

GET_MATCHES = (
    lambda competition: f"""
    SELECT * from played_games WHERE competition = '{competition}'
"""
)

GET_MATCHES_IN_TARGET_YEAR = """
    SELECT count(*) from played_games WHERE date_hour LIKE %s AND competition = %s
"""

INSERT_PLAYED_GAMES = """
    INSERT INTO played_games (date_hour, home_team, away_team, home_score, away_score, competition)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (date_hour, home_team) DO NOTHING
"""

INSERT_SCHEDULED_GAMES = """
    INSERT INTO scheduled_games (
        match_time, 
        teams, 
        prediction, 
        competition, 
        correct_predictions, 
        correct_predictions_with_draws
    )
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (match_time, teams) DO 
        UPDATE SET
             match_time = EXCLUDED.match_time,
             teams = EXCLUDED.teams,
             prediction = EXCLUDED.prediction,
             competition = EXCLUDED.competition,
             correct_predictions = EXCLUDED.correct_predictions,
             correct_predictions_with_draws = EXCLUDED.correct_predictions_with_draws
"""


"""
select * from scheduled_games 
where date(match_time) >= CURRENT_DATE
order by match_time asc, correct_predictions desc;
"""
