
import pandas as pd
import os
import json

DATA_PATH = 'cleaned_nigerian_spotify_songs.csv'
OUTPUT_DIR = 'dashboard'
OUTPUT_FILE = 'data.json'

def export_to_json():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Ensure release_date logic is consistent (extract year)
    # The csv has full date string, let's make sure we have year for filtering
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    
    # Fill NaN for JSON serialization safety
    df = df.fillna("")
    
    # Convert to list of dicts
    data = df.to_dict(orient='records')
    
    # Save to JSON
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    print(f"Exporting {len(data)} records to {output_path}...")
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4, default=str)
        
    print("Export complete.")

if __name__ == "__main__":
    export_to_json()
