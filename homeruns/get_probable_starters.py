import statsapi, re
from google.cloud import bigquery
from google.oauth2 import service_account
from pybaseball import playerid_lookup
from config_bigquery import json_key_path, project_id, dataset_name, get_todays_games_table as table_name
from park_factors import fetch_park_factors

schedule = statsapi.schedule(start_date='04/12/2024', end_date='04/12/2024')
json_key_path = json_key_path
project_id = project_id
dataset_name = dataset_name
table_name = table_name
park_factors = fetch_park_factors()

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
    bigquery.SchemaField('hr_index', 'STRING'),
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

    if away_pitcher:
        away_pitcher_parts = away_pitcher.split(' ')
        if len(away_pitcher_parts) >= 2:
            away_pitcher_mlbam = safe_playerid_lookup(away_pitcher_parts[1], away_pitcher_parts[0])
        else:
            away_pitcher_mlbam = None
    else:
        away_pitcher_mlbam = None

    if home_pitcher:
        home_pitcher_parts = home_pitcher.split(' ')
        if len(home_pitcher_parts) >= 2:
            home_pitcher_mlbam = safe_playerid_lookup(home_pitcher_parts[1], home_pitcher_parts[0])
        else:
            home_pitcher_mlbam = None
    else:
        home_pitcher_mlbam = None

    print(f"Home Pitcher: {' '.join(home_pitcher_parts) if home_pitcher else 'Unknown'} (MLBAM ID: {home_pitcher_mlbam})")
    print(f"Away Pitcher: {' '.join(away_pitcher_parts) if away_pitcher else 'Unknown'} (MLBAM ID: {away_pitcher_mlbam})")

# Retrieve park factors for the venue
    venue = game['venue_name']
    game_id = game['game_id']
    
    # Retrieve HR Index from park factors
    hr_index = park_factors.get(venue, "Unknown")  # Default to "Unknown" if venue is not found

    print(f"HR Index for {venue}: {hr_index}")

    # Append a tuple with game information and HR index
    rows_to_insert.append((
        game_date, 
        game_datetime, 
        int(away_team_id), 
        away_team, 
        int(home_team_id), 
        home_team, 
        int(away_pitcher_mlbam) if away_pitcher_mlbam else None, 
        ' '.join(away_pitcher_parts) if away_pitcher else 'Unknown', 
        int(home_pitcher_mlbam) if home_pitcher_mlbam else None, 
        ' '.join(home_pitcher_parts) if home_pitcher else 'Unknown', 
        venue,
        hr_index, 
        game_id, 
        game_status
    ))

client.insert_rows(table, rows_to_insert)