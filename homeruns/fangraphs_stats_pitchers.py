import requests, re
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from config_bigquery import json_key_path, project_id, dataset_name

table_name = 'fangraphs_pitcher_stats'

credentials = service_account.Credentials.from_service_account_file(json_key_path)
client = bigquery.Client(credentials=credentials, project=project_id)
table_id = f"{project_id}.{dataset_name}.{table_name}"

pd.set_option('display.max_columns', None)

def fangraphs_player_stats(playerid, season): 

   def fangraphs_overall_stats(playerid):
      url = f'https://www.fangraphs.com/api/players/stats?playerid={playerid}&position=P&st=true&'
      response = requests.get(url)
      data = response.json()
      data = pd.DataFrame(data['data'])
      return data

   def fangraphs_advanced_stats(playerid, season):
      url = f'https://www.fangraphs.com/api/players/splits?playerid={playerid}&position=P&season={season}&split='
      response = requests.get(url)
      data = response.json()
      return data

   def extract_year(url):
      match = re.search(r'season=(\d+)', url)
      return int(match.group(1)) if match else None

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
      # Replace space with underscore
      clean_name = clean_name.replace(' ', '_')
      # Prefix with an underscore if the name starts with a number
      if re.match(r'^\d', clean_name):
         clean_name = '_' + clean_name
      return clean_name

   # Get overall player stats from Fangraphs 
   data = fangraphs_overall_stats(playerid)
   # Add a new column 'Year' by applying the function to the 'Season' column
   data['Year'] = data['Season'].apply(extract_year)
   # Filter the DataFrame for MLB data and the year 
   overall_stats = data[(data['AbbLevel'] == 'MLB') & (data['Year'] == season)]
   # Filter the DataFrame for the columns we want": 
   overall_stats = overall_stats[['Season', 'IP', 'HR', 'HR/9', 'GB/FB', 'HR/FB', 'Pull%', 'Cent%', 'Oppo%', 'Soft%', 'Med%', 'Hard%', 'EV', 'LA', 'Barrel%', 'HardHit%']]
   # Prepend each column name with 'ovr_' to indicate it is an overall statistic
   overall_stats.columns = ['ovr_' + col if col != 'Season' else col for col in overall_stats.columns]
   # Drop the 'Season' column
   overall_stats = overall_stats.drop(columns='Season')
   # Insert the playerid and season as the first two columns
   overall_stats.insert(0, 'playerid', playerid)
   overall_stats.insert(1, 'season', season)
   # Clean column names using the clean_column_name function
   overall_stats.columns = [clean_column_name(col) for col in overall_stats.columns]

   # Get advanced player stats from Fangraphs
   data = fangraphs_advanced_stats(playerid, season)
   # Convert the data to a pandas DataFrame
   split_stats = pd.DataFrame(data)
    # Filter to only vs L and vs R in the Split column 
   split_stats = split_stats[split_stats['Split'].str.contains('vs L|vs R')]
   # Filter to remove Home and Away splits
   split_stats = split_stats[~split_stats['Split'].str.contains('Home|Away')] 
   # Filter to only the columns we want: PA, HR, GB/FB, FB%, Pull%, Hard%
   split_stats = split_stats[['Split', 'IP', 'HR', 'HR/9', 'GB/FB', 'FB%', 'HR/FB', 'Pull%', 'Cent%', 'Oppo%', 'Soft%', 'Med%', 'Hard%']]
   # Append the playerid and season to the DataFrame as the first two columns
   split_stats.insert(0, 'playerid', playerid)
   split_stats.insert(1, 'season', season)
   # Reshape the DataFrame so that all stats are in the same row
   split_stats = split_stats.pivot(index=['playerid', 'season'], columns='Split')
   # Flatten the MultiIndex columns so that the handedness is the start of the column name
   split_stats.columns = [f'{col[1]}_{col[0]}' for col in split_stats.columns]
   # Reset the index to make the playerid and season columns regular columns
   split_stats = split_stats.reset_index()
   # Rename the columns to remove the 'Split_' prefix
   split_stats.columns = [col.replace('Split_', '') for col in split_stats.columns]
   # Clean the column names using the clean_column_name function
   split_stats.columns = [clean_column_name(col) for col in split_stats.columns]
   # Join the two DataFrames on the playerid and season columns and keep all the player data
   merged_df = pd.merge(overall_stats, split_stats, on=['playerid', 'season'], how='outer')

   # Write merged_df to BigQuery using the connection defined above
   merged_df.to_gbq(table_id, project_id=project_id, if_exists='replace', credentials=credentials)

   # # Save the combined DataFrame to a CSV file
   # merged_df.to_csv('fangraphs_combined_pitcher_stats.csv', index=False)

if __name__ == '__main__':
   # Ask the user for input
   playerid = input("Enter the playerid: ")
   season = input("Enter the season: ")
   # Store the playerid and season as integers
   playerid = int(playerid)
   season = int(season)
   # Call the function
   fangraphs_player_stats(playerid, season)
   print("Pitcher stats saved to fangraphs_combined_pitcher_stats.csv")