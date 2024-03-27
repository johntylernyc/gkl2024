import pandas as pd
from pybaseball import batting_stats
import re

from google.cloud import bigquery
from google.oauth2 import service_account
from helpers import dataset_name, json_key_path, project_id, batter_table_name

credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)
batter_table_id = f"{project_id}.{dataset_name}.{batter_table_name}"

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

# Define the years of interest
years = [2021, 2022, 2023]

# Pull batting stats for each year with qual=50 and concatenate them
all_batting_stats = pd.concat([batting_stats(year, qual=10) for year in years], ignore_index=True)

all_batting_stats.to_csv('all_batting_stats_2021_2023.csv', index=False)

# Load the player IDs from your CSV file
players_df = pd.read_csv('/Users/johntyler/github/gkl2024/draft/draft_analysis/updated_players_data_with_fangraph_ids.csv')

# Filter the batting stats to include only the players in your list
# This is done by matching the 'IDfg' column from the batting stats with the 'IDfg' column in your players DataFrame
filtered_batting_stats = all_batting_stats[all_batting_stats['IDfg'].isin(players_df['IDfg'])]

# Merge the filtered batting stats with the players DataFrame to include the 'eligible_positions' column
final_batting_stats = pd.merge(filtered_batting_stats, players_df[['IDfg', 'eligible_positions','Cost','Team_Name']], on='IDfg', how='left')

# Save the filtered stats to a new CSV file
filtered_batting_stats.to_csv('filtered_batting_stats_2021_2023.csv', index=False)

# Apply the cleaning function to each column name
final_batting_stats.columns = [clean_column_name(col) for col in final_batting_stats.columns]
final_batting_stats.columns = [col.replace('/', '_per_') for col in final_batting_stats.columns]

# Use to_gbq to append the data to the batter_stats table in BigQuery
final_batting_stats.to_gbq(batter_table_id, project_id=project_id, if_exists='append', credentials=credentials)
