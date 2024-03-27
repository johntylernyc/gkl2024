from google.cloud import bigquery
from google.oauth2 import service_account
from helpers import json_key_path, dataset_name, project_id
import pandas as pd
import numpy as np

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)

# Define your dataset and table names
table_name = 'batter_player_consistency'

# SQL query to retrieve data and calculate league averages
query = f"""
SELECT
  *
FROM
  `{project_id}.{dataset_name}.{table_name}`
WHERE 
  avg_ab >= 175
"""

data = client.query(query).to_dataframe()

category_columns = ['avg_r', 'avg_h', 'avg_3b', 'avg_hr', 'avg_rbi', 'avg_sb']

# Function to calculate Z-scores
def calculate_z_scores(df, avg, std):
    return (df - avg) / std

# Step 1: Identify players who meet the criteria
criteria1 = (data['SeasonsPlayed'] == 1) & (data['LatestAge'] < 24) & (data['avg_ab'] > 200)
criteria2 = (data['SeasonsPlayed'] == 2) & (data['LatestAge'] < 27) & (data['avg_ab'] < 400) 

# Step 2: Normalize counting stats
for column in category_columns:
    data.loc[criteria1, column] = data.loc[criteria1, column] * (500 / data.loc[criteria1, 'avg_ab'])

# Step 2: Normalize counting stats
for column in category_columns:
    data.loc[criteria2, column] = data.loc[criteria2, column] * (500 / data.loc[criteria2, 'avg_ab'])    

averages = data[category_columns].mean()
std_devs = data[category_columns].std()
zscores = data[category_columns].apply(lambda x: calculate_z_scores(x, averages[x.name], std_devs[x.name]))

# print(zscores.describe())
# ratio_stats = ['hits_above_avg', 'obp_above_avg', 'slg_above_avg']
# print(data[ratio_stats].describe())

# Standard deviations from summary data
std_hits_above_avg = 27.54
std_obp_above_avg = 0.027
std_slg_above_avg = 0.048

# Average standard deviation of Z-scores for counting stats (approximately 1)
avg_std_counting_stats = 1

# Calculate scaling factors based on the ratio of standard deviations
scaling_factor_hits = avg_std_counting_stats / std_hits_above_avg
scaling_factor_obp = avg_std_counting_stats / std_obp_above_avg
scaling_factor_slg = avg_std_counting_stats / std_slg_above_avg

# Apply scaling factors to ratio stats
data['hits_above_avg_scaled'] = data['hits_above_avg'] * scaling_factor_hits
data['obp_above_avg_scaled'] = data['obp_above_avg'] * scaling_factor_obp
data['slg_above_avg_scaled'] = data['slg_above_avg'] * scaling_factor_slg

data['expected_value_counting'] = zscores.sum(axis=1)
data['expected_value_ratios'] = data[['hits_above_avg_scaled', 'obp_above_avg_scaled', 'slg_above_avg_scaled']].sum(axis=1)

data['expected_value'] = data['expected_value_counting']+data['expected_value_ratios'] 

# Find the 25th percentile player value
p25_value = data['expected_value'].quantile(0.35)

# Shift the values so that the 25th percentile is at 0
shift_value = abs(p25_value)
data['adjusted_expected_value'] = data['expected_value'] + shift_value

# Check the new range of expected values
print(f"New Min: {data['adjusted_expected_value'].min()}, New Max: {data['adjusted_expected_value'].max()}")

# ratio_stats_scaled = ['hits_above_avg_scaled', 'obp_above_avg_scaled', 'slg_above_avg_scaled']
# print(zscores.describe())
# print(data[ratio_stats_scaled].describe())

# print(data.head())
# print(data['expected_value'].describe())

def adjust_player_value(row):
    adjusted_value = row['adjusted_expected_value']
    
    # # Apply bonus for overall_consistency > 0.90
    # if row['overall_consistency'] > 0.90:
    #     adjusted_value *= 1.1
    
    # Apply bonus for LatestAge between 26 and 30
    if 26 <= row['LatestAge'] <= 30:
        adjusted_value *= 1.1
    
    # # Apply penalty for overall_consistency < 0.60
    # if row['overall_consistency'] < 0.60:
    #     adjusted_value *= 0.9
    
    # Apply penalty for LatestAge >= 34
    if row['LatestAge'] >= 34:
        adjusted_value *= 0.80
    
    return adjusted_value

# Apply the adjust_total_value function to each row
data['adjusted_expected_value'] = data.apply(adjust_player_value, axis=1)

# Calculate draft value
data['player_draft_value'] = data['adjusted_expected_value'] * 4.19

destination_table_id = f"{project_id}.{dataset_name}.batter_zscore_value"

# Step 4: Write to BigQuery
data.to_gbq(
    destination_table_id,
    project_id=project_id,
    if_exists='replace',
    credentials=credentials
)