import statsapi
from pybaseball import playerid_lookup
import pandas as pd

schedule = statsapi.schedule(sportId=1, start_date='04/11/2024', end_date='04/11/2024')

# # Function to safely get the first matching player ID
# def safe_playerid_lookup(last_name, first_name):
#     try:
#         lookup_df = playerid_lookup(last_name, first_name, fuzzy=True)
#         if not lookup_df.empty:
#             # Assuming the first row is the correct player
#             return lookup_df.iloc[0]['key_mlbam']
#     except Exception as e:
#         print(f"Lookup failed for {first_name} {last_name}: {e}")
#     return None

# For each game in schedule get the game_id and get the starting lineups for that game
for game in schedule:
    game_id = game['game_id']
    params = {
        "sportId": 1,
        "gamePk": game_id,
        "hydrate": "lineups",
    }
    gamedata = statsapi.get("schedule", params)
    
    print(gamedata)
    
    # handle cases where lineups have not been submitted and the 'lineups' key is not present
    # if 'lineups' in gamedata['dates'][0]['games'][0]:
    #     teamdata = gamedata['dates'][0]['games'][0]['lineups']
    # else:
    #     print(f"No lineups found for game {game_id}")

    # print(teamdata)

    # for team, players in teamdata.items():
    #     for i in range(len(players)):
    #         if 'fullName' in players[i]:
    #             full_name = players[i]['fullName']
    #             if full_name.count(' ') == 2:
    #                 full_name = ' '.join(full_name.split(' ')[:2])
    #         else: 
    #             print(f"No full name found for player {i} in team {team}. Player data: {players[i]}")
    #         # Use the playerid_lookup function to lookup the player's player_id
    #         first_name, last_name = full_name.split(' ')
    #         player_id = playerid_lookup(last_name, first_name, fuzzy=True)
    #         key_mlbam = player_id.iloc[0]['key_mlbam']
    #         teamdata[team][i] = {'name': full_name, 'player_id': key_mlbam}

   # Using 'teamdata' create a dataframe with the game_id, home or away, the team, player name, and player_id
    # This still needs testing / debugging / validation

    # df = pd.DataFrame(columns=['game_id', 'team', 'player_name', 'player_id'])
    # for team, players in teamdata.items():
    #     for i in range(len(players)):
    #         full_name = players[i]['fullName']
    #         player_id = players[i]['player_id']
    #         df = df.append({
    #             'game_id': game_id,
    #             'team': team,
    #             'player_name': full_name,
    #             'player_id': player_id
    #         }, ignore_index=True)
    # print(df)

# For each player name in the lineups dictionary, use pybaseball to lookup that player's player_id and add it to the dictionary

# Parse the first and last name from the player's full name for each player in the lineups dictionary
# Use the safe_playerid_lookup function to lookup the player's player_id
# Add the player_id to the dictionary
# Print the updated dictionary

# for team, players in lineups.items():
#     for i in range(len(players)):
#         full_name = players[i]
#         first_name, last_name = full_name.split(' ')
#         player_id = safe_playerid_lookup(last_name, first_name)
#         lineups[team][i] = {'name': full_name, 'player_id': player_id}

# print(lineups)

