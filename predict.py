import pandas as pd

# Sample player performance data (replace with actual data)
data = [
    {"Runs": 58, "Balls Faced": 98, "4s": 6, "6s": 1, "SR": 59.18, "Dismissal": "caught", "Opposition": "Australia", "Ground": "Christchurch", "Role": "Batsman"},
    {"Runs": 34, "Balls Faced": 75, "4s": 3, "6s": 1, "SR": 45.33, "Dismissal": "caught", "Opposition": "South Africa", "Ground": "Mount Maunganui", "Role": "Batsman"},
    {"Runs": 11, "Balls Faced": 17, "4s": 1, "6s": 0, "SR": 64.7, "Dismissal": "not out", "Opposition": "South Africa", "Ground": "Mount Maunganui", "Role": "Batsman"},
    {"Runs": 190, "Balls Faced": 318, "4s": 23, "6s": 4, "SR": 59.74, "Dismissal": "caught", "Opposition": "England", "Ground": "Nottingham", "Role": "Batsman"},
    {"Runs": 62, "Balls Faced": 131, "4s": 4, "6s": 1, "SR": 47.32, "Dismissal": "not out", "Opposition": "England", "Ground": "Nottingham", "Role": "Batsman"},
]

df = pd.DataFrame(data)

# Weights for recent performance (more weight to recent matches)
weights = [i / 20 for i in range(1, 21)]  # Dynamic weighting based on 20 matches

# Function to calculate fantasy points
def calculate_fantasy_points(row):
    points = 0
    
    # Points for runs
    points += row["Runs"]
    
    # Points for boundaries
    points += row["4s"]  # 1 point for each four
    points += row["6s"] * 2  # 2 points for each six
    
    # Bonus points for strike rate
    if row["SR"] > 100:
        points += 10  # Strike rate above 100
    elif 80 <= row["SR"] <= 100:
        points += 5  # Strike rate between 80 and 100
    
    # Bonus for not out
    if row["Dismissal"] == "not out":
        points += 5
    
    # Additional bonus for milestones (centuries, half-centuries)
    if row["Runs"] >= 100:
        points += 20  # Bonus for a century
    elif row["Runs"] >= 50:
        points += 10  # Bonus for a half-century
    return points

# Apply fantasy points calculation for each match
df["Fantasy Points"] = df.apply(calculate_fantasy_points, axis=1)

# Weighted average function with up to 20 matches
def weighted_average_fantasy_points(df, weights):
    last_n_matches = min(len(df), 20)  # Use up to 20 matches, or fewer if not available
    recent_matches = df.tail(last_n_matches)
    
    # Adjust weights to match the number of available matches
    adjusted_weights = weights[-last_n_matches:]
    
    weighted_points_sum = sum(weight * points for weight, points in zip(adjusted_weights, recent_matches["Fantasy Points"]))
    weighted_average = weighted_points_sum / sum(adjusted_weights)
    
    return weighted_average

# Predict based on weighted average and bonus for opposition and ground
def predict_next_match_points(df, next_opposition, next_ground):
    # Use weighted average for recent performance (up to 20 matches)
    avg_points = weighted_average_fantasy_points(df, weights)
    
    # Adjust prediction based on opposition and ground performance
    opposition_matches = df[df["Opposition"] == next_opposition]
    ground_matches = df[df["Ground"] == next_ground]
    
    # Adjust based on performance against opposition
    if not opposition_matches.empty:
        opposition_avg = opposition_matches["Fantasy Points"].mean()
        avg_points = (avg_points + opposition_avg) / 2  # Give equal weight to opposition performance
    
    # Adjust based on performance at the ground
    if not ground_matches.empty:
        ground_avg = ground_matches["Fantasy Points"].mean()
        avg_points = (avg_points + ground_avg) / 2  # Give equal weight to ground performance
    
    return avg_points

# Generate fantasy points for past data
print("Fantasy Points for previous matches:")
print(df[["Runs", "Fantasy Points"]])

# Predict next match points
predicted_points = predict_next_match_points(df, "Australia", "Christchurch")
print(f"\nPredicted Fantasy Points for next match: {predicted_points:.2f}")
