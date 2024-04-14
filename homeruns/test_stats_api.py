from pybaseball import playerid_lookup, statcast_pitcher
import matplotlib.pyplot as plt

# lookup player ID '680869'
# player = playerid_reverse_lookup([663978])
# print(player)

# player = playerid_lookup('Taylor', 'Michael')
# print(player)

player = playerid_lookup('Carrasco', 'Carlos')
pitcher = statcast_pitcher(start_dt = '2015-03-01', end_dt = '2024-04-12', player_id=471911)

# Define the date range and pitcher ID
start_date = '2023-04-01'
end_date = '2024-04-12'
pitcher_id = 471911  # Replace with the actual pitcher's MLBAM ID

# Fetch the data
data = statcast_pitcher(start_dt=start_date, end_dt=end_date, player_id=pitcher_id)
#print all of the unique values in 'events' column
print(data['events'].unique())
# #filter the data to include only batted ball events, which are any 'events' that result in a fair ball 
# batted_data = data[data['events'].notnull()]
# #remove strikeouts, walks, or hit by pitches from batted_data
# batted_data = batted_data[~batted_data['events'].isin(['strikeout', 'walk', 'hit_by_pitch'])]
# # Create a barreled% where: To be Barreled, a batted ball requires an exit velocity of at least 98 mph. At that speed, balls struck with a launch angle between 26-30 degrees always garner Barreled classification. For every mph over 98, the range of launch angles expands. Every additional mph over 100 increases the range another two to three degrees until an exit velocity of 116 mph is reached. At that threshold, the Barreled designation is assigned to any ball with a launch angle between eight and 50 degrees.
# # Calculate the barreled percentage
# barreled_data = batted_data[
#     (batted_data['launch_speed'] >= 98) &
#     (
#         (batted_data['launch_speed'] <= 100) &
#         (batted_data['launch_angle'].between(26, 30))
#     ) |
#     (
#         (batted_data['launch_speed'] > 100) &
#         (batted_data['launch_speed'] <= 116) &
#         (batted_data['launch_angle'].between(26, 30 + (batted_data['launch_speed'] - 100) * 3))
#     ) |
#     (
#         (batted_data['launch_speed'] > 116) &
#         (batted_data['launch_angle'].between(8, 50))
#     )
# ]
# barrel_percentage = (len(barreled_data) / len(batted_data)) * 100
# print(f"Barrel Percentage on Batted Balls in Play: {barrel_percentage:.2f}%")

# get the average of batted_data
# batted_data = batted_data.mean().to_dict()
# print(batted_data)

# # Calculate percentages
# gb_percentage = (batted_data['batted_ball_type'] == 'ground_ball').mean() * 100
# fb_percentage = (batted_data['batted_ball_type'] == 'fly_ball').mean() * 100
# ld_percentage = (batted_data['batted_ball_type'] == 'line_drive').mean() * 100

# # Calculate Barrel Percentage
# # Barrels are usually defined in the launch_speed_angle but the definition can vary.
# # A common definition includes certain launch angles with high exit velocities.
# # Adjust according to official Statcast definition if needed.
# barrel_data = data[data['launch_speed_angle'].notnull()]
# barrel_percentage = (barrel_data['launch_speed_angle'] == 6).mean() * 100

# print(f"Ground Ball Percentage: {gb_percentage:.2f}%")
# print(f"Fly Ball Percentage: {fb_percentage:.2f}%")
# print(f"Line Drive Percentage: {ld_percentage:.2f}%")
# print(f"Barrel Percentage: {barrel_percentage:.2f}%")

# # Plotting
# plt.bar(['GB%', 'FB%', 'LD%', 'Barrel%'], [gb_percentage, fb_percentage, ld_percentage, barrel_percentage])
# plt.ylabel('Percentage')
# plt.title('Pitcher Batted Ball Event Percentages')
# plt.show()














# import statsapi 

# schedule = statsapi.schedule(start_date='04/10/2024', end_date='04/11/2024')

# for game in schedule:
#     game_datetime = game['game_datetime']
#     away_team = game['away_name']
#     home_team = game['home_name']
#     away_pitcher = game['away_probable_pitcher']
#     home_pitcher = game['home_probable_pitcher']
#     venue = game['venue_name']
#     game_id = game['game_id']
    
#     print("Date and Time:", game_datetime)
#     print("Teams:", away_team, "vs", home_team)
#     print("Probable Pitchers:", away_pitcher, "vs", home_pitcher)
#     print("Venue:", venue)
#     print("Game ID:", game_id)
#     print()

# schedule = statsapi.schedule(sportId=1)
# games = [game['game_id'] for game in schedule]
# params = {
#     "sportId": 1, 
#     "gamePk": 746728, 
#     "hydrate": "lineups",
# }

# gamedata = statsapi.get("schedule", params)

# teamdata = gamedata['dates'][0]['games'][0]['lineups']
# lineups = {}

# home = []

# away = []

# for player in teamdata['homePlayers']:
#     name = player['fullName']

#     home.append(name)

# lineups['home'] = home

# for player in teamdata['awayPlayers']:
#     name = player['fullName']
#     away.append(name)

# lineups['away'] = away

