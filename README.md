# Elo Football Ratings

Elo Football Ratings computes Elo ratings and match win probabilities using historical and current match data (scraped from FBref). It simulates seasons across start-years and confidence thresholds to find optimal prediction parameters, saves scheduled predictions to PostgreSQL, and exports played matches/results to CSV archives.

Features
- Scrapes fixtures and results from FBref
- Computes Elo ratings with adjustable K-values and confidence thresholds
- Runs simulations to find best start-year and confidence
- Saves scheduled predictions to DB and exports played matches to archive/*.csv
- Rich terminal table display for upcoming predictions

Requirements
- Python 3.9+
- See requirements.txt for pinned dependencies (beautifulsoup4, pandas, requests, rich, psycopg2)

Configuration
- Edit league list and mappings: src/config.py
- Environment variables for PostgreSQL (used by default):
  - DB_HOST
  - DB_NAME
  - DB_USERNAME
  - DB_PASSWORD
  - DB_PORT

Behavior notes
- The code creates two DB tables on startup: `played_games` and `scheduled_games` (see src/db/queries.py).
- If the DB is not available, the extraction class can be adapted to use local CSV exports instead (methods/extract_matches.py uses local CSV when use_db=False).
- Output CSVs are written to archive/{competition}.csv and intermediate export files named like archive/{start_year}-{current_year}-{comp}.csv

Usage
1. Install dependencies:
   pip install -r requirements.txt

2. Set required environment variables for PostgreSQL, e.g. (bash):
   export DB_HOST=localhost
   export DB_NAME=elo_db
   export DB_USERNAME=elo_user
   export DB_PASSWORD=secret
   export DB_PORT=5432

3. Run the main script from the repository root:
   python src/main.py

Customization
- Tweak initial ratings, K-brackets, simulation years and thresholds in src/config.py
- Add/remove competitions or adjust start years/confidences in the `leagues` tuple

Development
- Core modules:
  - src/methods/extract_matches.py — scraping and parsing fixtures & results
  - src/methods/elo_ratings.py — Elo calculation, predictions, exports
  - src/methods/simulation_runner.py — brute-force simulation over years/confidences
  - src/db — DB helpers, queries, and display table

