from google.cloud import bigquery
from google.oauth2 import service_account
import json
from helpers.config_bigquery import json_key_path

# Initialize a BigQuery client
credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Set your dataset and table
dataset_name = 'gkl2024'
table_name = 'yahoo_player_data'
table_id = f'{client.project}.{dataset_name}.{table_name}'

# Define your table schema
schema = [
    bigquery.SchemaField("player_key", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("player_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("full_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("first_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("last_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("editorial_player_key", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("editorial_team_key", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("editorial_team_full_name", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("editorial_team_abbr", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("display_position", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("uniform_number", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("image_url", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("position_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("primary_position", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("eligible_positions", "STRING", mode="REPEATED"),
    bigquery.SchemaField("eligible_positions_to_add", "STRING", mode="REPEATED"),
    bigquery.SchemaField("has_player_notes", "BOOLEAN", mode="NULLABLE"),
    bigquery.SchemaField("player_notes_last_timestamp", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("projected_auction_value", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("average_auction_cost", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("player_ranks", "RECORD", mode="REPEATED", fields=[
        bigquery.SchemaField("rank_type", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("rank_value", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("rank_season", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("rank_position", "STRING", mode="NULLABLE"),
    ]),
    bigquery.SchemaField("draft_analysis", "RECORD", mode="NULLABLE", fields=[
        bigquery.SchemaField("average_pick", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("average_round", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("average_cost", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("percent_drafted", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("preseason_average_pick", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("preseason_average_round", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("preseason_average_cost", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("preseason_percent_drafted", "STRING", mode="NULLABLE"),
    ]),
]

# Create a table in BigQuery
table = bigquery.Table(table_id, schema=schema)
table = client.create_table(table, exists_ok=True)  # Make an API request.
print(f"Table {table.project}.{table.dataset_id}.{table.table_id} created.")

# Load the JSON data
with open('yahoo_player_data.json') as f:
    data = json.load(f)

# Prepare the data for BigQuery
rows_to_insert = []
for player_info in data['players']:
    player = player_info['player']
    eligible_positions = [pos['position'] for pos in player.get('eligible_positions', [])]
    eligible_positions_to_add = [pos['position'] for pos in player.get('eligible_positions_to_add', [])]
    
    # Process player ranks, skipping any entry with '2024' as the rank_season
    player_ranks = []
    for rank in player.get('player_ranks', []):
        if rank['player_rank']['rank_season'] != '2024':
            player_ranks.append({
                'rank_type': rank['player_rank']['rank_type'],
                'rank_value': rank['player_rank']['rank_value'],
                'rank_season': rank['player_rank']['rank_season'],
                'rank_position': rank['player_rank'].get('rank_position')
            })

    # If player_ranks is empty after filtering, skip this player
    if not player_ranks:
        continue

    draft_analysis = player.get('draft_analysis', {})
    row = {
        'player_key': player.get('player_key'),
        'player_id': player.get('player_id'),
        'full_name': player['name'].get('full'),
        'first_name': player['name'].get('first'),
        'last_name': player['name'].get('last'),
        'url': player.get('url'),
        'editorial_player_key': player.get('editorial_player_key'),
        'editorial_team_key': player.get('editorial_team_key'),
        'editorial_team_full_name': player.get('editorial_team_full_name'),
        'editorial_team_abbr': player.get('editorial_team_abbr'),
        'display_position': player.get('display_position'),
        'uniform_number': player.get('uniform_number'),
        'image_url': player.get('image_url'),
        'position_type': player.get('position_type'),
        'primary_position': player.get('primary_position'),
        'eligible_positions': eligible_positions,
        'eligible_positions_to_add': eligible_positions_to_add,
        'has_player_notes': player.get('has_player_notes') == 1,
        'player_notes_last_timestamp': player.get('player_notes_last_timestamp'),
        'projected_auction_value': player.get('projected_auction_value'),
        'average_auction_cost': player.get('average_auction_cost'),
        'player_ranks': player_ranks,
        'draft_analysis': draft_analysis,
    }
    rows_to_insert.append(row)

# Insert the data into the BigQuery table
errors = client.insert_rows_json(table_id, rows_to_insert)  # Make an API request.
if errors == []:
    print("New rows have been added.")
else:
    print("Encountered errors while inserting rows: {}".format(errors))
