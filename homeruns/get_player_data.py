starting_pitcher_id = '605452'

from pybaseball import statcast, pitching_stats, batting_stats, playerid_lookup
from config_bigquery import json_key_path, project_id, dataset_name
from google.oauth2 import service_account
from google.cloud import bigquery
import statsapi
import pandas as pd
import re

statcast_table_name = "statcast_data"
pitching_table_name = "pitching_data" 
batting_table_name = "batting_data"

# Function to clean column names
def clean_column_name(column_name):
    # Replace special characters with underscore
    clean_name = re.sub(r'[%]', '_rate', column_name)
    # Replace special characters with underscore
    clean_name = re.sub(r'[()/]', '_', column_name)
    # Replace spaces with underscore
    clean_name = re.sub(r'\s+', '_', clean_name)
    # Remove trailing underscores
    clean_name = re.sub(r'_+$', '', clean_name)
    # Replace / with _per_
    clean_name = clean_name.replace('/', '_per_')
    # Replace period with underscore
    clean_name = clean_name.replace('.', '_')
    # Prefix with an underscore if the name starts with a number
    if re.match(r'^\d', clean_name):
        clean_name = '_' + clean_name
    return clean_name

''' 
need to retrieve plate appearance data for each at bat in 2023 season and year-to-date 
2024 season and examine the event we want to predict (home run) against all other events 
and the variables we've selected (noted below) to run a logistic regression model that 
predicts the probability of a home run given the variables we've selected.
'''

# cache.enable()
# data = statcast(start_dt='2022-03-01', end_dt='2024-04-15')
# data.to_csv('statcast_data.csv', index=False)

# credentials = service_account.Credentials.from_service_account_file(json_key_path)
# client = bigquery.Client(credentials=credentials, project=project_id)
# table_id = f"{project_id}.{dataset_name}.{statcast_table_name}"

# statcast_data = pd.read_csv('statcast_data.csv')
# statcast_data.columns = [clean_column_name(col) for col in statcast_data.columns]
# statcast_data.to_gbq(table_id, project_id=project_id, if_exists='replace', credentials=credentials)

''' 
pitching_stats gives Hard%, GB/FB, FB%, Barrel%, EV, LA, HR/FB%+ for a given player.

In order to use these stats in our statcast data we need to join on the player_id column
but the problem is we may not have these stats at "time of game"; i.e., we only have them 
in aggregate for a season (e.g., 2023) and thus we can't use them in our model. 
'''

# pitching_stats = pitching_stats(2022, 2024, qual=1, ind=1)
# pitching_stats.to_csv('pitching_stats.csv', index=False)

# credentials = service_account.Credentials.from_service_account_file(json_key_path)
# client = bigquery.Client(credentials=credentials, project=project_id)
# table_id = f"{project_id}.{dataset_name}.{pitching_table_name}"

# pitching_stats = pd.read_csv('pitching_stats.csv')
# pitching_stats.columns = [clean_column_name(col) for col in pitching_stats.columns]
# pitching_stats.to_gbq(table_id, project_id=project_id, if_exists='replace', credentials=credentials)

'''
batting_stats gives Hard%, GB/FB, FB%, Barrel%, EV, LA, HR/FB%+ for a given player. 

In order to use these stats in our statcast data we need to join on the player_id column
but the problem is we may not have these stats at "time of game"; i.e., we only have them 
in aggregate for a season (e.g., 2023) and thus we can't use them in our model. 
'''

batting_stats = batting_stats(2022, 2024, qual=1, ind=1)
batting_stats.to_csv('batting_stats.csv', index=False)

credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)
table_id = f"{project_id}.{dataset_name}.{batting_table_name}"

batting_stats = pd.read_csv('batting_stats.csv')
batting_stats.columns = [clean_column_name(col) for col in batting_stats.columns]
batting_stats.to_gbq(table_id, project_id=project_id, if_exists='replace', credentials=credentials)

''' 
working on splits data 
'''

# personIds = str(statsapi.lookup_player('canning')[0]['id']) + ',' + str(statsapi.lookup_player('caballero')[0]['id'])
# params = {'personIds':personIds, 'hydrate':'stats(group=[hitting,pitching],type=[statSplits],sitCodes=[vr,vl])'}
# people = statsapi.get('people',params)
# for person in people['people']:
#     print('{}'.format(person['fullName']))
#     for stat in person['stats']:
#         if len(stat['splits']): print('  {}'.format(stat['group']['displayName']))
#         for split in stat['splits']:
#             print('    {} {}:'.format(split['season'], split['split']['description']))
#             for split_stat,split_stat_value in split['stat'].items():
#                 print('      {}: {}'.format(split_stat, split_stat_value))
#             print('\n')

# data = playerid_lookup('Diaz', 'Yandy', fuzzy=True)
# print(data) 