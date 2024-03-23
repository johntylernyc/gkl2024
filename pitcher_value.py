from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
from helpers.config_bigquery import dataset_name, json_key_path, project_id

# Authenticate and create a BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Define your dataset and table names
table_name = 'pitcher_player_consistency'

query = f"""
SELECT
  AVG(avg_ip) AS league_avg_ip, 
  STDDEV(avg_ip) AS stddev_ip,
  AVG(avg_app) AS league_avg_app, 
  STDDEV(avg_app) AS stddev_app, 
  AVG(avg_w) AS league_avg_w, 
  STDDEV(avg_w) AS stddev_w, 
  AVG(avg_sv) AS league_avg_sv, 
  STDDEV(avg_sv) AS stddev_sv, 
  AVG(avg_k) AS league_avg_k, 
  STDDEV(avg_k) AS stddev_k,
  AVG(avg_hld) AS league_avg_hld, 
  STDDEV(avg_hld) AS stddev_hld,
  AVG(avg_qs) AS league_avg_qs, 
  STDDEV(avg_qs) AS stddev_qs,
  AVG(total_er * 9 / NULLIF(total_ip, 0)) AS league_avg_era,
  STDDEV(total_er * 9 / NULLIF(total_ip, 0)) AS stddev_era,
  AVG((total_bb + total_h) / NULLIF(total_ip, 0)) AS league_avg_whip,
  STDDEV((total_bb + total_h) / NULLIF(total_ip, 0)) AS stddev_whip,
  AVG(total_k / NULLIF(total_bb, 0)) AS league_avg_k_bb,
  STDDEV(total_k / NULLIF(total_bb, 0)) AS stddev_k_bb,
  AVG(earned_runs_below_avg) AS avg_earned_runs_below_avg, 
  STDDEV(earned_runs_below_avg) AS stddev_earned_runs_below_avg,
  AVG(walks_hits_below_avg) AS avg_walks_hits_below_avg, 
  STDDEV(walks_hits_below_avg) AS stddev_walks_hits_below_avg,
  AVG(k_bb_ratio_adjustment) AS avg_k_bb_ratio_adjustment, 
  STDDEV(k_bb_ratio_adjustment) AS stddev_k_bb_ratio_adjustment
FROM
  `{project_id}.{dataset_name}.{table_name}`
WHERE 
  avg_ip >= 30  # Assuming a minimum innings pitched threshold
"""


# Run the query for league averages
league_averages = client.query(query).to_dataframe()

# Display the league averages
print(league_averages)

# Query to retrieve pitcher data
query2 = f"""
  SELECT * 
  FROM
    `{project_id}.{dataset_name}.{table_name}`
"""

# Run the query for pitcher data
pitcher_data = client.query(query2).to_dataframe()

# Calculate value for counting stats where higher values are better
pitcher_data['value_app'] = (pitcher_data['avg_app'] - league_averages['league_avg_app'].iloc[0]) / league_averages['stddev_app'].iloc[0]
pitcher_data['value_w'] = (pitcher_data['avg_w'] - league_averages['league_avg_w'].iloc[0]) / league_averages['stddev_w'].iloc[0]
pitcher_data['value_sv'] = (pitcher_data['avg_sv'] - league_averages['league_avg_sv'].iloc[0]) / league_averages['stddev_sv'].iloc[0]
pitcher_data['value_k'] = (pitcher_data['avg_k'] - league_averages['league_avg_k'].iloc[0]) / league_averages['stddev_k'].iloc[0]
pitcher_data['value_hld'] = (pitcher_data['avg_hld'] - league_averages['league_avg_hld'].iloc[0]) / league_averages['stddev_hld'].iloc[0]
pitcher_data['value_qs'] = (pitcher_data['avg_qs'] - league_averages['league_avg_qs'].iloc[0]) / league_averages['stddev_qs'].iloc[0]

# Calculate value for pitching stats where lower values are better (like ERA and WHIP)
# For these, we reverse the subtraction order to reflect that lower values are preferable
pitcher_data['value_era'] = (league_averages['league_avg_era'].iloc[0] - pitcher_data['avg_era']) / league_averages['stddev_era'].iloc[0]
pitcher_data['value_whip'] = (league_averages['league_avg_whip'].iloc[0] - pitcher_data['avg_whip']) / league_averages['stddev_whip'].iloc[0]

