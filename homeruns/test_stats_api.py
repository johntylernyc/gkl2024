from pybaseball import playerid_lookup, playerid_reverse_lookup

# lookup player ID '680869'
# player = playerid_reverse_lookup([663978])
# print(player)

player = playerid_lookup('Taylor', 'Michael')
print(player)

















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

