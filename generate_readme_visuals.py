import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import shutil

# Set style for dark theme
plt.style.use('dark_background')
sns.set_palette("husl")

DATA_PATH = 'cleaned_nigerian_spotify_songs.csv'
IMAGES_DIR = 'images'
VISUALS_DIR = 'Visuals'

def create_images_directory():
    """Create images directory and copy existing visuals"""
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    
    # Copy existing visuals with proper names
    if os.path.exists(VISUALS_DIR):
        # Copy and rename files
        visual_mapping = {
            'top_genres.png': 'genre_distribution.png',
            'correlation_heatmap.png': 'correlation_heatmap.png',
            'songs_over_time.png': 'songs_over_time.png',
            'popularity_distribution.png': 'popularity_distribution.png'
        }
        
        for old_name, new_name in visual_mapping.items():
            old_path = os.path.join(VISUALS_DIR, old_name)
            new_path = os.path.join(IMAGES_DIR, new_name)
            if os.path.exists(old_path):
                shutil.copy2(old_path, new_path)
                print(f"Copied {old_name} -> {new_name}")

def generate_additional_visuals():
    """Generate missing visualizations for README"""
    df = pd.read_csv(DATA_PATH)
    
    # Ensure release_date is datetime
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    
    # 1. Audio Features Radar Chart
    audio_features = ['danceability', 'energy', 'loudness', 'speechiness', 
                      'acousticness', 'instrumentalness', 'liveness', 'valence']
    
    # Calculate average of each feature (normalize loudness to 0-1 scale)
    feature_values = []
    feature_labels = []
    
    for feature in audio_features:
        if feature in df.columns:
            if feature == 'loudness':
                # Normalize loudness from typical range [-60, 0] to [0, 1]
                normalized = (df[feature] + 60) / 60
                feature_values.append(normalized.mean())
            else:
                feature_values.append(df[feature].mean())
            feature_labels.append(feature.capitalize())
    
    # Create radar chart
    angles = np.linspace(0, 2 * np.pi, len(feature_labels), endpoint=False).tolist()
    feature_values_plot = feature_values + [feature_values[0]]  # Complete the circle
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    ax.plot(angles, feature_values_plot, 'o-', linewidth=2, color='#1DB954', label='Average')
    ax.fill(angles, feature_values_plot, alpha=0.25, color='#1DB954')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_labels, size=10)
    ax.set_ylim(0, 1)
    ax.set_title('Audio Features Profile - Nigerian Spotify Songs', size=14, pad=20)
    ax.grid(True, color='gray', alpha=0.3)
    plt.savefig(f'{IMAGES_DIR}/audio_features_radar.png', dpi=300, bbox_inches='tight', 
                facecolor='#0e1117')
    plt.close()
    print("Generated audio_features_radar.png")
    
    # 2. Danceability vs Energy Scatter Plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sample data if too large
    sample_size = min(1000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    
    scatter = ax.scatter(df_sample['danceability'], df_sample['energy'], 
                        c=df_sample['popularity'], cmap='viridis', 
                        alpha=0.6, s=50, edgecolors='white', linewidth=0.5)
    
    ax.set_xlabel('Danceability', fontsize=12)
    ax.set_ylabel('Energy', fontsize=12)
    ax.set_title('Danceability vs Energy (colored by Popularity)', fontsize=14, pad=20)
    ax.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Popularity', fontsize=10)
    
    plt.savefig(f'{IMAGES_DIR}/danceability_energy_scatter.png', dpi=300, 
                bbox_inches='tight', facecolor='#0e1117')
    plt.close()
    print("Generated danceability_energy_scatter.png")
    
    # 3. Top Artists Table (as visualization)
    top_artists = df.groupby('artist').agg({
        'name': 'count',
        'popularity': 'mean'
    }).round(1)
    top_artists.columns = ['Songs', 'Avg Popularity']
    top_artists = top_artists.sort_values('Songs', ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    table_data.append(['Artist', 'Songs', 'Avg Pop'])
    for artist, row in top_artists.iterrows():
        # Truncate long artist names
        artist_name = artist[:30] + '...' if len(artist) > 30 else artist
        table_data.append([artist_name, int(row['Songs']), f"{row['Avg Popularity']:.1f}"])
    
    table = ax.table(cellText=table_data, cellLoc='left', loc='center',
                    colWidths=[0.6, 0.2, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header row
    for i in range(3):
        table[(0, i)].set_facecolor('#1DB954')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style data rows
    for i in range(1, len(table_data)):
        for j in range(3):
            table[(i, j)].set_facecolor('#262730' if i % 2 == 0 else '#1a1d24')
            table[(i, j)].set_text_props(color='white')
    
    plt.title('🏆 Top Artists by Song Count', fontsize=14, pad=20, color='white')
    plt.savefig(f'{IMAGES_DIR}/top_artists_table.png', dpi=300, 
                bbox_inches='tight', facecolor='#0e1117')
    plt.close()
    print("Generated top_artists_table.png")

if __name__ == "__main__":
    print("Creating images directory...")
    create_images_directory()
    
    print("\nGenerating additional visualizations...")
    generate_additional_visuals()
    
    print("\n✅ All visualizations generated successfully!")
    print(f"Images saved to: {IMAGES_DIR}/")
