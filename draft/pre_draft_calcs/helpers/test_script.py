from pybaseball import playerid_lookup, playerid_reverse_lookup, statcast_batter, batting_stats, statcast_batter_pitch_arsenal, pitching_stats
import pandas as pd

# data = playerid_lookup("Bellinger")
# print("data")
# print(data) 

# player_ids_list = []
# player_ids = playerid_reverse_lookup(data['IDfg'].values, key_type='fangraphs')
# player_ids = player_ids['key_mlbam'].values.tolist()
# player_ids_list.extend(player_ids)
# player_ids_list = list(dict.fromkeys(player_ids_list))

# print("ids")
# print(player_ids)
# print("list")
# print(player_ids_list)

# player_data = statcast_batter("2023-01-01", "2023-11-01", 641355)
# print("player_data") 
# print(player_data)

# player_batting = batting_stats(2021, end_season=2023, qual=200, ind=1) 
# print("player_batting") 
# print(vars(player_batting))
# print(player_batting.head())

# get data for all qualified batters in 2019
# data = statcast_batter_pitch_arsenal(2023)
# print(vars(data))
# print(data.head())

# player_pitching = pitching_stats(2021, end_season=2023, qual=200, ind=1) 
# print("player_batting") 
# print(vars(player_pitching))
# print(player_pitching.head())

from pybaseball import playerid_reverse_lookup

fg_ids = [26289]

data = playerid_reverse_lookup(fg_ids, key_type="fangraphs")

print(data)
