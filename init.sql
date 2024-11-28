CREATE TABLE IF NOT EXISTS played_games (
    date_hour       varchar(200),
    home_team       varchar(100),
    away_team       varchar(100),
    home_score      int,
    away_score      int,
    competition     varchar(100),
    added_at        timestamp DEFAULT current_timestamp,
    PRIMARY KEY (date_hour, home_team)
);

CREATE TABLE IF NOT EXISTS scheduled_games (
    id INT GENERATED ALWAYS AS IDENTITY,
    match_time                          varchar(200),
    teams                               varchar(200),
    prediction                          varchar(200),
    competition                         varchar(200),
    correct_predictions                 varchar(200),
    correct_predictions_with_draws      varchar(200),
    bet                                 boolean DEFAULT FALSE,
    added_at                            timestamp DEFAULT current_timestamp,
    PRIMARY KEY (match_time, teams)
);
