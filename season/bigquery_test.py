
import pandas as pd
from pybaseball import batting_stats
import re

from google.cloud import bigquery
from google.oauth2 import service_account
from config_bigquery import dataset_name, json_key_path, project_id, batter_table_name

credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)
batter_table_id = f"{project_id}.{dataset_name}.{batter_table_name}"

# Create synthesized data
data = {
    'PlayerID': [1, 2, 3],
    'PlayerName': ['John Doe', 'Jane Smith', 'Mike Johnson'],
    'Team': ['Team A', 'Team B', 'Team C'],
    'HomeRuns': [25, 30, 22],
    'Average': [0.275, 0.320, 0.280]
}

# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Define the table schema explicitly
schema = [
    bigquery.SchemaField("PlayerID", "INTEGER"),
    bigquery.SchemaField("PlayerName", "STRING"),
    bigquery.SchemaField("Team", "STRING"),
    bigquery.SchemaField("HomeRuns", "INTEGER"),
    bigquery.SchemaField("Average", "FLOAT")
]

# Create a BigQuery job configuration
job_config = bigquery.LoadJobConfig(schema=schema)
# Overwrite any existing table
job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

# Upload the DataFrame to BigQuery
job = client.load_table_from_dataframe(df, batter_table_id, job_config=job_config)

# Wait for the load job to complete
job.result()

print(f"Uploaded synthesized data to {batter_table_id}")