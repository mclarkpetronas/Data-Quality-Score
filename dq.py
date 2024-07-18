import pandas as pd
from datetime import datetime, timedelta

# Sample dataset
data = {
    'CustomerID': [1, 2, 3, 4, 5, None],
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Alice'],
    'Email': ['alice@example.com', 'bob@example.com', None, 'david@example.com', 'eve@example.com', 'alice@example.com'],
    'SignupDate': ['2020-01-01', '2020-01-02', '2020-01-03', '2021-01-04', '2021-01-05', '2021-01-06']
}

df = pd.DataFrame(data)

# Define weights
weights = {
    'completeness': 0.25,
    'uniqueness': 0.20,
    'consistency': 0.20,
    'freshness': 0.10,
    'velocity': 0.15,  # New weight for velocity
    'criticality': 0.10  # New weight for criticality
}

# Define criticality for columns (assuming 'CustomerID' and 'Email' are most critical)
column_criticality = {
    'CustomerID': 0.5,
    'Name': 0.2,
    'Email': 0.5,
    'SignupDate': 0.3
}

# Function to measure completeness
def completeness_score(df):
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    return (total_cells - missing_cells) / total_cells

# Function to measure uniqueness
def uniqueness_score(df, column):
    total_rows = df.shape[0]
    unique_rows = df[column].nunique()
    return unique_rows / total_rows

# Function to measure consistency (example: date format)
def consistency_score(df, column, date_format):
    total_rows = df.shape[0]
    try:
        pd.to_datetime(df[column], format=date_format, errors='raise')
        return 1.0
    except:
        inconsistent_rows = df[pd.to_datetime(df[column], format=date_format, errors='coerce').isna()]
        return (total_rows - len(inconsistent_rows)) / total_rows

# Freshness score for the last 5 values
def freshness_score(df, column, threshold_days=30):
    try:
        recent_dates = pd.to_datetime(df[column].dropna().tail(5))
        stale_dates = recent_dates[recent_dates < (datetime.now() - timedelta(days=threshold_days))]
        freshness = (5 - len(stale_dates)) / 5
        return freshness
    except:
        return 0  # If conversion fails, consider freshness as 0

# Function to measure velocity
def velocity_score(df, column, period_days=30):
    df['ChangeDate'] = pd.to_datetime(df['SignupDate'])
    recent_changes = df[df['ChangeDate'] >= (datetime.now() - timedelta(days=period_days))]
    velocity = len(recent_changes) / len(df)
    return velocity

# Function to measure criticality (weighted sum of criticality scores)
def criticality_score(df, column_criticality):
    total_criticality = sum(column_criticality.values())
    completeness_scores = {col: completeness_score(df[[col]]) for col in df.columns if col in column_criticality}
    weighted_criticality = sum(completeness_scores[col] * column_criticality[col] for col in completeness_scores)
    return weighted_criticality / total_criticality

# Calculate individual scores
completeness = completeness_score(df)
uniqueness = uniqueness_score(df, 'Name')  # Assuming Name should be unique
consistency = consistency_score(df, 'SignupDate', '%Y-%m-%d')
freshness = freshness_score(df, 'SignupDate', 365)  # Considering data stale if older than 365 days
velocity = velocity_score(df, 'SignupDate', 30)  # Considering velocity over the last 30 days
criticality = criticality_score(df, column_criticality)

# Calculate overall weighted score
overall_score = (completeness * weights['completeness'] +
                 uniqueness * weights['uniqueness'] +
                 consistency * weights['consistency'] +
                 freshness * weights['freshness'] +
                 velocity * weights['velocity'] +
                 criticality * weights['criticality'])

print(f"Completeness Score: {completeness:.2f}")
print(f"Uniqueness Score: {uniqueness:.2f}")
print(f"Consistency Score: {consistency:.2f}")
print(f"Freshness Score: {freshness:.2f}")
print(f"Velocity Score: {velocity:.2f}")
print(f"Criticality Score: {criticality:.2f}")
print(f"Overall Weighted Score: {overall_score:.2f}")
