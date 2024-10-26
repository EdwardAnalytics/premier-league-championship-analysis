import pandas as pd
from src.data_preperation.join_pl_championship_data import (
    process_league_data,
    join_pl_champ_data,
    format_joined_data,
)
import yaml

# Load the YAML file showing duplicate player names
file_path = "conf/duplicated_player_names.yaml"
with open(file_path, "r") as file:
    duplicated_player_names = yaml.safe_load(file)

premier_league_goals = pd.read_csv(
    "data/premier_league_goals/combined_seasons/premier_league_goals.csv"
)
premier_league_assists = pd.read_csv(
    "data/premier_league_assists/combined_seasons/premier_league_assists.csv"
)
championship_goals = pd.read_csv(
    "data/championship_goals/combined_seasons/championship_goals.csv"
)
championship_assists = pd.read_csv(
    "data/championship_assists/combined_seasons/championship_assists.csv"
)

# Join PL and Championship data individualy
premier_league_merged = process_league_data(
    goals_df=premier_league_goals,
    assists_df=premier_league_assists,
    duplicated_player_names=duplicated_player_names,
)
championship_merged = process_league_data(
    goals_df=championship_goals,
    assists_df=championship_assists,
    duplicated_player_names=duplicated_player_names,
)

# Join PL and Championship data
pl_champ_merged = join_pl_champ_data(
    pl_df=premier_league_merged, champ_df=championship_merged
)
pl_champ_merged = format_joined_data(pl_champ_merged)

# Save as csv
pl_champ_merged.to_csv("data/premier_league_championship_joined.csv", index=False)