# Calculate value for the K/BB ratio where higher values are better
pitcher_data['value_k_bb'] = (pitcher_data['avg_k_bb'] - league_averages['league_avg_k_bb'].iloc[0]) / league_averages['stddev_k_bb'].iloc[0]

# Calculate total player value by summing individual category values, including the adjusted values for ERA and WHIP
pitcher_data['total_value'] = pitcher_data[['value_app', 'value_w', 'value_sv', 'value_k', 'value_hld', 'value_qs', 'value_era', 'value_whip', 'value_k_bb']].sum(axis=1)

# Sort by total value to get rankings
pitcher_value_rankings = pitcher_data.sort_values(by='total_value', ascending=False)

# Convert 'eligible_positions' from comma-separated string to list
pitcher_value_rankings['eligible_positions_list'] = pitcher_value_rankings['eligible_positions'].apply(lambda x: x.split(',') if x else [])

# Get a set of all unique positions
all_positions = set()
pitcher_value_rankings['eligible_positions_list'].apply(lambda positions: all_positions.update(positions))

# Initialize columns for position ranks
for position in all_positions:
    pitcher_value_rankings[f'{position.lower()}_rank'] = None

# Rank players for each position
for index, row in pitcher_value_rankings.iterrows():
    for position in row['eligible_positions_list']:
        # Filter players eligible for the current position
        eligible_players = pitcher_value_rankings[pitcher_value_rankings['eligible_positions_list'].apply(lambda positions: position in positions)]
        # Sort eligible players by total_value and get the rank
        ranked_players = eligible_players.sort_values(by='total_value', ascending=False).reset_index()
        rank = ranked_players.index[ranked_players['IDfg'] == row['IDfg']].tolist()[0] + 1  # Find the rank of the current player
        # Assign rank to the respective position column
        pitcher_value_rankings.at[index, f'{position.lower()}_rank'] = rank

# Clean up by removing the temporary 'eligible_positions_list' column
pitcher_value_rankings.drop(columns=['eligible_positions_list'], inplace=True)

# Convert rank columns to integers if they exist
rank_columns = [col for col in pitcher_value_rankings.columns if col.endswith('_rank')]
pitcher_value_rankings[rank_columns] = pitcher_value_rankings[rank_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Drop duplicate IDfg records, keeping the first occurrence
pitcher_value_rankings = pitcher_value_rankings.drop_duplicates(subset='IDfg', keep='first')

def adjust_total_value(row):
    adjusted_value = row['total_value']
    
    # Apply bonus for overall_consistency > 0.90
    if row['overall_consistency'] > 0.90:
        adjusted_value *= 1.1
    
    # Apply bonus for LatestAge between 26 and 30
    if 26 <= row['LatestAge'] <= 30:
        adjusted_value *= 1.1
    
    # Apply bonus for more than one eligible position
    if ',' in row['eligible_positions']:
        adjusted_value *= 1.05
    
    # Apply penalty for overall_consistency < 0.60
    if row['overall_consistency'] < 0.60:
        adjusted_value *= 0.9
    
    # Apply penalty for LatestAge > 33
    if row['LatestAge'] > 33:
        adjusted_value *= 0.85
    
    return adjusted_value

# Apply adjustments to total value based on consistency, age, and eligibility
pitcher_value_rankings['adjusted_total_value'] = pitcher_data.apply(adjust_total_value, axis=1)

# Remove players with the specified IDfg values because they were kept
pitcher_keepers_2024 = [21846, 25436, 22267, 13774, 13449, 1675, 27498]

pitcher_value_rankings_filtered = pitcher_value_rankings[~pitcher_value_rankings['IDfg'].isin(pitcher_keepers_2024)]

# Calculate draft value
pitcher_value_rankings_filtered['player_draft_value'] = pitcher_value_rankings_filtered['adjusted_total_value'] * 1.66

# Save the output DataFrame to a new CSV file
pitcher_value_rankings_filtered.to_csv('pitcher_value_final.csv', index=False)

# Define the destination table ID for pitcher player value
destination_table_id = f"{project_id}.{dataset_name}.pitcher_values_final.csv"

# Step 4: Write to BigQuery
pitcher_value_rankings_filtered.to_gbq(
    destination_table_id,
    project_id=project_id,
    if_exists='replace',
    credentials=credentials
)

print(f"Data written to {destination_table_id}")
