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

# TODO: add added_at column
CREATE_SCHEDULED_GAMES_TABLE = f"""
    CREATE TABLE IF NOT EXISTS scheduled_games (
        match_time                          varchar(200),
        teams                               varchar(200),
        prediction                          varchar(200),
        competition                         varchar(200),
        correct_predictions                 varchar(200),
        correct_predictions_with_draws      varchar(200),
        PRIMARY KEY (match_time, teams)
    )
"""

CREATE_STAGING_TABLE = """
"""
