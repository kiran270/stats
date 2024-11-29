import pandas as pd
from sklearn.model_selection import train_test_split
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
df["fantasy_points"] = (df["Runs"]*1.25) + (df["wickets"] * 25)

# Encode categorical variables
# label_encoder_opposition = LabelEncoder()
# label_encoder_ground = LabelEncoder()
# df["opposition_encoded"] = label_encoder_opposition.fit_transform(df["opposition"])
# df["ground_encoded"] = label_encoder_ground.fit_transform(df["ground"])

# Input innings type, opposition, and ground
innings_type = int(input("Enter the innings type (1 or 2): "))
# opposition = input("Enter the opposition team: ")
# ground = input("Enter the ground: ")

# Encode input opposition and ground
# opposition_encoded = label_encoder_opposition.transform([opposition])[0]
# ground_encoded = label_encoder_ground.transform([ground])[0]

# Filter data for the selected innings type
df = df[df["Innings"] == innings_type]

# Store predictions for all players
fantasy_points_predictions = []

# Get unique players
players = df["player"].unique()

# Loop through each player
for player in players:
    player_data = df[df["player"] == player]

    # Skip if not enough data for training
    if len(player_data) < 2:
        fantasy_points_predictions.append({
            "player": player,
            "innings_type": innings_type,
            "predicted_fantasy_points": 0
        })
        continue

    # Features and target
    X = player_data[["Innings"]]
    y = player_data["fantasy_points"]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict for the next innings at the specified ground and opposition
    next_innings = pd.DataFrame({
        "Innings": [innings_type]
    })
    predicted_fantasy_points = model.predict(next_innings)
    predicted_fantasy_points = round(predicted_fantasy_points[0])
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
