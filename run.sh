#!/bin/bash

# Build and start the Docker containers
docker-compose up --build -d

# Execute the main Python script inside the app container
docker-compose exec app /bin/bash -c "python3 main.py"

# Optionally, you can add commands to stop the containers after the script finishes
# docker-compose down
# docker-compose config | grep 'name'
# docker volume rm elo-football-ratings-main_postgres_data
