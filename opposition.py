import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# Load data
csv_file = "output.csv"  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Clean and preprocess the data
df["Runs"] = (
    df["Runs"]
    .str.replace("*", "", regex=False)  # Remove '*'
    .replace(["DNB", "N/A", "-", "TDNB", "absent", "sub"], "0")  # Replace non-numeric values with '0'
    .astype(int)  # Convert to integer
)
df["wickets"] = df["wickets"].replace(["DNB", "N/A", "-", "TDNB", "absent", "sub"], 0).astype(int)
df["fantasy_points"] = (df["Runs"] * 1.25) + (df["wickets"] * 25)

# Input innings type and opposition
innings_type = int(input("Enter the innings type (1 or 2): "))
opposition = input("Enter the opposition team: ")

# Filter data for the selected innings type
df = df[df["Innings"] == innings_type]

# Store predictions for all players
fantasy_points_predictions = []

# Get unique players
players = df["player"].unique()

# Loop through each player
for player in players:
    if innings_type and opposition:  # Both innings and opposition are provided
        player_data = df[(df["player"] == player) & 
                         (df["Innings"] == innings_type) & 
                         (df["opposition"] == opposition)]
    elif innings_type:  # Only innings is provided
        player_data = df[(df["player"] == player) & 
                         (df["Innings"] == innings_type)]
    elif opposition:  # Only opposition is provided
        player_data = df[(df["player"] == player) & 
                         (df["opposition"] == opposition)]
    else:  # Neither innings nor opposition is provided
        player_data = df[df["player"] == player]
    # Skip if no records are available
    if len(player_data) == 0:
        fantasy_points_predictions.append({
            "player": player,
            "innings_type": innings_type,
            "predicted_fantasy_points": 0
        })
        continue

    # Features and target
    X = player_data[["Innings"]]
    y = player_data["fantasy_points"]

    # Handle cases with only one record
    if len(player_data) == 1:
        # Use the existing record's fantasy points as the predicted value
        predicted_fantasy_points = y.iloc[0] 
    else:
        # Train the model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Predict for the next innings
        next_innings = pd.DataFrame({"Innings": [innings_type]})
        predicted_fantasy_points = model.predict(next_innings)[0]

    predicted_fantasy_points = round(predicted_fantasy_points)

    # Store predictions
    fantasy_points_predictions.append({
        "player": player,
        "innings_type": innings_type,
        "predicted_fantasy_points": predicted_fantasy_points
    })

# Convert predictions to a DataFrame
fantasy_points_df = pd.DataFrame(fantasy_points_predictions)

# Sort by predicted fantasy points in descending order
fantasy_points_df = fantasy_points_df.sort_values(by="predicted_fantasy_points", ascending=False)

# Print detailed predictions
print(fantasy_points_df)

# Save predictions to a CSV file
output_file = f"fantasy_points_predictions_innings_{innings_type}.csv"
fantasy_points_df.to_csv(output_file, index=False)
