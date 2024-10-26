import pandas as pd
import numpy as np


def rename_duplicated_players(df, duplicated_player_names):
    """
    Rename players in the DataFrame based on duplicated player names.

    Parameters:
    df (pd.DataFrame): The DataFrame containing player statistics (e.g., goals).
    duplicated_player_names (pd.DataFrame): A DataFrame containing duplicated player names with columns 'Player', 'Team', 'Season', and 'Rename'.

    Returns:
    pd.DataFrame: The modified DataFrame with updated player names.
    """
    for player_info in duplicated_player_names:
        # Apply conditions to match 'Player', 'Team', and 'Season'
        condition = (df["Player"] == player_info["Player"]) & (
            df["Team"] == player_info["Team"]
        )

        # Replace player name with 'Rename' if conditions match
        df.loc[condition, "Player"] = player_info["Rename"]

    return df


import pandas as pd


def fill_missing_values(merged_df):
    """
    Fill missing values in the DataFrame.

    Parameters
    ----------
    merged_df : pd.DataFrame
        The DataFrame containing merged player data with potentially missing values.

    Returns
    -------
    pd.DataFrame
        The DataFrame with missing values filled.
    """
    merged_df["Assists"] = merged_df["Assists"].fillna(0)
    merged_df["Goals"] = merged_df["Goals"].fillna(0)
    merged_df["Team"] = (
        merged_df["Team"].fillna("Unknown").astype(str)
    )  # Ensure all entries are strings
    return merged_df


def group_data(merged_df):
    """
    Group the DataFrame by Player, Season, Country, and season_start.

    Parameters
    ----------
    merged_df : pd.DataFrame
        The DataFrame containing player data to be grouped.

    Returns
    -------
    pd.DataFrame
        The grouped DataFrame with aggregated Assists and Goals.
    """
    return (
        merged_df.groupby(["Player", "Season", "Country", "season_start"])
        .agg(
            {
                "Team": lambda x: " / ".join(sorted(set(x))),
                "Assists": "sum",
                "Goals": "sum",
            }
        )
        .reset_index()
    )


def process_league_data(goals_df, assists_df, duplicated_player_names):
    """
    Process and merge league goals and assists data.

    Parameters
    ----------
    goals_df : pd.DataFrame
        DataFrame containing players' goals data.
    assists_df : pd.DataFrame
        DataFrame containing players' assists data.
    duplicated_player_names : list
        List of names of duplicated players to rename.

    Returns
    -------
    pd.DataFrame
        A processed DataFrame containing merged and aggregated data for players.
    """

    # Rename duplicate player names
    goals_df = rename_duplicated_players(
        df=goals_df, duplicated_player_names=duplicated_player_names
    )
    assists_df = rename_duplicated_players(
        df=assists_df, duplicated_player_names=duplicated_player_names
    )

    # Merge goals and assists DataFrames
    merged_df = pd.merge(
        assists_df,
        goals_df,
        on=["Player", "Country", "Team", "Season", "season_start"],
        how="outer",
    )

    # Fill missing values
    merged_df = fill_missing_values(merged_df)

    # Select final columns
    merged_df = merged_df[
        ["Player", "Country", "Team", "Assists", "Season", "season_start", "Goals"]
    ]

    # Group data
    merged_df = group_data(merged_df)

    return merged_df


def merge_dataframes(pl_df, champ_df):
    """
    Merges the Premier League and Championship DataFrames on specified columns.

    Parameters
    ----------
    pl_df : pd.DataFrame
        DataFrame containing Premier League data.
    champ_df : pd.DataFrame
        DataFrame containing Championship data.

    Returns
    -------
    pd.DataFrame
        Merged DataFrame with the `lagged_season_start` column dropped.
    """
    merged_df = pd.merge(
        pl_df,
        champ_df,
        left_on=["Player", "Country", "season_start"],
        right_on=["Player", "Country", "lagged_season_start"],
        suffixes=("_premier_league", "_championship"),
        how="inner",
    )
    return merged_df.drop(columns=["lagged_season_start"])


import pandas as pd
import numpy as np


def create_lagged_season(champ_df):
    """
    Creates a lagged season_start column in the Championship DataFrame.

    Parameters
    ----------
    champ_df
        DataFrame containing Championship data.

    Returns
    -------
        Championship DataFrame with the lagged_season_start column added.
    """
    champ_df["lagged_season_start"] = champ_df["season_start"] + 1
    return champ_df


def merge_dataframes(pl_df, champ_df):
    """
    Merges the Premier League and Championship DataFrames on specified columns.

    Parameters
    ----------
    pl_df
        DataFrame containing Premier League data.
    champ_df
        DataFrame containing Championship data.

    Returns
    -------
        Merged DataFrame with the `lagged_season_start` column dropped.
    """
    merged_df = pd.merge(
        pl_df,
        champ_df,
        left_on=["Player", "Country", "season_start"],
        right_on=["Player", "Country", "lagged_season_start"],
        suffixes=("_premier_league", "_championship"),
        how="inner",
    )
    return merged_df.drop(columns=["lagged_season_start"])


