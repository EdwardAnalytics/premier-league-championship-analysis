from src.data_preperation.load_pl_championship_data import (
    generate_urls,
    get_all_season_data,
    combine_save_csvs,
)

# Constants for URL parameters
start_season_premier_league = 2000
start_season_championship_assists = 2014
start_season_championship_goals = 2000
end_season = 2024

# Generate URLs for Premier League Goals and Assists
PREMIER_LEAGUE_GOAL_URLS = generate_urls(
    league_name="eng-premier-league",
    stat_type="goalgetter",
    start_season=start_season_premier_league,
    end_season=end_season,
)
PREMIER_LEAGUE_ASSISTS = generate_urls(
    league_name="eng-premier-league",
    stat_type="assists",
    start_season=start_season_premier_league,
    end_season=end_season,
)

# Generate URLs for Championship Goals and Assists
CHAMPIONSHIP_GOAL_URLS = generate_urls(
    league_name="eng-championship",
    stat_type="goalgetter",
    start_season=start_season_championship_goals,
    end_season=end_season,
)
CHAMPIONSHIP_ASSIST_URLS = generate_urls(
    league_name="eng-championship",
    stat_type="assists",
    start_season=start_season_championship_assists,
    end_season=end_season,
)


# Fetch and save goal data
sleep_time = 0.01
get_all_season_data(
    seasons=PREMIER_LEAGUE_GOAL_URLS,
    league="premier_league",
    metric="goals",
    sleep_time=sleep_time,
)
get_all_season_data(
    seasons=PREMIER_LEAGUE_ASSISTS,
    league="premier_league",
    metric="assists",
    sleep_time=sleep_time,
)
get_all_season_data(
    seasons=CHAMPIONSHIP_GOAL_URLS,
    league="championship",
    metric="goals",
    sleep_time=sleep_time,
)
get_all_season_data(
    seasons=CHAMPIONSHIP_ASSIST_URLS,
    league="championship",
    metric="assists",
    sleep_time=sleep_time,
)

# Combine and save data
for league_metric in [
    "premier_league_goals",
    "premier_league_assists",
    "championship_goals",
    "championship_assists",
]:
    combine_save_csvs(league_metric=league_metric)
