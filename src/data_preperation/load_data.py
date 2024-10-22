import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


def fetch_html(url):
    """
    Fetches the HTML content from the given URL.

    Parameters
    ----------
    url : str
        The URL of the webpage to fetch.

    Returns
    -------
    str
        The HTML content of the webpage. Returns None if the request fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def parse_table(html, headers):
    """
    General function to parse HTML table content and return it as a DataFrame.

    Parameters
    ----------
    html : str
        The HTML content of the webpage.
    headers : list
        List of column headers for the table.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the table data. Returns an empty DataFrame if no table is found.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "standard_tabelle"})

    if not table:
        print("Table not found on the page.")
        return pd.DataFrame()

    # Extract table rows
    rows = table.find_all("tr")[1:]  # Skip the header row

    # Prepare data for the DataFrame
    data = []
    for row in rows:
        columns = row.find_all("td")
        processed_columns = [col.text.strip().split("\n")[-1] for col in columns]
        data.append(processed_columns)

    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)

    return df


def clean_goals_column(df):
    """
    Cleans the 'Goals' column in the given DataFrame by extracting the number of goals.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the 'Goals' column.

    Returns
    -------
    pd.DataFrame
        The DataFrame with the cleaned 'Goals' column.
    """
    if "Goals" in df.columns:
        df["Goals"] = df["Goals"].apply(lambda goal_str: goal_str.split(" ")[0])
    return df


def parse_goals_table(html):
    """
    Parses the HTML content and extracts the goals table data.

    Parameters
    ----------
    html : str
        The HTML content of the webpage.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the goal data.
    """
    headers = ["#", "Player", "", "Country", "Team", "Goals"]
    df = parse_table(html=html, headers=headers)

    # Clean the goals column
    df = clean_goals_column(df)

    return df


def parse_assists_table(html):
    """
    Parses the HTML content and extracts the assists table data.

    Parameters
    ----------
    html : str
        The HTML content of the webpage.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the assist data.
    """
    headers = ["#", "Player", "", "Country", "Team", "Assists"]
    return parse_table(html=html, headers=headers)


def get_season_data(url, season, metric, sleep_time=0.5):
    """
    Gets data (goals or assists) for a specific season from the given URL.

    Parameters
    ----------
    url : str
        The URL of the webpage to get data from.
    season : str
        The season for which to get the data.
    metric : str
        Either 'goals' or 'assists' to determine which table to parse.
    sleep_time : float, optional
        Time to sleep between requests to avoid overloading the server (default is 0.5 seconds).

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the data for the given season. Returns an empty DataFrame if getting data fails.
    """
    html = fetch_html(url=url)
    if html is None:
        return pd.DataFrame()

    if metric == "goals":
        df = parse_goals_table(html=html)
    elif metric == "assists":
        df = parse_assists_table(html=html)

    # Add season column
    if not df.empty:
        df["Season"] = season

    # Drop unnecessary columns
    df = df.drop(columns=["#", ""], errors="ignore")

    # Sleep to avoid overloading the server
    time.sleep(sleep_time)

    return df


def get_all_season_data(seasons, league, metric, sleep_time=0.5):
    """
    Gets data (goals or assists) for multiple seasons and writes them as individual CSVs.

    Parameters
    ----------
    seasons : dict
        A dictionary where keys are season strings and values are URLs to get data from for those seasons.
    metric : str
        Either 'goals' or 'assists' to determine which data to get.
    sleep_time : float, optional
        Time to sleep between requests to avoid overloading the server (default is 0.5 seconds).
    """
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)

    for season, url in seasons.items():
        print(f"Getting {metric} data for season {season}...")

        # Fetch data for the current season
        season_data = get_season_data(
            url=url, season=season, metric=metric, sleep_time=sleep_time
        )

        if not season_data.empty:
            # Define file path
            file_path = f"data/{league}_{metric}/{season}.csv"

            # Save each season's data to a separate CSV file
            season_data.to_csv(file_path, index=False)
            print(f"Data for season {season} saved to {file_path}.")
        else:
            print(f"No data available for season {season}.")


def generate_urls(league_name, stat_type, start_season, end_season):
    """
    Generate URLs for a specified league and statistical type across a range of seasons.

    Parameters
    ----------
    league_name : str
        The name of the league for which the URLs are being generated.
    stat_type : str
        The type of statistics (e.g., goals, matches) for which the URLs are being generated.
    start_season : int
        The starting year of the season range (inclusive).
    end_season : int
        The ending year of the season range (exclusive).

    Returns
    -------
    dict
        A dictionary where keys are season strings in the format "YYYY-YYYY"
        and values are the corresponding URLs for the specified league and statistic type.
    """
    urls = {}
    for year in range(start_season, end_season):
        season_str = f"{year}-{str(year + 1)}"
        urls[season_str] = (
            f"https://www.worldfootball.net/{stat_type}/{league_name}-{season_str}/"
        )
    return urls


def combine_csvs(directory_path):
    """
    Combine all CSV files in a specified directory into a single DataFrame.

    Parameters
    ----------
    directory_path : str
        The path to the directory containing the CSV files to be combined.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the combined data from all CSV files in the directory.
        Additionally, a new column 'season_start' is added, representing the start year
        extracted from the 'Season' column.
    """
    # List to store DataFrames
    data_frames = []

    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            # Read the CSV file into a DataFrame and append to the list
            df = pd.read_csv(file_path)
            data_frames.append(df)

    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(data_frames, ignore_index=True)

    # Extract season_start from the "Season" column and convert to int
    combined_df["season_start"] = combined_df["Season"].str[:4].astype(int)

    return combined_df


def combine_save_csvs(league_metric):
    """
    Combine CSV files for a specified league metric and save the result to a new CSV file.

    Parameters
    ----------
    league_metric : str
        The metric associated with the league (e.g., "premier-league-goals")
        which defines the directory for input CSV files and the output file name.

    Returns
    -------
    None
        The function does not return a value. It saves the combined DataFrame
        to a CSV file in a specified directory.
    """
    directory_path = f"data/{league_metric}"
    csv_save_path = f"{directory_path}/combined_seasons/{league_metric}.csv"
    premier_league_goals = combine_csvs(directory_path)
    premier_league_goals.to_csv(csv_save_path, index=False)
