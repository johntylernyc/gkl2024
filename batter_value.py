from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.config_bigquery import json_key_path, dataset_name, project_id
import pandas as pd

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)

# Define your dataset and table names
table_name = 'batter_player_consistency'

# SQL query to retrieve data and calculate league averages
query = f"""
SELECT
  AVG(avg_ab) AS league_avg_ab, STDDEV(avg_ab) AS stddev_ab,
  AVG(avg_r) AS league_avg_r, STDDEV(avg_r) AS stddev_r,
  AVG(avg_h) AS league_avg_h, STDDEV(avg_h) AS stddev_h,
  AVG(avg_3b) AS league_avg_3b, STDDEV(avg_3b) AS stddev_3b,
  AVG(avg_hr) AS league_avg_hr, STDDEV(avg_hr) AS stddev_hr,
  AVG(avg_rbi) AS league_avg_rbi, STDDEV(avg_rbi) AS stddev_rbi,
  AVG(avg_sb) AS league_avg_sb, STDDEV(avg_sb) AS stddev_sb,
  SUM(total_hits) / SUM(total_at_bats) AS league_avg_avg,
  (SUM(total_hits) + SUM(total_walks) + SUM(total_hbp)) / (SUM(total_at_bats) + SUM(total_walks) + SUM(total_hbp) + SUM(total_sf)) AS league_avg_obp,
  (SUM(total_hits) - SUM(total_2b) - SUM(total_3b) - SUM(total_hr) + (2 * SUM(total_2b)) + (3 * SUM(total_3b)) + (4 * SUM(total_hr))) / SUM(total_at_bats) AS league_avg_slg,
  AVG(hits_above_avg) AS avg_hits_above_avg, STDDEV(hits_above_avg) AS stddev_hits_above_avg,
  AVG(obp_above_avg) AS avg_obp_above_avg, STDDEV(obp_above_avg) AS stddev_obp_above_avg,
  AVG(slg_above_avg) AS avg_slg_above_avg, STDDEV(slg_above_avg) AS stddev_slg_above_avg
FROM
  `{project_id}.{dataset_name}.{table_name}`
WHERE 
  avg_ab >= 175
"""

# Run the query for league averages
league_averages = client.query(query).to_dataframe()

# Display the league averages
print(league_averages)

# Query to retrieve player data
query2 = f"""
  SELECT * 
  FROM
    `{project_id}.{dataset_name}.{table_name}`
"""

# Run the query for player data
player_data = client.query(query2).to_dataframe()

# Calculate value for counting stats
player_data['value_r'] = (player_data['avg_r'] - league_averages['league_avg_r'].iloc[0]) / league_averages['stddev_r'].iloc[0]
player_data['value_h'] = (player_data['avg_h'] - league_averages['league_avg_h'].iloc[0]) / league_averages['stddev_h'].iloc[0]
player_data['value_3b'] = (player_data['avg_3b'] - league_averages['league_avg_3b'].iloc[0]) / league_averages['stddev_3b'].iloc[0]
player_data['value_hr'] = (player_data['avg_hr'] - league_averages['league_avg_hr'].iloc[0]) / league_averages['stddev_hr'].iloc[0]
player_data['value_rbi'] = (player_data['avg_rbi'] - league_averages['league_avg_rbi'].iloc[0]) / league_averages['stddev_rbi'].iloc[0]
player_data['value_sb'] = (player_data['avg_sb'] - league_averages['league_avg_sb'].iloc[0]) / league_averages['stddev_sb'].iloc[0]

# Calculate value for ratio stats
player_data['value_hits_above_avg'] = player_data['hits_above_avg'] / league_averages['stddev_hits_above_avg'].iloc[0]
player_data['value_obp_above_avg'] = player_data['obp_above_avg'] / league_averages['stddev_obp_above_avg'].iloc[0]
player_data['value_slg_above_avg'] = player_data['slg_above_avg'] / league_averages['stddev_slg_above_avg'].iloc[0]

# Calculate total player value by summing individual category values
player_data['total_value'] = player_data[['value_r', 'value_h', 'value_3b', 'value_hr', 'value_rbi', 'value_sb', 'value_hits_above_avg', 'value_obp_above_avg', 'value_slg_above_avg']].sum(axis=1)

# Sort by total value to get rankings
player_value_rankings = player_data.sort_values(by='total_value', ascending=False)

# Convert 'eligible_positions' from comma-separated string to list
player_value_rankings['eligible_positions_list'] = player_value_rankings['eligible_positions'].apply(lambda x: x.split(',') if x else [])

# Get a set of all unique positions
all_positions = set()
player_value_rankings['eligible_positions_list'].apply(lambda positions: all_positions.update(positions))

# Initialize columns for position ranks
for position in all_positions:
    player_value_rankings[f'{position.lower()}_rank'] = None

# Rank players for each position
for index, row in player_value_rankings.iterrows():
    for position in row['eligible_positions_list']:
        # Filter players eligible for the current position
        eligible_players = player_value_rankings[player_value_rankings['eligible_positions_list'].apply(lambda positions: position in positions)]
        # Sort eligible players by total_value and get the rank
        ranked_players = eligible_players.sort_values(by='total_value', ascending=False).reset_index()
        rank = ranked_players.index[ranked_players['IDfg'] == row['IDfg']].tolist()[0] + 1  # Find the rank of the current player
        # Assign rank to the respective position column
        player_value_rankings.at[index, f'{position.lower()}_rank'] = rank

# Clean up by removing the temporary 'eligible_positions_list' column
player_value_rankings.drop(columns=['eligible_positions_list'], inplace=True)

# Convert rank columns to integers if they exist
rank_columns = [col for col in player_value_rankings.columns if col.endswith('_rank')]
player_value_rankings[rank_columns] = player_value_rankings[rank_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)

# Drop duplicate IDfg records, keeping the first occurrence
player_value_rankings = player_value_rankings.drop_duplicates(subset='IDfg', keep='first')

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

# Apply the adjust_total_value function to each row
player_value_rankings['adjusted_total_value'] = player_value_rankings.apply(adjust_total_value, axis=1)

# Remove players with the specified IDfg values because they were kept
batter_keepers_2024 = [
    11579, 27465, 29766, 26323, 25878, 20437, 27790, 19755, 23697, 8524,
    29695, 26668, 19556, 22275, 22514, 11737, 16939, 24729, 25764, 26288, 19608 #last one isn't a keeper but was an outlier I wanted to remove
]

player_value_rankings_filtered = player_value_rankings[~player_value_rankings['IDfg'].isin(batter_keepers_2024)]

# Calculate draft value
player_value_rankings_filtered['player_draft_value'] = player_value_rankings_filtered['adjusted_total_value'] * 3.64


# Save the output DataFrame to a new CSV file
player_value_rankings_filtered.to_csv('player_values_final.csv', index=False)

# Define the destination table ID
destination_table_id = f"{project_id}.{dataset_name}.batter_player_value"

# Step 4: Write to BigQuery
player_value_rankings_filtered.to_gbq(
    destination_table_id,
    project_id=project_id,
    if_exists='replace',
    credentials=credentials
)
