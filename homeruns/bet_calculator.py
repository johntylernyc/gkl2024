VHI = 1.02 # Park HR index for the venue
league_HHR = 36.3
league_FB = 23.5
weight_overall = 0.45
weight_specific = 0.55
weight_HHR = 0.45 
weight_FB = 0.55
baseline_HRP = 0.03
at_bats = 2.5
smooth_factor = 0.8 

# Ask user for input, what hand the pitcher and batter are
pitcher_hand = input("Enter the pitcher's hand (L/R): ").upper()
batter_hand = input("Enter the batter's hand (L/R): ").upper()

# Using the pitcher hand and batter hand, request the user to input the necessary stats
if pitcher_hand == 'L' and batter_hand == 'L':
    PHHR_situational = float(input("Enter the pitcher's Hard Hit Rate against left-handed batters: "))
    PFB_situational = float(input("Enter the pitcher's Fly Ball Rate against left-handed batters: "))
    BHHR_situational = float(input("Enter the batter's Hard Hit Rate against left-handed pitchers: "))
    BFB_situational = float(input("Enter the batter's Fly Ball Rate against left-handed pitchers: "))
elif pitcher_hand == 'L' and batter_hand == 'R':
    PHHR_situational = float(input("Enter the pitcher's Hard Hit Rate against right-handed batters: "))
    PFB_situational = float(input("Enter the pitcher's Fly Ball Rate against right-handed batters: "))
    BHHR_situational = float(input("Enter the batter's Hard Hit Rate against left-handed pitchers: "))
    BFB_situational = float(input("Enter the batter's Fly Ball Rate against left-handed pitchers: "))
elif pitcher_hand == 'R' and batter_hand == 'L':
    PHHR_situational = float(input("Enter the pitcher's Hard Hit Rate against left-handed batters: "))
    PFB_situational = float(input("Enter the pitcher's Fly Ball Rate against left-handed batters: "))
    BHHR_situational = float(input("Enter the batter's Hard Hit Rate against right-handed pitchers: "))
    BFB_situational = float(input("Enter the batter's Fly Ball Rate against right-handed pitchers: "))
elif pitcher_hand == 'R' and batter_hand == 'R':
    PHHR_situational = float(input("Enter the pitcher's Hard Hit Rate against right-handed batters: "))
    PFB_situational = float(input("Enter the pitcher's Fly Ball Rate against right-handed batters: "))
    BHHR_situational = float(input("Enter the batter's Hard Hit Rate against right-handed pitchers: "))
    BFB_situational = float(input("Enter the batter's Fly Ball Rate against right-handed pitchers: "))
else:
    print("Invalid input. Please enter 'L' or 'R' for the pitcher and batter hands.")

# Get overall stats for the pitcher and batter
PHHR = float(input("Enter the pitcher's overall Hard Hit Rate: "))
PFB = float(input("Enter the pitcher's overall Fly Ball Rate: "))
BHHR = float(input("Enter the batter's overall Hard Hit Rate: "))
BFB = float(input("Enter the batter's overall Fly Ball Rate: "))

# Calculate the adjusted stats based on the pitcher and batter hands
Adjusted_PHHR = (PHHR * weight_overall + PHHR_situational * weight_specific) / (weight_overall + weight_specific)
Adjusted_PFB = (PFB * weight_overall + PFB_situational * weight_specific) / (weight_overall + weight_specific)
Adjusted_BHHR = (BHHR * weight_overall + BHHR_situational * weight_specific) / (weight_overall + weight_specific)
Adjusted_BFB = (BFB * weight_overall + BFB_situational * weight_specific) / (weight_overall + weight_specific)

# Adjust stats for the batter weights on HHR and FB 
Adjusted_BHHR = (Adjusted_BHHR * weight_HHR + BHHR_situational * weight_FB) / (weight_HHR + weight_FB)
Adjusted_BFB = (Adjusted_BFB * weight_FB + BFB_situational * weight_HHR) / (weight_HHR + weight_FB)

# Adjust stats for the pitcher weights on HHR and FB 
Adjusted_PHHR = (Adjusted_PHHR * weight_HHR + PHHR_situational * weight_FB) / (weight_HHR + weight_FB)
Adjusted_PFB = (Adjusted_PFB * weight_FB + PFB_situational * weight_HHR) / (weight_HHR + weight_FB)

# Convert percentages to proportions for calculation
Adjusted_PHHR /= 100
Adjusted_PFB /= 100
Adjusted_BHHR /= 100
Adjusted_BFB /= 100

league_HHR /= 100
league_FB /= 100

# Calculate percentage differences relative to league averages for the batter
batter_percentage_diff_HHR = (Adjusted_BHHR - league_HHR) / league_HHR
batter_percentage_diff_FB = (Adjusted_BFB - league_FB) / league_FB
# Calculate percentage differences relative to league averages for the pitcher
pitcher_percentage_diff_PHHR = (Adjusted_PHHR - league_HHR) / league_HHR
pitcher_percentage_diff_PFB = (Adjusted_PFB - league_FB) / league_FB

HRP_realistic = baseline_HRP * (1 + smooth_factor * (batter_percentage_diff_HHR + batter_percentage_diff_FB + pitcher_percentage_diff_PHHR + pitcher_percentage_diff_PFB)) * VHI

print(f"Probability of hitting a home run in a single at bat: {HRP_realistic:.2%}")

# Re-defining the probabilities and number of experiments after state reset
probability_one_experiment = HRP_realistic
number_of_experiments = at_bats

# Calculate the probability of the event not occurring in a single experiment
probability_not_occuring_one = 1 - probability_one_experiment

# Calculate the probability of the event not occurring in 2.5 experiments
probability_not_occuring_multiple = probability_not_occuring_one ** number_of_experiments

