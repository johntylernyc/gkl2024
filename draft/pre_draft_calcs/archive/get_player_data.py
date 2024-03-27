## Global imports 

from pybaseball import batting_stats, pitching_stats
import pandas as pd
import re
from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.config_bigquery import dataset_name, json_key_path, project_id, pitcher_table_name, batter_table_name

credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)
batter_table_id = f"{project_id}.{dataset_name}.{batter_table_name}"
pitcher_table_id = f"{project_id}.{dataset_name}.{pitcher_table_name}"

# Function to clean column names
def clean_column_name(column_name):
    # Replace special characters with underscore
    clean_name = re.sub(r'[%]', '_rate', column_name)
    # Replace special characters with underscore
    clean_name = re.sub(r'[()/]', '_', column_name)
    # Replace spaces with underscore
    clean_name = re.sub(r'\s+', '_', clean_name)
    # Remove trailing underscores
    clean_name = re.sub(r'_+$', '', clean_name)
    # Prefix with an underscore if the name starts with a number
    if re.match(r'^\d', clean_name):
        clean_name = '_' + clean_name
    return clean_name

# Apply the cleaning function to each column name
player_batting = batting_stats(2021, end_season=2023, qual=200, ind=1) 
player_batting.columns = [clean_column_name(col) for col in player_batting.columns]
player_batting.columns = [col.replace('/', '_per_') for col in player_batting.columns]
player_batting.to_gbq(batter_table_id, project_id=project_id, if_exists='append', credentials=credentials)

# # Apply the cleaning function to each column name
# player_pitching = pitching_stats(2021, end_season=2023, qual=200, ind=1) 
# player_pitching.columns = [clean_column_name(col) for col in player_pitching.columns]
# player_pitching.columns = [col.replace('/', '_per_') for col in player_pitching.columns]
# player_pitching.to_gbq(pitcher_table_id, project_id=project_id, if_exists='append', credentials=credentials)
