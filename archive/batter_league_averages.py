from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.config_bigquery import json_key_path, dataset_name, project_id, dataset_name
import json
import numpy as np
import pandas as pd

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Define your dataset and table names
table_name = 'batter_player_consistency_eligibility'

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
  -- League average batting average (AVG), OBP, and SLG
  SUM(total_hits) / SUM(total_at_bats) AS league_avg_avg,
  (SUM(total_hits) + SUM(total_walks) + SUM(total_hbp)) / (SUM(total_at_bats) + SUM(total_walks) + SUM(total_hbp) + SUM(total_sf)) AS league_avg_obp,
  (SUM(total_hits) - SUM(total_2b) - SUM(total_3b) - SUM(total_hr) + (2 * SUM(total_2b)) + (3 * SUM(total_3b)) + (4 * SUM(total_hr))) / SUM(total_at_bats) AS league_avg_slg,
  -- Standard deviations for adjusted rate stats
  AVG(hits_above_avg) as avg_hits_above_avg, STDDEV(hits_above_avg) AS stddev_hits_above_avg,
  AVG(obp_above_avg) as avg_obp_above_avg, STDDEV(obp_above_avg) AS stddev_obp_above_avg,
  AVG(slg_above_avg) as avg_slg_above_avg, STDDEV(slg_above_avg) AS stddev_slg_above_avg
FROM
  `{project_id}.{dataset_name}.{table_name}`
WHERE 
  avg_ab >= 300
"""

# Run the query
league_averages = client.query(query).to_dataframe()

# Display the league averages
print(league_averages)

query2 = f"""
  SELECT * 
  FROM
    `{project_id}.{dataset_name}.{table_name}`
