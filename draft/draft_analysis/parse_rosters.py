import pandas as pd
import re

# Predefined list of team names
team_names = [
    "Big Daddy's Funk", "Boys of Summer", "Frank in the House", "Holy Toledo!", "IWU Tang Clan",
    "Kirby Puckett", "Mary's Little Lambs", "My Name is My Name", "O'Hoppe Day", "PJ Shuffle",
    "Spare Parts Too", "Springfield Isotopes", "Steel City Sluggers", "Tenacious D", "The Revs.",
    "The ShapeShifters", "What Can Braun Do 4U", "Yellow&Black Attack"
]

# Normalize team names for pattern matching (remove apostrophes, convert to lowercase)
normalized_team_names = [re.sub(r"[\W_]+", '', team).lower() for team in team_names]

# Function to parse the .txt file
def parse_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Pattern to identify player details
    player_pattern = re.compile(r'^\d+\.\s+\(\d+\)\s+(.*?)\s+\((.+?) - (.+?)\)\s+\$(\d+)$')

    data = []
    current_team = ''

    for line in lines:
        line = line.strip()
        normalized_line = re.sub(r"[\W_]+", '', line).lower()  # Normalize the line for matching

        # Check if the normalized line matches any normalized team name
        for team, normalized_team in zip(team_names, normalized_team_names):
            if normalized_team in normalized_line:
                current_team = team  # Update the current team name
                break
        
        if player_pattern.match(line):
            player_info = player_pattern.match(line)
            player_name = player_info.group(1)
            position = player_info.group(3)
            cost = f"${player_info.group(4)}"
            data.append((current_team, player_name, position, cost))

    return data

# Path to your .txt file
file_path = '/Users/johntyler/github/gkl2024/draft/draft_analysis/fantasy_baseball.txt'  # Update this to the path of your .txt file

# Parse the file
parsed_data = parse_file(file_path)

# Convert the list of tuples into a pandas DataFrame
df = pd.DataFrame(parsed_data, columns=['Team_Name', 'Player_Name', 'eligible_positions', 'Cost'])

# Save the DataFrame to a CSV file
df.to_csv('parsed_players_data.csv', index=False)

print("Data parsed and saved to CSV successfully.")
