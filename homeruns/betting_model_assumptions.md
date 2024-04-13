# Betting on home runs 
## Hypothesis: 
* We can create a dataset that characterizes the types of pitches a pitcher throws, how hard they throw them, and how often they give up barreled bats to hitters. 
* We can create a dataset that characterizes the types of pitches a hitter barrels, their average launch angle for a pitch profile, and how often they hit home runs (total, consistency). 
* We can use these two datasets to create a betting model that predicts the matchups during which a player will hit a home run. Then use this model to place bets. 

## Data Required: 
* Probable starters (who is going to pitch on what day) :check:
* Who is playing today? If we can't get lineup cards, we at least need to check which teams have games scheduled and which players are on the teams playing. 
    * Should be able to get the list of teams playing via the Probable Starters table, so it's just getting the players in the starting lineup for those teams. 
* Associated statcast data for both batters and pitchers 

## Data Exploration: 
* Want to see some visual confirmation of our hypothesized predictors
    * Do players have a given "long ball" pitch profile. 
        * Do some players favor curveballs/off-speed pitches over fastballs? 
        * Is this a good predictor of the likelihood a player goes yard? 
        * When they've hit home runs do the pitcher's pitch profile align with the pitch type that they went yard on?
