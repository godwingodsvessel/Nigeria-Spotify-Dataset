
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set(style="whitegrid")

DATA_PATH = 'cleaned_nigerian_spotify_songs.csv'
OUTPUT_DIR = 'eda'

def perform_eda():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    df = pd.read_csv(DATA_PATH)
    
    # 1. Distribution of Popularity (Proxy for Streaming Counts)
    plt.figure(figsize=(10, 6))
    sns.histplot(df['popularity'], kde=True, bins=20)
    plt.title('Distribution of Song Popularity')
    plt.xlabel('Popularity')
    plt.ylabel('Frequency')
    plt.savefig(f'{OUTPUT_DIR}/popularity_distribution.png')
    plt.close()
    
    # 2. Most Popular Genres
    plt.figure(figsize=(12, 8))
    # Count of songs per genre
    top_genres = df['artist_top_genre'].value_counts().head(10)
    sns.barplot(y=top_genres.index, x=top_genres.values, palette='viridis')
    plt.title('Top 10 Genres by Number of Songs')
    plt.xlabel('Number of Songs')
    plt.ylabel('Genre')
    plt.savefig(f'{OUTPUT_DIR}/top_genres.png')
    plt.close()
    
    # 3. Time Series Analysis (Songs per Year)
    # Extract year if release_date is full date, or use it if it's just year.
    # We kept release_date as object/datetime in cleaning but saved as string in CSV.
    # Let's ensure year is extracted. 
    # Some older pandas versions might need conversion.
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    
    songs_per_year = df.groupby('year').size()
    avg_popularity_per_year = df.groupby('year')['popularity'].mean()

    plt.figure(figsize=(12, 6))
    sns.lineplot(x=songs_per_year.index, y=songs_per_year.values, marker='o', label='Number of Songs')
    plt.title('Number of Songs Released Over Time')
    plt.xlabel('Year')
    plt.ylabel('Count')
    plt.savefig(f'{OUTPUT_DIR}/songs_over_time.png')
    plt.close()
    
    # 4. Correlation Heatmap
    # Select numerical columns
    numeric_df = df.select_dtypes(include=['number'])
    # Drop 'year' if it's there
    if 'year' in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=['year'])
        
    plt.figure(figsize=(12, 10))
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap of Audio Features')
    plt.savefig(f'{OUTPUT_DIR}/correlation_heatmap.png')
    plt.close()
    
    print(f"EDA plots saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    perform_eda()