def rename_columns(df):
    """
    Renames specific columns in the DataFrame for clarity.

    Parameters
    ----------
    df
        DataFrame to rename columns in.

    Returns
    -------
        DataFrame with renamed columns.
    """
    df.rename(
        columns={
            "Season_premier_league": "Season (PL)",
            "season_start_premier_league": "Season Start (PL)",
            "Season_championship": "Season (Champ.)",
            "season_start_championship": "Season Start (Champ.)",
            "Team_premier_league": "Team (PL)",
            "Assists_premier_league": "Assists (PL)",
            "Goals_premier_league": "Goals (PL)",
            "Team_championship": "Team (Champ.)",
            "Assists_championship": "Assists (Champ.)",
            "Goals_championship": "Goals (Champ.)",
            "same_team": "With Promoted Team",
        },
        inplace=True,
    )
    return df


def add_same_team_column(df):
    """
    Adds a column to the DataFrame indicating if the player is on the same team in both leagues.

    Parameters
    ----------
    df
        DataFrame to add the same_team column to.

    Returns
    -------
        DataFrame with the same_team column added.
    """
    df["same_team"] = np.where(df["Team (PL)"] == df["Team (Champ.)"], 1, 0)
    return df


def join_pl_champ_data(pl_df, champ_df):
    """
    Main function to process Premier League and Championship DataFrames.

    Parameters
    ----------
    pl_df
        DataFrame containing Premier League data.
    champ_df
        DataFrame containing Championship data.

    Returns
    -------
        Final processed DataFrame after merging, renaming, and adding columns.
    """
    champ_df_with_lag = create_lagged_season(champ_df)  # Create lagged season
    merged_df = merge_dataframes(pl_df, champ_df_with_lag)  # Merge DataFrames
    renamed_df = rename_columns(merged_df)  # Rename columns
    final_df = add_same_team_column(renamed_df)  # Add same team column
    return final_df


def format_player_season(row):
    """
    Format the player's name and season into a specified string format.

    The function removes the first name from the player's name if the name consists of two or more names.
    It formats the season to a "YY/YY" format.

    Parameters
    ----------
    row : pandas.Series
        A row from the DataFrame containing 'Player' and 'Season (PL)' columns.

    Returns
    -------
    str
        A formatted string of the player's name and the season in the format "LastName (YY/YY)".

    """

    # Split the name
    name_parts = row["Player"].split()

    # Check if the name has two or more parts
    if len(name_parts) > 1:
        last_name = " ".join(name_parts[1:])  # Remove the first name
    else:
        last_name = name_parts[0]  # Keep the name as it is if only one part

    # Combine them
    return f"{last_name} ({row['Season (PL)']})"


# Define a function to format the season
def format_season(season):
    start_year, end_year = season.split("-")
    return f"{start_year}/{end_year[-2:]}"  # Get last two digits of the years


import pandas as pd


def format_joined_data(pl_champ_merged):
    """
    Format the provided DataFrames for player statistics in the Championship and Premier League.

    This function performs the following operations:
    1. Removes assists for seasons before 2014 in the championship_merged DataFrame.
    2. Shortens the season names in the pl_champ_merged DataFrame using a provided formatting function.
    3. Concatenates player names with their respective seasons to create a new full name column.
    4. Applies a player-season formatting function to create a new column with formatted player-season data.
    5. Sorts the pl_champ_merged DataFrame by season start and player name.

    Parameters
    ----------
    championship_merged : pd.DataFrame
        DataFrame containing player statistics for the Championship, which includes season start years and assists.

    pl_champ_merged : pd.DataFrame
        DataFrame containing player statistics for the Premier League and Championship, which includes season information and player names.

    format_season : function
        A function that takes a season string and returns a formatted version of that string.

    format_player_season : function
        A function that takes a row of the DataFrame and returns a formatted player-season string.

    Returns
    -------
    pd.DataFrame
        The modified pl_champ_merged DataFrame after formatting and sorting.

    Raises
    ------
    ValueError
        If the input DataFrames do not contain the expected columns.

    """

    # Remove pre 2014 assists
    pl_champ_merged.loc[
        pl_champ_merged["Season Start (Champ.)"] < 2014, "Assists (Champ.)"
    ] = None

    # Shorten season name
    pl_champ_merged["Season (PL)"] = pl_champ_merged["Season (PL)"].apply(format_season)
    pl_champ_merged["Season (Champ.)"] = pl_champ_merged["Season (Champ.)"].apply(
        format_season
    )

    # Concat Name and Season
    pl_champ_merged["Player (PL Season) - Full Name"] = (
        pl_champ_merged["Player"] + " (" + pl_champ_merged["Season (PL)"] + ")"
    )
    pl_champ_merged["Player (PL Season)"] = pl_champ_merged.apply(
        format_player_season, axis=1
    )

    # Sort
    pl_champ_merged = pl_champ_merged.sort_values(["Season Start (PL)", "Player"])

    # Remove " FC" from end of team names
    pl_champ_merged['Team (PL)'] = pl_champ_merged['Team (PL)'].str.rstrip(' FC')
    pl_champ_merged['Team (Champ.)'] = pl_champ_merged['Team (Champ.)'].str.rstrip(' FC')

    return pl_champ_merged
