import pandas as pd
from pybaseball import playerid_lookup



# Load the CSV file into a pandas DataFrame
df = pd.read_csv('y_players_2024.csv')

# Prepare a DataFrame to store the final output
output_df = pd.DataFrame(columns=['full_name', 'eligible_positions', 'IDfg'])

# List to store names that resulted in an error during the lookup
lookup_errors = []

# Iterate over the rows in the DataFrame
for index, row in df.iterrows():
    full_name = row['full_name']
    display_position = row['display_position']  # Assuming this is the eligible positions

    # Split the full name into first and last name for the lookup
    split_name = full_name.split()
    first_name, last_name = split_name[0], " ".join(split_name[1:])

    # Look up the player ID
    try:
        lookup_result = playerid_lookup(last_name, first_name, fuzzy=True)
        # Select the first result from the fuzzy match
        if not lookup_result.empty:
            player_id = lookup_result.iloc[0]['key_fangraphs']
            # Append the data to the output DataFrame
            output_df = output_df.append({
                'full_name': full_name,
                'eligible_positions': display_position,
                'IDfg': player_id
            }, ignore_index=True)
        else:
            # If the lookup_result is empty, add to errors
            lookup_errors.append(full_name)
    except Exception as e:
        lookup_errors.append(full_name)

# Save the output DataFrame to a new CSV file
output_df.to_csv('players_with_ids_2024.csv', index=False)

# Check if there were any lookup errors and print the list
if lookup_errors:
    print("Names that resulted in lookup errors:", lookup_errors)
