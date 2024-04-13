import statsapi, re
from google.cloud import bigquery
from google.oauth2 import service_account
from pybaseball import playerid_lookup, playerid_reverse_lookup
from config_bigquery import json_key_path, project_id, dataset_name, table_name

schedule = statsapi.schedule(start_date='04/10/2024', end_date='04/11/2024')
json_key_path = json_key_path
project_id = project_id
dataset_name = dataset_name
table_name = table_name

# Create a BigQuery client using the service account key file
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(project=project_id, credentials=credentials)

# Define the schema of the table
schema = [
    bigquery.SchemaField('game_date', 'DATE'),
    bigquery.SchemaField('game_datetime', 'TIMESTAMP'),
    bigquery.SchemaField('away_team_id', 'INTEGER'),
    bigquery.SchemaField('away_team', 'STRING'),
    bigquery.SchemaField('home_team_id', 'INTEGER'),
    bigquery.SchemaField('home_team', 'STRING'),
    bigquery.SchemaField('away_pitcher_mlbam', 'INTEGER'),
    bigquery.SchemaField('away_pitcher', 'STRING'),
    bigquery.SchemaField('home_pitcher_mlbam', 'INTEGER'),
    bigquery.SchemaField('home_pitcher', 'STRING'),
    bigquery.SchemaField('venue', 'STRING'),
    bigquery.SchemaField('game_id', 'INTEGER'),
    bigquery.SchemaField('game_status', 'STRING')
]

# Create the table if it doesn't exist
table_ref = f"{project_id}.{dataset_name}.{table_name}"
table = bigquery.Table(table_ref, schema=schema)
table = client.create_table(table, exists_ok=True)

# Function to clean column names
def clean_column_name(column_name):
    # Replace special characters with underscore
    clean_name = re.sub(r'[%]', '_rate', column_name)
    # Replace special characters with underscore
    clean_name = re.sub(r'[()/]', '_', column_name)
    # Replace spaces with underscore
    clean_name = re.sub(r'\s+', '_', clean_name)
    # Remove trailing underscores
    clean_name = re.sub(r'_+$', '', clean_name)
    # Prefix with an underscore if the name starts with a number
    if re.match(r'^\d', clean_name):
        clean_name = '_' + clean_name
    return clean_name

# Function to safely get the first matching player ID
def safe_playerid_lookup(last_name, first_name):
    try:
        lookup_df = playerid_lookup(last_name, first_name, fuzzy=True)
        if not lookup_df.empty:
            # Assuming the first row is the correct player
            return lookup_df.iloc[0]['key_mlbam']
    except Exception as e:
        print(f"Lookup failed for {first_name} {last_name}: {e}")
    return None

# Retrieve and insert the data into the table
rows_to_insert = []
for game in schedule:
    game_date = game['game_date']
    game_datetime = game['game_datetime']
    away_team_id = game['away_id']
    away_team = game['away_name']
    home_team_id = game['home_id']
    home_team = game['home_name']
    away_pitcher = game['away_probable_pitcher']
    home_pitcher = game['home_probable_pitcher']
    venue = game['venue_name']
    game_id = game['game_id']
    game_status = game['status']

    print(f"Processing game {game_id} between {away_team} and {home_team} at {venue} on {game_date}.")

    # Lookup the player IDs for the away and home pitchers
    away_pitcher = away_pitcher.split(' ')
    away_pitcher_mlbam = safe_playerid_lookup(away_pitcher[1], away_pitcher[0])
    home_pitcher = home_pitcher.split(' ')
    home_pitcher_mlbam = safe_playerid_lookup(home_pitcher[1], home_pitcher[0])

    print(f"Home Pitcher: {home_pitcher[1]} {home_pitcher[0]} (FGID: {home_pitcher_mlbam})")
    print(f"Away Pitcher: {away_pitcher[1]} {away_pitcher[0]} (FGID: {away_pitcher_mlbam})")
    
    rows_to_insert.append((
        game_date, 
        game_datetime, 
        int(away_team_id), 
        away_team, 
        int(home_team_id), 
        home_team, 
        int(away_pitcher_mlbam), 
        ' '.join(away_pitcher), 
        int(home_pitcher_mlbam), 
        ' '.join(home_pitcher), 
        venue, 
        game_id, 
        game_status))
    
    print(rows_to_insert)

client.insert_rows(table, rows_to_insert)