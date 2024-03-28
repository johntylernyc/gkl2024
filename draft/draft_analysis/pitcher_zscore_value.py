from google.cloud import bigquery
from google.oauth2 import service_account
from helpers import json_key_path, dataset_name, project_id
import pandas as pd
import numpy as np

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)

# Define your dataset and table names
table_name = 'pitcher_player_consistency'

# SQL query to retrieve data and calculate league averages
query = f"""
SELECT
  *
FROM
  `{project_id}.{dataset_name}.{table_name}`
WHERE 
  avg_ip >= 50
"""

data = client.query(query).to_dataframe()

category_columns = ['avg_app', 'avg_w', 'avg_sv', 'avg_k', 'avg_hld', 'avg_qs']

# Function to calculate Z-scores
def calculate_z_scores(df, avg, std):
    return (df - avg) / std

# Step 1: Identify players who meet the criteria
criteria1 = (data['SeasonsPlayed'] == 1) & (data['LatestAge'] < 27) & (data['avg_ip'] > 30) & (data['eligible_positions'] == 'RP')
criteria2 = (data['SeasonsPlayed'] == 2) & (data['LatestAge'] < 27) & (data['avg_ip'] < 60) & (data['eligible_positions'] == 'RP')
criteria3 = (data['SeasonsPlayed'] == 1) & (data['LatestAge'] < 27) & (data['avg_ip'] > 30) & (data['eligible_positions'] == 'SP')
criteria4 = (data['SeasonsPlayed'] == 2) & (data['LatestAge'] < 27) & (data['avg_ip'] < 60) & (data['eligible_positions'] == 'SP')
criteria5 = (data['SeasonsPlayed'] == 1) & (data['LatestAge'] < 27) & (data['avg_ip'] > 30) & (data['eligible_positions'] == 'SP,RP')
criteria6 = (data['SeasonsPlayed'] == 2) & (data['LatestAge'] < 27) & (data['avg_ip'] < 60) & (data['eligible_positions'] == 'SP,RP')

# Step 2: Normalize counting stats RP
for column in category_columns:
    data.loc[criteria1, column] = data.loc[criteria1, column] * (80 / data.loc[criteria1, 'avg_ip'])
for column in category_columns:
    data.loc[criteria2, column] = data.loc[criteria2, column] * (80 / data.loc[criteria2, 'avg_ip'])
for column in category_columns:
    data.loc[criteria5, column] = data.loc[criteria5, column] * (80 / data.loc[criteria2, 'avg_ip'])    
for column in category_columns:
    data.loc[criteria6, column] = data.loc[criteria6, column] * (80 / data.loc[criteria2, 'avg_ip'])

# Step 2: Normalize counting stats SP
for column in category_columns:
    data.loc[criteria3, column] = data.loc[criteria3, column] * (140 / data.loc[criteria1, 'avg_ip'])
for column in category_columns:
    data.loc[criteria4, column] = data.loc[criteria4, column] * (140 / data.loc[criteria2, 'avg_ip'])

averages = data[category_columns].mean()
std_devs = data[category_columns].std()
zscores = data[category_columns].apply(lambda x: calculate_z_scores(x, averages[x.name], std_devs[x.name]))

# print(zscores.describe())
# ratio_stats = ['walks_hits_below_avg', 'earned_runs_below_avg', 'k_bb_ratio_adjustment']
# print(data[ratio_stats].describe())

# Standard deviations from summary data
std_walks_hits_below_avg = 35.90
std_earned_runs_below_avg = 22.11
std_k_bb_ratio_adjustment = 1.29

# Average standard deviation of Z-scores for counting stats (approximately 1)
avg_std_counting_stats = 1

# Calculate scaling factors based on the ratio of standard deviations
scaling_factor_hits = avg_std_counting_stats / std_walks_hits_below_avg
scaling_factor_era = avg_std_counting_stats / std_earned_runs_below_avg
scaling_factor_k_bb = avg_std_counting_stats / std_k_bb_ratio_adjustment

# Apply scaling factors to ratio stats
data['walks_hits_below_avg_scaled'] = data['walks_hits_below_avg'] * scaling_factor_hits
data['earned_runs_below_avg_scaled'] = data['earned_runs_below_avg'] * scaling_factor_era
data['k_bb_ratio_adjustment_scaled'] = data['k_bb_ratio_adjustment'] * scaling_factor_k_bb

data['expected_value_counting'] = zscores.sum(axis=1)
data['expected_value_ratios'] = data[['walks_hits_below_avg_scaled', 'earned_runs_below_avg_scaled', 'k_bb_ratio_adjustment_scaled']].sum(axis=1)

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

# Calculate draft value
data['player_draft_value'] = data['adjusted_expected_value'] * 4.19

def enforce_negative_value_floor(row, floor_value=-10):
    # Check if the adjusted value is less than the floor value
    if row['player_draft_value'] < floor_value:
        # If it is, set it to the floor value
        return floor_value
    else:
        # Otherwise, keep the original value
        return row['player_draft_value']

# Apply the enforce_negative_value_floor function to each row
data['player_draft_value'] = data.apply(enforce_negative_value_floor, axis=1)

destination_table_id = f"{project_id}.{dataset_name}.pitcher_zscore_value"

# Step 4: Write to BigQuery
data.to_gbq(
    destination_table_id,
    project_id=project_id,
    if_exists='replace',
    credentials=credentials
)