# Calculate the probability of the event occurring at least once in 2.5 experiments
probability_occuring_at_least_once = 1 - probability_not_occuring_multiple
probability_occuring_at_least_once

HRP_realistic = probability_occuring_at_least_once

print(f"Probability of hitting at least one home run against the starting pitcher: {HRP_realistic:.2%}")

# Ask for user input on odds and bet amount
odds_win = float(input("Enter book odds for over 0.5 homeruns: "))
bet_amount = float(input("Enter the bet amount: "))

p_win = HRP_realistic
payoff_win = (odds_win/100) + bet_amount
p_loss = 1 - p_win
payoff_loss = -bet_amount
ev = (p_win * payoff_win) + (p_loss * payoff_loss)
print(f"Expected value: ${ev:.2f}")


'''
Griffin Canning (R) 
OVR 0.8 HHR
OVR 16.3 BAR

R 25% HHR 
R 28.8 FB% 
L 45.5 HHR 
L 42.4 FB% 
'''

# # Allow the user to run the program again, entering a new batter and updating pitcher inputs based on the batter hand
# while True:
#     run_again = input("Do you want to run the program again with a new batter? (y/n): ")
#     if run_again.lower() != 'y':
#         break
#     batter_hand_new = input("Enter the batter's hand (L/R): ").upper()
#     if batter_hand_new == 'L':
#         BHHR_situational = float(input("Enter the batter's Hard Hit Rate against {pitcher_hand}-handed pitchers: "))
#         BFB_situational = float(input("Enter the batter's Fly Ball Rate against {pitcher_hand}-handed pitchers: "))
#     elif batter_hand_new == 'R':
#         BHHR_situational = float(input("Enter the batter's Hard Hit Rate against {pitcher_hand}-handed pitchers: "))
#         BFB_situational = float(input("Enter the batter's Fly Ball Rate against {pitcher_hand}-handed pitchers: "))
#     else:
#         print("Invalid input. Please enter 'L' or 'R' for the batter hand.")
#         continue

#     if batter_hand_new != batter_hand: 
#         if batter_hand_new == 'L':
#             PHHR_situational = float(input("Enter the pitcher's Hard Hit Rate against left-handed batters: "))
#             PFB_situational = float(input("Enter the pitcher's Fly Ball Rate against left-handed batters: "))
#         elif batter_hand_new == 'R':
#             PHHR_situational = float(input("Enter the pitcher's Hard Hit Rate against right-handed batters: "))
#             PHHR_situational = float(input("Enter the pitcher's Fly Ball Rate against right-handed batters: "))
#         else:
#             print("Invalid input. Please enter 'L' or 'R' for the batter hand.")
#             continue

#     BHHR = float(input("Enter the batter's overall Hard Hit Rate: "))
#     BFB = float(input("Enter the batter's overall Fly Ball Rate: "))

#     # Calculate the adjusted stats based on the pitcher and batter hands
#     Adjusted_PHHR = (PHHR * weight_overall + PHHR_situational * weight_specific) / (weight_overall + weight_specific)
#     Adjusted_PFB = (PFB * weight_overall + PFB_situational * weight_specific) / (weight_overall + weight_specific)
#     Adjusted_BHHR = (BHHR * weight_overall + BHHR_situational * weight_specific) / (weight_overall + weight_specific)
#     Adjusted_BFB = (BFB * weight_overall + BFB_situational * weight_specific) / (weight_overall + weight_specific)

#     # Convert percentages to proportions for calculation
#     Adjusted_PHHR /= 100
#     Adjusted_PFB /= 100
#     Adjusted_BHHR /= 100
#     Adjusted_BFB /= 100

#     league_HHR /= 100
#     league_FB /= 100

#     # Calculate percentage differences relative to league averages for the batter
#     batter_percentage_diff_HHR = (Adjusted_BHHR - league_HHR) / league_HHR
#     batter_percentage_diff_FB = (Adjusted_BFB - league_FB) / league_FB
#     # Calculate percentage differences relative to league averages for the pitcher
#     pitcher_percentage_diff_PHHR = (Adjusted_PHHR - league_HHR) / league_HHR
#     pitcher_percentage_diff_PFB = (Adjusted_PFB - league_FB) / league_FB

#     HRP_realistic = baseline_HRP * (1 + batter_percentage_diff_HHR + batter_percentage_diff_FB + pitcher_percentage_diff_PHHR + pitcher_percentage_diff_PFB) * VHI

#     print(f"Probability of hitting a home run in a single at bat: {HRP_realistic:.2%}")

#     # Re-defining the probabilities and number of experiments after state reset
#     probability_one_experiment = HRP_realistic
#     number_of_experiments = at_bats

#     # Calculate the probability of the event not occurring in a single experiment
#     probability_not_occuring_one = 1 - probability_one_experiment

#     # Calculate the probability of the event not occurring in 2.5 experiments
#     probability_not_occuring_multiple = probability_not_occuring_one ** number_of_experiments

#     # Calculate the probability of the event occurring at least once in 2.5 experiments
#     probability_occuring_at_least_once = 1 - probability_not_occuring_multiple
#     probability_occuring_at_least_once

#     HRP_realistic = probability_occuring_at_least_once

#     print(f"Probability of hitting at least one home run against the starting pitcher: {HRP_realistic:.2%}")

#     # Ask for user input on odds and bet amount
#     odds_win = float(input("Enter the odds of winning: "))
#     bet_amount = float(input("Enter the bet amount: "))

#     p_win = HRP_realistic
#     payoff_win = (odds_win /100) + bet_amount
#     p_loss = 1 - p_win
#     payoff_loss = -bet_amount
#     ev = (p_win * payoff_win) + (p_loss * payoff_loss)
#     print(f"Expected value: ${ev:.2f}")