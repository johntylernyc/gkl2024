import pandas as pd
from pybaseball import playerid_reverse_lookup

def create_player_ids_list(csv_file_path):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Extract the 'Player_ID' column as a list
    player_ids = df['Player_ID'].tolist()

    return player_ids

def lookup_fangraph_id(player_ids):
    #Lookup Fangraph IDs 
    lookup_output = playerid_reverse_lookup(player_ids,key_type='mlbam')

    return lookup_output

def add_fangraphs_id(csv_file_path, lookup_output):
    # Load the CSV file into a DataFrame
    df = pd.read_csv('/Users/johntyler/github/gkl2024/draft/draft_analysis/updated_players_data_with_ids.csv')

    # Assuming lookup_output is a list of dictionaries, convert it to a DataFrame
    # If lookup_output is already a DataFrame, this step can be skipped
    lookup_df = pd.DataFrame(lookup_output)

    # Merge the original DataFrame with the lookup DataFrame on the MLBAM key
    # This adds the Fangraphs ID ('key_fangraphs') to your original DataFrame
    merged_df = pd.merge(df, lookup_df[['key_mlbam', 'key_fangraphs']], left_on='Player_ID', right_on='key_mlbam', how='left')

    # Rename 'key_fangraphs' column to 'IDfg' and drop the 'key_mlbam' column as it's redundant
    merged_df.rename(columns={'key_fangraphs': 'IDfg'}, inplace=True)
    merged_df.drop(columns=['key_mlbam'], inplace=True)

    # Save the updated DataFrame to the same CSV or a new CSV file
    merged_df.to_csv('/Users/johntyler/github/gkl2024/draft/draft_analysis/updated_players_data_with_fangraph_ids.csv', index=False)

    print("CSV updated with Fangraphs IDs.")


if __name__ == "__main__":
    # Specify the path to your CSV file
    csv_file_path = '/Users/johntyler/github/gkl2024/draft/draft_analysis/updated_players_data_with_ids.csv'
    
    # Create the list of player IDs
    player_ids = create_player_ids_list(csv_file_path)
    lookup_output = lookup_fangraph_id(player_ids)
    add_fangraphs_id(csv_file_path, lookup_output)