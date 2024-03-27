import pandas as pd
import numpy as np
from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.config_bigquery import json_key_path, dataset_name, project_id
import json

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)

# Define your dataset and table names
table_name = 'pitcher_stats_agg'

# SQL query to retrieve league averages for WHIP and ERA
league_avg_query = f"""
WITH LeagueAverages AS (
  SELECT
    (SUM(total_bb) + SUM(total_h)) / SUM(total_ip) AS league_whip,
    (SUM(total_er) * 9) / SUM(total_ip) AS league_era, 
    SUM(total_k) / NULLIF(SUM(total_bb), 0) AS league_k_bb_ratio
  FROM
    `{project_id}.{dataset_name}.{table_name}`
  WHERE 
    avg_ip >= 30  -- Assuming a minimum innings pitched threshold
)
SELECT * FROM LeagueAverages
"""

# Run the query to fetch league averages
league_averages = client.query(league_avg_query).to_dataframe()

# Calculate adjusted stats for each pitcher in a separate query
query2 = f"""
SELECT
  *,
  ({league_averages['league_whip'].iloc[0]} * total_ip) - (total_bb + total_h) AS walks_hits_below_avg,
  (({league_averages['league_era'].iloc[0]} / 9) * total_ip) - total_er AS earned_runs_below_avg,
  (total_k / NULLIF(total_bb, 0)) - {league_averages['league_k_bb_ratio'].iloc[0]} AS k_bb_ratio_adjustment
FROM
  `{project_id}.{dataset_name}.{table_name}`
"""

# Run query2 to fetch pitcher data with adjusted stats
pitcher_data_with_adjusted_stats = client.query(query2).to_dataframe()

# Compute standard deviation for adjusted stats within the pitcher data
std_dev_walks_hits_below_avg = np.std(pitcher_data_with_adjusted_stats['walks_hits_below_avg'], ddof=1)  # ddof=1 for sample standard deviation
std_dev_earned_runs_below_avg = np.std(pitcher_data_with_adjusted_stats['earned_runs_below_avg'], ddof=1)
std_dev_k_bb_ratio_adjustment = np.std(pitcher_data_with_adjusted_stats['k_bb_ratio_adjustment'], ddof=1)

# Output the standard deviations
print("Standard Deviation of Walks+Hits Below Average:", std_dev_walks_hits_below_avg)
print("Standard Deviation of Earned Runs Below Average:", std_dev_earned_runs_below_avg)
print("Standard Deviation of K/BB Ratio Adjustment:", std_dev_k_bb_ratio_adjustment)

# Display adjusted pitcher stats
print(pitcher_data_with_adjusted_stats)

# Define the destination table ID
destination_table_id = f"{project_id}.{dataset_name}.pitcher_adjusted_stats"

# Write the DataFrame to the new BigQuery table
pitcher_data_with_adjusted_stats.to_gbq(destination_table_id, project_id=project_id, if_exists='replace', credentials=credentials)

print(f"Data written to {destination_table_id}")
