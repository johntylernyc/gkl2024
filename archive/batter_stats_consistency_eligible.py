from google.cloud import bigquery
from google.oauth2 import service_account
from helpers.config_bigquery import json_key_path
from google.cloud.bigquery import SchemaField
import json

# Setup BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Define your dataset and table names
dataset_name = 'gkl2024'
first_table_name = 'yahoo_player_data'  # Table with fantasy league data
second_table_name = 'batter_stats_consistency'  # Table with player statistical data

# SQL query to perform the JOIN operation and fetch the required data
query = f"""
SELECT 
    s.*,  -- Select all columns from the second table
    f.eligible_positions  
FROM 
    `{credentials.project_id}.{dataset_name}.{second_table_name}` s
JOIN 
    `{credentials.project_id}.{dataset_name}.{first_table_name}` f
ON 
    lower(s.name) = lower(f.full_name)
"""

# Run the query
query_job = client.query(query)

# Fetch the result into a DataFrame
df = query_job.to_dataframe()

# Convert array columns to JSON strings
df['eligible_positions'] = df['eligible_positions'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)

# Manually define the schema
schema = [
    SchemaField("IDfg", "INT64", mode="NULLABLE"),
    SchemaField("Name", "STRING", mode="NULLABLE"),
    SchemaField("avg_ab", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_r", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_h", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_3b", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_hr", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_rbi", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_sb", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_avg", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_obp", "FLOAT64", mode="NULLABLE"),
    SchemaField("avg_slg", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_AB", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_R", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_H", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_3B", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_HR", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_RBI", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_SB", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_AVG", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_OBP", "FLOAT64", mode="NULLABLE"),
    SchemaField("stddev_SLG", "FLOAT64", mode="NULLABLE"),
    SchemaField("SeasonsPlayed", "INT64", mode="NULLABLE"),
    SchemaField("LatestAge", "INT64", mode="NULLABLE"),
    SchemaField("consistency_AB", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_R", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_H", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_3B", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_HR", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_RBI", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_SB", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_AVG", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_OBP", "FLOAT64", mode="NULLABLE"),
    SchemaField("consistency_SLG", "FLOAT64", mode="NULLABLE"),
    SchemaField("overall_consistency", "FLOAT64", mode="NULLABLE"),
    SchemaField("overall_consistency_cat", "STRING", mode="NULLABLE"),
    # Adding the new eligible_positions column, assuming it's stored as a JSON string
    SchemaField("eligible_positions", "STRING", mode="NULLABLE")
]

# Creating a new table with the merged data
merged_table_name = 'player_stats_consistency_eligibility'
merged_table_id = f"{credentials.project_id}.{dataset_name}.{merged_table_name}"

# Save the DataFrame to the new BigQuery table
df.to_gbq(merged_table_id, credentials=credentials, if_exists='replace')
