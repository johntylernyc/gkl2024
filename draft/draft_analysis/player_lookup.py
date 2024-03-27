import pandas as pd
from pybaseball import playerid_lookup

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

# Load the CSV into a DataFrame
df = pd.read_csv('/Users/johntyler/github/gkl2024/draft/draft_analysis/parsed_players_data.csv')

# Add a new column for Player_ID, initialized as None
df['Player_ID'] = None

for index, row in df.iterrows():
    # Split the player's name to get the first and last name
    names = row['Player_Name'].split()
    first_name, last_name = names[0], ' '.join(names[1:])
    
    # Lookup the player ID
    player_id = safe_playerid_lookup(last_name, first_name)
    
    # Update the DataFrame with the player ID
    df.at[index, 'Player_ID'] = player_id

# Save the updated DataFrame to a new CSV file
df.to_csv('updated_players_data_with_ids.csv', index=False)

print("CSV updated with player IDs.")
