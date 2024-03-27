import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
from helpers import json_key_path, dataset_name, project_id

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)

# Define your dataset and table names
table_name = 'batter_stats_agg'

# SQL query to retrieve league averages
league_avg_query = f"""
WITH LeagueAverages AS (
  SELECT
    SUM(total_hits) / SUM(total_at_bats) AS league_avg_avg,
    (SUM(total_hits) + SUM(total_walks) + SUM(total_hbp)) / (SUM(total_at_bats) + SUM(total_walks) + SUM(total_hbp) + SUM(total_sf)) AS league_avg_obp,
    (SUM(total_hits) - SUM(total_2b) - SUM(total_3b) - SUM(total_hr) + (2 * SUM(total_2b)) + (3 * SUM(total_3b)) + (4 * SUM(total_hr))) / SUM(total_at_bats) AS league_avg_slg
  FROM
    `{project_id}.{dataset_name}.{table_name}`
  WHERE 
    avg_ab >= 300
)
SELECT * FROM LeagueAverages
"""

# Run the query to fetch league averages
league_averages = client.query(league_avg_query).to_dataframe()

# Calculate adjusted stats for each player in a separate query
query2 = f"""
SELECT
  *,
  total_hits - (total_at_bats * {league_averages['league_avg_avg'].iloc[0]}) AS hits_above_avg,
  ((total_hits + total_walks + total_hbp) / (total_at_bats + total_walks + total_hbp + total_sf)) - {league_averages['league_avg_obp'].iloc[0]} AS obp_above_avg,
  (((total_hits - total_2b - total_3b - total_hr) + (2 * total_2b) + (3 * total_3b) + (4 * total_hr)) / total_at_bats) - {league_averages['league_avg_slg'].iloc[0]} AS slg_above_avg
FROM
  `{project_id}.{dataset_name}.{table_name}`
"""

# Run query2 to fetch player data with adjusted stats
player_data_with_adjusted_stats = client.query(query2).to_dataframe()

# Compute standard deviation for adjusted stats within the player data
std_dev_hits_above_avg = np.std(player_data_with_adjusted_stats['hits_above_avg'], ddof=1)  # ddof=1 for sample standard deviation
std_dev_obp_above_avg = np.std(player_data_with_adjusted_stats['obp_above_avg'], ddof=1)
std_dev_slg_above_avg = np.std(player_data_with_adjusted_stats['slg_above_avg'], ddof=1)

# Output the standard deviations
print("Standard Deviation of Hits Above Average:", std_dev_hits_above_avg)
print("Standard Deviation of OBP Above Average:", std_dev_obp_above_avg)
print("Standard Deviation of SLG Above Average:", std_dev_slg_above_avg)

# Display adjusted player stats
print(player_data_with_adjusted_stats)

# Define the destination table ID
destination_table_id = f"{project_id}.{dataset_name}.batter_adjusted_stats"

# Write the DataFrame to the new BigQuery table
player_data_with_adjusted_stats.to_gbq(destination_table_id, project_id=project_id, if_exists='replace', credentials=credentials)

print(f"Data written to {destination_table_id}")
