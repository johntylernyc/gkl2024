from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
from helpers.config_bigquery import dataset_name, json_key_path, project_id

# Authenticate and create a BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Construct a BigQuery SQL query
query = """
SELECT IDfg, Name, avg_ab, avg_r, avg_h, avg_3b, avg_hr, avg_rbi, avg_sb, avg_avg, hits_above_avg, avg_obp, obp_above_avg, avg_slg, slg_above_avg
    , total_hits, total_at_bats, total_walks, total_hbp, total_sf, total_pa, total_2b, total_3b, total_hr
    , stddev_AB, stddev_R, stddev_H, stddev_3B, stddev_HR, stddev_RBI, stddev_SB, stddev_AVG
    , stddev_OBP, stddev_SLG, SeasonsPlayed, LatestAge, eligible_positions
FROM `python-sandbox-381204.gkl2024.batter_adjusted_stats`
"""

# Run the query and save the results to a pandas DataFrame
df = client.query(query).to_dataframe()

# Function to calculate the consistency score
def calculate_consistency_score(mean, std_dev):
    if mean == 0:
        return 1 if std_dev == 0 else 0
    else:
        cv = std_dev / mean
        score = 1 / (1 + cv)
        return score

print(df.head())

# Calculate consistency scores for each stat
stats = ['AB', 'R', 'H', '3B', 'HR', 'RBI', 'SB', 'AVG', 'OBP', 'SLG']  # List of stat categories

for stat in stats:
    mean_column = f'avg_{stat.lower()}'  # Assuming mean columns are named like 'avg_r', 'avg_h', etc.
    std_dev_column = f'stddev_{stat}'  # Assuming std dev columns are named like 'stddev_R', 'stddev_H', etc.
    consistency_column = f'consistency_{stat}'  # Name for the new consistency score column
    
    # Apply the consistency score calculation
    df[consistency_column] = df.apply(lambda row: calculate_consistency_score(row[mean_column], row[std_dev_column]) if row['SeasonsPlayed'] > 1 else np.nan, axis=1)

# Calculate the overall consistency score by averaging the individual consistency scores
df['overall_consistency'] = df[[f'consistency_{stat}' for stat in stats]].mean(axis=1, skipna=True)

# Calculate the median overall consistency score among players with more than one season
median_consistency = df.loc[df['SeasonsPlayed'] > 1, 'overall_consistency'].median()

# Fill NaN overall consistency scores with the median value
df['overall_consistency'].fillna(median_consistency, inplace=True)

# Initialize 'overall_consistency_cat' column to handle NaN values properly
df['overall_consistency_cat'] = np.nan

# Label players aged 26 or younger with only one season played as "Prospect"
df.loc[(df['LatestAge'] <= 27) & (df['SeasonsPlayed'] == 1), 'overall_consistency_cat'] = 'Prospect'

# Filter the DataFrame for rows where 'overall_consistency_cat' is still NaN
df_filtered = df[df['overall_consistency_cat'].isna()]

# Define conditions and choices for the consistency categories on the filtered DataFrame
conditions = [
    df_filtered['overall_consistency'] >= 0.90,
    (df_filtered['overall_consistency'] >= 0.82) & (df_filtered['overall_consistency'] < 0.90),
    (df_filtered['overall_consistency'] >= 0.78) & (df_filtered['overall_consistency'] < 0.82),
    (df_filtered['overall_consistency'] >= 0.70) & (df_filtered['overall_consistency'] < 0.78),
    df_filtered['overall_consistency'] < 0.70
]

choices = [
    "Guarantee",
    "Highly Consistent",
    "Average Consistent",
    "Less Consistent",
    "Who Knows"
]

# Filter for rows where 'overall_consistency_cat' is still NaN and apply the conditions
df.loc[df['overall_consistency_cat'].isna(), 'overall_consistency_cat'] = np.select(conditions, choices, default='Unknown')

# Write the consistency table to BigQuery
batter_stats_consistency = f"{project_id}.{dataset_name}.batter_player_consistency"
df.to_gbq(batter_stats_consistency, project_id=project_id, if_exists='append', credentials=credentials)