
import pandas as pd
import sqlite3
import os

# File paths
DATA_PATH = 'nigerian_spotify_songs1.csv'
CLEAN_DATA_PATH = 'cleaned_nigerian_spotify_songs.csv'
DB_PATH = 'spotify.db'

def load_and_inspect_data(path):
    print(f"Loading data from {path}...")
    df = pd.read_csv(path)
    
    print("\n--- Data Structure ---")
    print(df.info())
    
    print("\n--- First 5 Rows ---")
    print(df.head())
    
    print("\n--- Numerical Description ---")
    print(df.describe())
    
    print("\n--- Missing Values ---")
    print(df.isnull().sum())
    
    print("\n--- Duplicates ---")
    duplicates = df.duplicated().sum()
    print(f"Number of duplicate rows: {duplicates}")
    
    return df

def clean_data(df):
    print("\n--- Starting Data Cleaning ---")
    
    # 1. Remove duplicate rows
    df_clean = df.drop_duplicates()
    print(f"Removed duplicates. Shape: {df_clean.shape}")
    
    # 2. Handle missing values
    # For this dataset, if 'name', 'album', 'artist' are missing, we likely can't use the row properly.
    # Let's inspect if any crucial columns are missing.
    # Numeric columns with missing values can be filled with median.
    
    # Checking for missing values in critical text columns
    critical_cols = ['name', 'artist', 'album', 'release_date']
    df_clean = df_clean.dropna(subset=critical_cols)
    print(f"Dropped rows with missing critical info. Shape: {df_clean.shape}")

    # Initialize numeric_cols by selecting numeric columns from df_clean
    numeric_cols = df_clean.select_dtypes(include=['number']).columns
    
    # Fill remaining missing numeric values with median
    if df_clean[numeric_cols].isnull().sum().sum() > 0:
        print("Filling missing numeric values with median...")
        df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
    
    # 3. Data Type Conversion
    # The 'release_date' appears to be years (integers) based on inspection.
    # We convert to datetime explicitly using format='%Y' to avoid nanosecond interpretation.
    print("Converting release_date (Year) to datetime...")
    df_clean['release_date'] = pd.to_datetime(df_clean['release_date'].astype(str), format='%Y', errors='coerce')
    
    # Drop rows where date parsing failed
    null_dates = df_clean['release_date'].isnull().sum()
    if null_dates > 0:
        print(f"Warning: {null_dates} rows have invalid release_date. Dropping them.")
        df_clean = df_clean.dropna(subset=['release_date'])
        
    print(f"Final Cleaned Shape: {df_clean.shape}")
    return df_clean

def save_data(df):
    # Save to CSV
    print(f"\nSaving cleaned data to {CLEAN_DATA_PATH}...")
    df.to_csv(CLEAN_DATA_PATH, index=False)
    
    # Save to SQLite
    print(f"Saving data to SQLite DB {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('songs', conn, if_exists='replace', index=False)
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
    else:
        df = load_and_inspect_data(DATA_PATH)
        df_clean = clean_data(df)
        save_data(df_clean)
