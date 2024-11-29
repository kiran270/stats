import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

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

# Add "latest 5 matches" feature based on row order
df["latest_5_avg_fantasy_points"] = (
    df.groupby("player")["fantasy_points"]
    .rolling(5, min_periods=1)
    .mean()
    .reset_index(level=0, drop=True)
)

# Input innings type and opposition
innings_type = int(input("Enter the innings type (1 or 2): "))
opposition = input("Enter the opposition team: ")

# Store predictions for all players
fantasy_points_predictions = []

# Get unique players
players = df["player"].unique()

# Loop through each player
for player in players:
    player_data = df[df["player"] == player]

    # Skip if no records are available
    if len(player_data) == 0:
        fantasy_points_predictions.append({
            "player": player,
            "innings_type": innings_type,
            "predicted_fantasy_points": 0,
            "actual_fantasy_points": 0
        })
        continue

    # Features and target
    X = player_data[["Innings", "latest_5_avg_fantasy_points"]]
    y = player_data["fantasy_points"]

    # Handle NaNs in features
    X = X.fillna(0)
    y = y.fillna(0)

    # Split the data into training and testing sets (90% train, 10% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    # Handle cases with only one record
    if len(player_data) == 1:
        predicted_fantasy_points = y.iloc[0]
    else:
        model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        model.fit(X_train, y_train)

        # Predict for the next innings
        next_innings = pd.DataFrame({
            "Innings": [innings_type],
            "latest_5_avg_fantasy_points": [player_data["latest_5_avg_fantasy_points"].iloc[-1]]
        }).fillna(0)
        predicted_fantasy_points = model.predict(next_innings)[0]

        # Evaluate model performance on the test data
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Player: {player}, MSE: {mse}, R-squared: {r2}")

    predicted_fantasy_points = round(predicted_fantasy_points)

    # Store predictions with actual fantasy points from the test data
    actual_fantasy_points = y_test.iloc[0] if len(y_test) > 0 else 0

    fantasy_points_predictions.append({
        "player": player,
        "innings_type": innings_type,
        "predicted_fantasy_points": predicted_fantasy_points,
        "actual_fantasy_points": actual_fantasy_points
    })

# Convert predictions to a DataFrame
fantasy_points_df = pd.DataFrame(fantasy_points_predictions)

# Print backtest results
print(fantasy_points_df)

# Calculate and print overall performance metrics
backtest_mse = mean_squared_error(fantasy_points_df["actual_fantasy_points"], fantasy_points_df["predicted_fantasy_points"])
backtest_r2 = r2_score(fantasy_points_df["actual_fantasy_points"], fantasy_points_df["predicted_fantasy_points"])
print(f"\nOverall Backtest MSE: {backtest_mse}")
print(f"Overall Backtest R-squared: {backtest_r2}")

# Sort by predicted fantasy points in descending order
fantasy_points_df = fantasy_points_df.sort_values(by="predicted_fantasy_points", ascending=False)

# Save predictions to a CSV file
output_file = f"fantasy_points_predictions_innings_{innings_type}.csv"
fantasy_points_df.to_csv(output_file, index=False)