"""

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

# Display the rankings
print(player_value_rankings[['Name', 'total_value']])

print(player_value_rankings.dtypes)

# Convert the column to a JSON string if it contains array-like data
if 'eligible_positions_filtered' in player_value_rankings.columns:
    player_value_rankings['eligible_positions_filtered'] = player_value_rankings['eligible_positions_filtered'].apply(
        lambda x: json.dumps(x.tolist()) if isinstance(x, np.ndarray) else json.dumps(x) if isinstance(x, list) else x
    )

# Step 1: Identify Unique Positions
# Convert JSON strings in 'eligible_positions_filtered' to lists
player_value_rankings['eligible_positions_filtered'] = player_value_rankings['eligible_positions_filtered'].apply(json.loads)

# Get a set of all unique positions
all_positions = set()
player_value_rankings['eligible_positions_filtered'].apply(lambda positions: all_positions.update(positions))

# Step 2: Rank Players for Each Position
# Initialize columns for position ranks
for position in all_positions:
    player_value_rankings[f'{position.lower()}_rank'] = None

for index, row in player_value_rankings.iterrows():
    for position in row['eligible_positions_filtered']:
        # Filter players eligible for the current position
        eligible_players = player_value_rankings[player_value_rankings['eligible_positions_filtered'].apply(lambda positions: position in positions)]
        # Sort eligible players by total_value and get the rank
        ranked_players = eligible_players.sort_values(by='total_value', ascending=False).reset_index()
        rank = ranked_players.index[ranked_players['IDfg'] == row['IDfg']].tolist()[0] + 1  # Find the rank of the current player
        # Assign rank to the respective position column
        player_value_rankings.at[index, f'{position.lower()}_rank'] = rank

# Display the DataFrame with the new position rank columns
print(player_value_rankings.dtypes)

# Step 1: Convert Rank Columns to Integers
rank_columns = ['ss_rank', 'util_rank', '3b_rank', 'lf_rank', 'sp_rank', 'rp_rank', 'il_rank', 'p_rank', 'c_rank', '2b_rank', 'cf_rank', 'rf_rank', '1b_rank']
for column in rank_columns:
    if column in player_value_rankings.columns:
        player_value_rankings[column] = pd.to_numeric(player_value_rankings[column], errors='coerce').fillna(0).astype(int)

# Step 2: Handle eligible_positions_filtered
player_value_rankings['eligible_positions_filtered'] = player_value_rankings['eligible_positions_filtered'].apply(
    lambda x: json.dumps(x) if isinstance(x, list) else x
)

# Step 3: Define the Schema
# Step 3: Define the Schema
# Define the Schema as a list of dictionaries
schema = [
    {"name": "IDfg", "type": "INTEGER"},
    {"name": "Name", "type": "STRING"},
    {"name": "avg_ab", "type": "FLOAT"},
    {"name": "avg_r", "type": "FLOAT"},
    {"name": "avg_h", "type": "FLOAT"},
    {"name": "avg_3b", "type": "FLOAT"},
    {"name": "avg_hr", "type": "FLOAT"},
    {"name": "avg_rbi", "type": "FLOAT"},
    {"name": "avg_sb", "type": "FLOAT"},
    {"name": "avg_avg", "type": "FLOAT"},
    {"name": "hits_above_avg", "type": "FLOAT"},
    {"name": "avg_obp", "type": "FLOAT"},
    {"name": "obp_above_avg", "type": "FLOAT"},
    {"name": "avg_slg", "type": "FLOAT"},
    {"name": "slg_above_avg", "type": "FLOAT"},
    {"name": "total_hits", "type": "INTEGER"},
    {"name": "total_at_bats", "type": "INTEGER"},
    {"name": "total_walks", "type": "INTEGER"},
    {"name": "total_hbp", "type": "INTEGER"},
    {"name": "total_sf", "type": "INTEGER"},
    {"name": "total_pa", "type": "INTEGER"},
    {"name": "total_2b", "type": "INTEGER"},
    {"name": "total_3b", "type": "INTEGER"},
    {"name": "total_hr", "type": "INTEGER"},
    {"name": "stddev_AB", "type": "FLOAT"},
    {"name": "stddev_R", "type": "FLOAT"},
    {"name": "stddev_H", "type": "FLOAT"},
    {"name": "stddev_3B", "type": "FLOAT"},
    {"name": "stddev_HR", "type": "FLOAT"},
    {"name": "stddev_RBI", "type": "FLOAT"},
    {"name": "stddev_SB", "type": "FLOAT"},
    {"name": "stddev_AVG", "type": "FLOAT"},
    {"name": "stddev_OBP", "type": "FLOAT"},
    {"name": "stddev_SLG", "type": "FLOAT"},
    {"name": "SeasonsPlayed", "type": "INTEGER"},
    {"name": "LatestAge", "type": "INTEGER"},
    {"name": "eligible_positions_filtered", "type": "STRING"},
    {"name": "value_r", "type": "FLOAT"},
    {"name": "value_h", "type": "FLOAT"},
    {"name": "value_3b", "type": "FLOAT"},
    {"name": "value_hr", "type": "FLOAT"},
    {"name": "value_rbi", "type": "FLOAT"},
    {"name": "value_sb", "type": "FLOAT"},
    {"name": "value_hits_above_avg", "type": "FLOAT"},
    {"name": "value_obp_above_avg", "type": "FLOAT"},
    {"name": "value_slg_above_avg", "type": "FLOAT"},
    {"name": "total_value", "type": "FLOAT"},
    # Define the rank columns as INTEGER type
    {"name": "ss_rank", "type": "INTEGER"},
    {"name": "util_rank", "type": "INTEGER"},
    {"name": "3b_rank", "type": "INTEGER"},
    {"name": "lf_rank", "type": "INTEGER"},
    {"name": "sp_rank", "type": "INTEGER"},
    {"name": "rp_rank", "type": "INTEGER"},
    {"name": "il_rank", "type": "INTEGER"},
    {"name": "p_rank", "type": "INTEGER"},
    {"name": "c_rank", "type": "INTEGER"},
    {"name": "2b_rank", "type": "INTEGER"},
    {"name": "cf_rank", "type": "INTEGER"},
    {"name": "rf_rank", "type": "INTEGER"},
    {"name": "1b_rank", "type": "INTEGER"}
]

# Define the destination table ID
destination_table_id = f"{project_id}.{dataset_name}.batter_player_value"

# Step 4: Write to BigQuery
player_value_rankings.to_gbq(
    destination_table_id,
    project_id=project_id,
    if_exists='replace',
    credentials=credentials,
    table_schema=schema  # Use the defined schema
)

# End of Script