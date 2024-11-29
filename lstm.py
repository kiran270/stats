import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Load and preprocess data
df = pd.read_csv("output.csv")

# Clean data
df["Runs"] = (
    df["Runs"]
    .str.replace("*", "", regex=False)
    .replace(["DNB", "N/A", "-", "TDNB", "absent", "sub"], "0")
    .astype(int)
)
df["wickets"] = df["wickets"].replace(["DNB", "N/A", "-", "TDNB", "absent", "sub"], 0).astype(int)
df["fantasy_points"] = (df["Runs"] * 1.25) + (df["wickets"] * 25)

# Filter data based on innings type and opposition
innings_type = int(input("Enter the innings type (1 or 2): "))
opposition = input("Enter the opposition team: ")
df = df[(df["Innings"] == innings_type) & (df["opposition"] == opposition)]

# Sort data by player and date (assuming a date column is available)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['player', 'date'])

# Normalize data
scaler = MinMaxScaler()
df[['Runs', 'wickets', 'fantasy_points']] = scaler.fit_transform(df[['Runs', 'wickets', 'fantasy_points']])

# Prepare data for LSTM
def create_sequences(data, sequence_length):
    sequences = []
    for i in range(len(data) - sequence_length):
        seq = data[i : i + sequence_length]
        label = data[i + sequence_length][-1]  # Fantasy points
        sequences.append((seq, label))
    return sequences

sequence_length = 5  # Use the last 5 matches as input
player_data = []

for player in df['player'].unique():
    player_df = df[df['player'] == player][['Runs', 'wickets', 'fantasy_points']].values
    sequences = create_sequences(player_df, sequence_length)
    player_data.extend(sequences)

# Split into input (X) and target (y)
X, y = zip(*player_data)
X = np.array(X)
y = np.array(y)

# Define LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=False, input_shape=(X.shape[1], X.shape[2])))
model.add(Dropout(0.2))
model.add(Dense(1))

model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

# Train the model
model.fit(X, y, epochs=20, batch_size=32, validation_split=0.1)

# Predict fantasy points for each player
predictions = {}
for player in df['player'].unique():
    player_df = df[df['player'] == player][['Runs', 'wickets', 'fantasy_points']].values[-sequence_length:]
    player_df = np.expand_dims(player_df, axis=0)
    pred_fantasy_points = model.predict(player_df)[0][0]
    predictions[player] = scaler.inverse_transform([[0, 0, pred_fantasy_points]])[0][-1]

# Select the top 11 players
top_11_players = sorted(predictions.items(), key=lambda x: x[1], reverse=True)[:11]

# Display top 11 players
print("\nTop 11 Players for the Upcoming Match:")
for player, points in top_11_players:
    print(f"{player}: Predicted Fantasy Points = {points:.2f}")

