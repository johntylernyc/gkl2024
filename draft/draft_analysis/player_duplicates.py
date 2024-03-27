import pandas as pd

def find_duplicate_players(csv_file_path):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Find duplicate player names
    duplicate_players = df[df.duplicated('Player_Name', keep=False)]['Player_Name'].unique()

    return duplicate_players

if __name__ == "__main__":
    # Specify the path to your CSV file
    csv_file_path = '/Users/johntyler/github/gkl2024/draft/draft_analysis/updated_players_data_with_ids.csv'  # Update this to your CSV file path

    # Find duplicate player names
    duplicate_players = find_duplicate_players(csv_file_path)

    # Print duplicate player names
    if len(duplicate_players) > 0:
        print("Duplicate player names found:")
        for player in duplicate_players:
            print(player)
    else:
        print("No duplicate player names found.")

