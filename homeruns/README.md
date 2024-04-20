## General betting strategy 

### Determine universe of pitchers and batters we want to consider for a given day.
    ✅ Retrieve games, probable starters for each game, venue, and hr index for the park. (get_probable_starters.py)
    - For pitchers appearing in games with a venue hr index of 95 or higher evaluate: 
        - Hard hit rate above league average
        - Barrel rate at or above league average 
        - FB% at or above league average 
    - For pitchers that meet all 3 criteria, consider the following:
        - The pitcher's HR/9 rate as compared to league average. 
        - The pitcher's splits against left and right handed batters for GB/FB Rate, Hard Hit%, Pull% (from FanGraphs)
    - Using the pool of qualified pitchers, retrieve opposing team starting lineups and evaluate:
        - Batter hard hit rate above league average
        - Batter barrelled ball rate at or above league average
        - Batter FB% at or above league average
    - For batters that meet all 3 criteria, consider the following: 
        - The batter's at bats per home run rate as compared to league average. 
        - The batter's splits against left and right handed pitchers for GB/FB Rate, Hard Hit%, Pull% (from FanGraphs)

### Home run model we believe requires more nuanced data to model probability.

What will we know at the time of an at bat? 
- Who the pitcher is 
- Who the batter is 
- Information about the pitcher's arsenal and past pitches thrown and outcomes
- Information about the batter's past at bats, including pitches thrown and outcomes 

Pitcher Statcast Fields: 
- game_date 
- release_speed 
- batter (MLB Player Id tied to the play event) 
- events (Event of the resulting plate appearance) 


    - Using the above information, calculate a probability of a home run for each batter in the lineup. 
        - Use the following formula to start: TBD 
        - Over time, improve the formula by: 
            - incorporating the batter's splits against the pitcher's splits. 
            - weighting each factor based on the strength of the correlation to home runs by training a logistic regression 
              model on historical data.

## CLI interface
    - Prompt the user for the over 0.5 home runs prop odds offered by the book for each batter in the starting lineup for today's 
      games against a qualified pitcher. Example: Program asks, "[Player Name] odds: " and the user enters, "425" for +425 odds or 
      "-100" for -100 odds. If the player does not have odds available, the user can enter "0" to skip the player.
        - Calculate the expected value for each batter using the calculated probability and the odds, assuming a £1 bet. 
    - After all batters are evaluated, display the top 10 batters with the highest expected value. For each batter: 
        - Display the player name, team, and expected value for a £1 bet.
        - Ask the user whether they would like to bet on the player (Y/N). 
        - Prompt the user to enter the amount they would like to bet on the player. 
        - Calculate the projected return on investment (ROI) for the bet.
    - After all bets are placed: 
        - Display the total number of batters to bet on. 
        - Display the total bet amount, assuming £1 per bet.
        - Display the total expected value.
        - Display the total projected return on investment (ROI).

Qualified Pitcher is: 
    * Pitching in a park with a hr index of equal to or greater than 95, 
    * Has a hard hit rate above league average, 
    * Has a barreled ball rate above league average, 
    * Has a fly ball rate above league average. 

## Database to store the following data 
    - Game data: game date, game time, away team, home team, away pitcher, home pitcher, venue, hr index, game id, game status
    - Pitcher data: pitcher name, mlbam id, hard hit rate, barrel rate, fb rate, gb rate, hr/9 rate, splits against left and right
        handed batters
    - Batter data: batter name, mlbam id, hard hit rate, barrel rate, fb rate, gb rate, at bats per home run rate, splits against
        left and right handed pitchers
    - Lineup data: game id, team, batter name, mlbam id, position
    - Odds data: game id, batter name, mlbam id, odds offered by the book entered by the user
    - Expected value data: game id, batter name, mlbam id, expected value calculated by the program
    - Bet data: game id, batter name, mlbam id, bet amount, expected value, book odds, bet status (open, closed), actual ROI (calculated
        using bood odds and bet amount once bet status is closed and actual outcome is known)
    - Projected ROI data: game id, total batters to bet on, total bet amount, total expected value, total projected ROI
    - Actual ROI data: date bets placed, total batters to bet on, total bet amount, total expected value, total actual ROI

    Assumes a script to update the bets data:
        - Using the bets placed and the actual outcomes, calculate the actual return on investment (ROI) for the program.
        - Updates the bet data with the actual ROI for each bet: changing the bet status from "open" to "closed" and adding the actual ROI.

## Future ideas for improvements after initial implementation
In the future, it would be interesting to include weather as a factor in the model to adjust the model to account for the 
weather conditions and how they may impact the probability of a home run. It would require an examination and understanding
of how weather conditions have historically impacted home run rates but the following factors could be considered:
    - Wind speed and direction
    - Temperature
    - Humidity
    - Air density

Additionally, it would be useful to include Statcast data for the starting pitchers and batters in the model. Generally, 
building a profile for the pitcher's aresenal and comparing that to the batters in the opposing lineup and their performance 
against similar pitches. Based on nothing, I expect this to be the biggest opportunity to find an edge over the betting 
market as the data is not readily available on public websites and would require some data wrangling to get it into a usable
format. This would also help find opportunities for players with more favorable odds (e.g., +500 or higher). 