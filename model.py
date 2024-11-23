import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np

# Load data from CSV file
csv_file = "output.csv"  # Replace with your CSV file path
df = pd.read_csv(csv_file)

# Replace specific non-numeric values (e.g., 'DNB', 'N/A', '-') with 0
df["Runs"] = df["Runs"].replace(["DNB", "N/A", "-"], 0)
df["wickets"] = df["wickets"].replace(["DNB", "N/A", "-"], 0)

# Convert columns to numeric
df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce").fillna(0)
df["wickets"] = pd.to_numeric(df["wickets"], errors="coerce").fillna(0)
df["Innings"] = pd.to_numeric(df["Innings"], errors="coerce")

# Group data by player
players = df["player"].unique()

# Dictionary to store predictions and actual results for evaluation
results = []

for player in players:
    # Filter data for the specific player
    player_data = df[df["player"] == player]
    
    # Features (Innings) and targets (Runs and Wickets)
    X = player_data["Innings"].values.reshape(-1, 1)  # Independent variable
    y_runs = player_data["Runs"].values              # Dependent variable for runs
    y_wickets = player_data["wickets"].values        # Dependent variable for wickets
    
    # Skip if there's insufficient data for the player
    if len(X) < 2:  # At least two data points are required for training
        continue

    # Train-test split (80% training, 20% testing)
    X_train, X_test, y_runs_train, y_runs_test = train_test_split(X, y_runs, test_size=0.2, random_state=42)
    _, _, y_wickets_train, y_wickets_test = train_test_split(X, y_wickets, test_size=0.2, random_state=42)
    
    # Add weights for the training data: More recent matches (lower index) have higher weight
    weights = np.linspace(1, 2, len(X_train))
    
    # Train Weighted Linear Regression Model for Runs
    model_runs = LinearRegression()
    model_runs.fit(X_train, y_runs_train, sample_weight=weights)
    
    # Train Weighted Linear Regression Model for Wickets
    model_wickets = LinearRegression()
    model_wickets.fit(X_train, y_wickets_train, sample_weight=weights)
    
    # Predict on the test set
    predicted_runs_test = model_runs.predict(X_test)
    predicted_wickets_test = model_wickets.predict(X_test)
    
    # Predict for the next match (e.g., Innings = max(Innings) + 1)
    next_innings = np.array([[player_data["Innings"].max() + 1]])
    predicted_runs_next = model_runs.predict(next_innings)
    predicted_wickets_next = model_wickets.predict(next_innings)
    
    # Round predictions and cast to integers
    predicted_runs_next = int(round(predicted_runs_next[0]))
    predicted_wickets_next = int(round(predicted_wickets_next[0]))
    
    # Append results for test predictions
    for i in range(len(X_test)):
        results.append({
            "player": player,
            "innings": int(X_test[i][0]),
            "actual_runs": int(y_runs_test[i]),
            "predicted_runs": int(round(predicted_runs_test[i])),
            "actual_wickets": int(y_wickets_test[i]),
            "predicted_wickets": int(round(predicted_wickets_test[i]))
        })
    
    # Append predictions for the next match
    results.append({
        "player": player,
        "innings": next_innings[0][0],
        "actual_runs": "N/A",
        "predicted_runs": predicted_runs_next,
        "actual_wickets": "N/A",
        "predicted_wickets": predicted_wickets_next
    })

# Convert results to a DataFrame for better display
results_df = pd.DataFrame(results)

# Save results to a CSV file
output_file = "player_predictions_with_train_test.csv"
results_df.to_csv(output_file, index=False)

# Print results
print(results_df[results_df["player"] == "jess-jonassen-374936"])
