import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
import warnings
# Step 1: Load Data
file_path = 'women_BIGBASH.csv'  # Replace with actual file path
df = pd.read_csv(file_path)

# Step 2: Data Preprocessing
# Extract overs data and the final score

# Assume over columns are 'Over 1', 'Over 2', ..., 'Over 20' and the last column is 'Final_Score'
overs_columns = [f"Over {i}" for i in range(1, 21)]  # Over columns from Over 1 to Over 20

# Extract final score and clean data
final_scores = []
for index, row in df.iterrows():
    final_score = None
    for over in reversed(overs_columns):  # Start checking from the last over column
        if pd.notna(row[over]) and row[over] != 'N/A':
            over_score = str(row[over]).replace('="', '').replace('"', '')
            score, wickets = over_score.split('/')
            try:
                final_score = int(score)
            except ValueError:
                final_score = None  # If the score cannot be converted to integer, we set it to None
            break
    final_scores.append(final_score)

df['Final_Score'] = final_scores

# Step 3: Remove rows with NaN in 'Final_Score'
df_cleaned = df.dropna(subset=['Final_Score'])

# Step 4: Create Features (Over, Score, Wickets) for Model Training
data = []
for index, row in df_cleaned.iterrows():
    for over_index in range(20):  # For each over column
        over_score = row[overs_columns[over_index]]
        if pd.notna(over_score) and over_score != 'N/A':
            over_score = str(over_score).replace('="', '').replace('"', '')
            try:
                score, wickets = over_score.split('/')
                data.append({
                    'Over': over_index + 1,  # Over number
                    'Score': int(score),  # Score at the over
                    'Wickets': int(wickets),  # Wickets at the over
                    'Final_Score': row['Final_Score']  # Final score of the match
                })
            except ValueError:
                continue  # Skip rows where the data cannot be parsed properly

# Convert to DataFrame for training
training_df = pd.DataFrame(data)

# Step 5: Define Features (X) and Target (y)
X = training_df[['Over', 'Score', 'Wickets']]  # Features: Over, Score, Wickets
y = training_df['Final_Score']  # Target: Final score

# Step 6: Split Data for Training and Testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 7: Train Random Forest Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 8: Evaluate the Model
predictions = model.predict(X_test)
error = np.sqrt(mean_squared_error(y_test, predictions))
# print(f"Model RMSE: {error}")

# Step 9: User Input for Prediction
print("Enter the details for prediction:")
def extract_final_score(row):
    for i in range(20, 0, -1):  # Loop through overs in reverse order (20 to 1)
        over_column = f"Over {i}"
        if over_column in row and pd.notna(row[over_column]) and row[over_column] != 'N/A':
            try:
                score = row[over_column]  # Extract the score part before '/'
                return score
            except (ValueError, IndexError):
                continue  # Skip if data format is incorrect
    return None  # Return None if no valid score is found

def predict_final_score(row):
    predictions = []
    for i in range(6, 16):
        try:
            over_input = i
            score_input, wickets_input = map(int, row[f"Over {i}"].split("/"))  # Extract score and wickets

            if not (1 <= over_input <= 20):
                print("Over number must be between 1 and 20. Skipping.")
                continue
            input_data = [[over_input, score_input, wickets_input]]
            predicted_score = model.predict(input_data)[0]
            predictions.append({
                "Over": over_input,
                "Score": score_input,
                "Wickets": wickets_input,
                "Predicted Final Score": round(predicted_score, 2)
            })
        except ValueError:
            continue
        except Exception as e:
            continue
    if predictions:
        predictions_df = pd.DataFrame(predictions)
        print("\nPredicted Scores Table:"+ extract_final_score(row))
        print(predictions_df.to_string(index=False))

df = pd.read_csv("test_wbbl.csv")
count=0
for index, row in df.iterrows():
    predict_final_score(row)
    if count > 50:
        break
    count=count+1