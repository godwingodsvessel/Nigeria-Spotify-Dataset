
import sqlite3
import pandas as pd

DB_PATH = 'spotify.db'

def run_queries():
    conn = sqlite3.connect(DB_PATH)
    
    print("--- SQL Analysis Results ---")
    
    # 1. Top 5 Artists by Average Popularity (min 3 songs)
    query_artists = """
    SELECT artist, COUNT(*) as song_count, AVG(popularity) as avg_popularity
    FROM songs
    GROUP BY artist
    HAVING song_count >= 3
    ORDER BY avg_popularity DESC
    LIMIT 5;
    """
    print("\n1. Top 5 Artists by Average Popularity (min 3 songs):")
    print(pd.read_sql_query(query_artists, conn))
    
    # 2. Top 5 Tracks by Popularity
    query_tracks = """
    SELECT name, artist, popularity, release_date
    FROM songs
    ORDER BY popularity DESC
    LIMIT 5;
    """
    print("\n2. Top 5 Tracks by Popularity:")
    print(pd.read_sql_query(query_tracks, conn))
    
    # 3. Genre Popularity (Avg Popularity)
    query_genre = """
    SELECT artist_top_genre, COUNT(*) as song_count, AVG(popularity) as avg_popularity
    FROM songs
    GROUP BY artist_top_genre
    ORDER BY avg_popularity DESC
    LIMIT 10;
    """
    print("\n3. Top 10 Genres by Average Popularity:")
    print(pd.read_sql_query(query_genre, conn))
    
    # 4. Songs Released per Year (Growth Analysis)
    # Extract year from release_date (first 4 chars)
    query_growth = """
    SELECT substr(release_date, 1, 4) as year, COUNT(*) as releases
    FROM songs
    WHERE year IS NOT NULL
    GROUP BY year
    ORDER BY year DESC
    LIMIT 10;
    """
    print("\n4. Releases per Year (Last 10 Years):")
    print(pd.read_sql_query(query_growth, conn))
    
    # 5. Average Danceability & Energy by Genre (Engagement Metrics)
    query_engagement = """
    SELECT artist_top_genre, AVG(danceability) as avg_dance, AVG(energy) as avg_energy, AVG(popularity) as avg_pop
    FROM songs
    GROUP BY artist_top_genre
    ORDER BY avg_pop DESC
    LIMIT 5;
    """
    print("\n5. Engagement Metrics (Danceability/Energy) for Top Genres:")
    print(pd.read_sql_query(query_engagement, conn))

    conn.close()

if __name__ == "__main__":
    run_queries()
