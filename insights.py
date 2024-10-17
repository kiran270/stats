import pandas as pd

# Sample player performance data (can be loaded from a CSV or Excel)
data = [
    {"Runs": 58, "Balls Faced": 98, "4s": 6, "6s": 1, "SR": 59.18, "Dismissal": "caught", "Opposition": "Australia", "Position": 5, "Innings": 3},
    {"Runs": 34, "Balls Faced": 75, "4s": 3, "6s": 1, "SR": 45.33, "Dismissal": "caught", "Opposition": "South Africa", "Position": 5, "Innings": 1},
    {"Runs": 11, "Balls Faced": 17, "4s": 1, "6s": 0, "SR": 64.7, "Dismissal": "not out", "Opposition": "South Africa", "Position": 5, "Innings": 3},
    {"Runs": 190, "Balls Faced": 318, "4s": 23, "6s": 4, "SR": 59.74, "Dismissal": "caught", "Opposition": "England", "Position": 5, "Innings": 1},
    {"Runs": 62, "Balls Faced": 131, "4s": 4, "6s": 1, "SR": 47.32, "Dismissal": "not out", "Opposition": "England", "Position": 5, "Innings": 3},
]

df = pd.DataFrame(data)

# Function to generate insights
def generate_insights(player_data):
    total_innings = len(player_data)
    total_runs = player_data["Runs"].sum()
    average_runs = player_data["Runs"].mean()
    total_balls_faced = player_data["Balls Faced"].sum()
    strike_rate = (total_runs / total_balls_faced) * 100 if total_balls_faced != 0 else 0
    boundary_percentage = ((player_data["4s"].sum() + player_data["6s"].sum()) / total_balls_faced) * 100

    most_common_dismissal = player_data["Dismissal"].mode()[0] if "Dismissal" in player_data else "Not available"
    
    # Generate key insights
    insights = {
        "Total Runs": total_runs,
        "Average Runs": round(average_runs, 2),
        "Strike Rate": round(strike_rate, 2),
        "Boundary Percentage": round(boundary_percentage, 2),
        "Most Common Dismissal": most_common_dismissal,
        "Number of Innings": total_innings
    }
    
    return insights

# Generate insights for the sample player data
insights = generate_insights(df)

# Print the insights
print("Player Insights:")
for key, value in insights.items():
    print(f"{key}: {value}")
