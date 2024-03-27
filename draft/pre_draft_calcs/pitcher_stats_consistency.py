from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import numpy as np
from helpers.config_bigquery import dataset_name, json_key_path, project_id

# Authenticate and create a BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Construct a BigQuery SQL query to select pitcher stats
query = f"""
SELECT IDfg, Name, avg_ip, avg_app, avg_w, avg_sv, avg_k, avg_hld, avg_qs, earned_runs_below_avg, walks_hits_below_avg, k_bb_ratio_adjustment, 
    avg_era, avg_whip, avg_k_bb, total_ip, total_app, total_w, total_sv, total_k, total_hld, total_h, total_er, total_bb,
    stddev_ip, stddev_app, stddev_w, stddev_sv, stddev_k, stddev_hld, stddev_qs, stddev_era, stddev_whip, stddev_k_bb,
    SeasonsPlayed, LatestAge, eligible_positions
FROM `{project_id}.{dataset_name}.pitcher_adjusted_stats`
"""

# Run the query and save the results to a pandas DataFrame
df = client.query(query).to_dataframe()

# Function to calculate the consistency score
def calculate_consistency_score(mean, std_dev):
    if mean == 0:
        return 1 if std_dev == 0 else 0
    else:
        cv = std_dev / mean  # Coefficient of Variation
        score = 1 / (1 + cv)  # Inverse to give higher score for lower variation
        return score

# List of pitching stats for which to calculate consistency scores
stats = ['ip', 'app', 'w', 'sv', 'k', 'hld', 'qs', 'era', 'whip', 'k_bb']

# Calculate consistency scores for each stat
for stat in stats:
    mean_column = f'avg_{stat}'  # Column names for average stats
    std_dev_column = f'stddev_{stat}'  # Column names for standard deviation stats
    consistency_column = f'consistency_{stat}'  # New column names for consistency scores
    
    # Apply the consistency score calculation
    df[consistency_column] = df.apply(lambda row: calculate_consistency_score(row[mean_column], row[std_dev_column]) if row['SeasonsPlayed'] > 1 else np.nan, axis=1)

# Calculate the overall consistency score by averaging the individual consistency scores
df['overall_consistency'] = df[[f'consistency_{stat}' for stat in stats]].mean(axis=1, skipna=True)

# Calculate the median overall consistency score among players with more than one season
median_consistency = df.loc[df['SeasonsPlayed'] > 1, 'overall_consistency'].median()

# Fill NaN overall consistency scores with the median value
df['overall_consistency'].fillna(median_consistency, inplace=True)

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

# Write the DataFrame to BigQuery
pitcher_stats_consistency_table_id = f"{project_id}.{dataset_name}.pitcher_player_consistency"
df.to_gbq(pitcher_stats_consistency_table_id, project_id=project_id, if_exists='replace', credentials=credentials)

print(f"Data written to {pitcher_stats_consistency_table_id}")
