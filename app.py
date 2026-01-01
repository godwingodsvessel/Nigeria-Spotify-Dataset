
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Configuration
st.set_page_config(
    page_title="Nigerian Spotify Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stButton>button {
            color: #ffffff;
            background-color: #1DB954; /* Spotify Green */
            border-radius: 20px;
        }
        h1, h2, h3 {
            font-family: 'Helvetica Neue', sans-serif;
            color: #1DB954;
        }
        .metric-card {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
        }
    </style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_nigerian_spotify_songs.csv')
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['year'] = df['release_date'].dt.year
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🎧 Filter Controls")

# Year Filter
min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_years = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

# Genre Filter
genres = ['All'] + sorted(df['artist_top_genre'].unique().tolist())
selected_genre = st.sidebar.selectbox("Select Genre", genres)

# Artist Filter
artists = ['All'] + sorted(df['artist'].unique().tolist())
selected_artist = st.sidebar.selectbox("Select Artist", artists)

# Apply Filters
filtered_df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
if selected_genre != 'All':
    filtered_df = filtered_df[filtered_df['artist_top_genre'] == selected_genre]
if selected_artist != 'All':
    filtered_df = filtered_df[filtered_df['artist'] == selected_artist]

# Main Dashboard
st.title("🎵 Nigerian Spotify Data Analysis")
st.markdown("### Insights into Streaming Trends, Genres, and Audio Features")

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Songs", f"{len(filtered_df)}")
with col2:
    st.metric("Avg Popularity", f"{filtered_df['popularity'].mean():.1f}")
with col3:
    st.metric("Top Genre", filtered_df['artist_top_genre'].mode()[0] if not filtered_df.empty else "N/A")
with col4:
    st.metric("Avg Danceability", f"{filtered_df['danceability'].mean():.2f}")

st.markdown("---")

# Visualizations

# Row 1: Time Series & Top Genres
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📈 Songs Released Over Time")
    if not filtered_df.empty:
        songs_per_year = filtered_df.groupby('year').size().reset_index(name='count')
        fig_time = px.line(songs_per_year, x='year', y='count', markers=True, 
                           color_discrete_sequence=['#1DB954'])
        fig_time.update_layout(xaxis_title="Year", yaxis_title="Number of Songs", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with row1_col2:
    st.subheader("🎹 Top Genres by Count")
    if not filtered_df.empty:
        top_genres = filtered_df['artist_top_genre'].value_counts().head(10).reset_index()
        top_genres.columns = ['Genre', 'Count']
        fig_genre = px.bar(top_genres, x='Count', y='Genre', orientation='h', 
                           color='Count', color_continuous_scale='Greens')
        fig_genre.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_genre, use_container_width=True)
    else:
        st.info("No data available.")

# Row 2: Audio Features & Scatter
st.markdown("---")
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("💃 Danceability vs Energy")
    if not filtered_df.empty:
        fig_scatter = px.scatter(filtered_df, x='energy', y='danceability', color='popularity',
                                 size='popularity', hover_data=['name', 'artist'],
                                 color_continuous_scale='Viridis')
        fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No data available.")

with row2_col2:
    st.subheader("📊 Audio Features Distribution")
    if not filtered_df.empty:
        features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'speechiness']
        # Check which columns exist
        available_features = [f for f in features if f in filtered_df.columns]
        if available_features:
            avg_features = filtered_df[available_features].mean().reset_index()
            avg_features.columns = ['Feature', 'Value']
            fig_radar = px.line_polar(avg_features, r='Value', theta='Feature', line_close=True)
            fig_radar.update_traces(fill='toself', line_color='#1DB954')
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Audio features missing.")


# Row 3: Top Artists & Tracks (New)
st.markdown("---")
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("🏆 Top Artists (by Song Count)")
    if not filtered_df.empty:
        top_artists = filtered_df['artist'].value_counts().head(5).reset_index()
        top_artists.columns = ['Artist', 'Songs']
        # Calculate avg popularity for these artists
        artist_pop = filtered_df.groupby('artist')['popularity'].mean().reset_index()
        top_artists = top_artists.merge(artist_pop, on='Artist')
        top_artists.columns = ['Artist', 'Songs', 'Avg Popularity']
        st.dataframe(top_artists.style.format({"Avg Popularity": "{:.1f}"}))
    else:
        st.info("No data available.")

with row3_col2:
    st.subheader("🔥 Top Tracks (by Popularity)")
    if not filtered_df.empty:
        top_tracks = filtered_df.nlargest(5, 'popularity')[['name', 'artist', 'popularity', 'year']]
        st.dataframe(top_tracks)
    else:
        st.info("No data available.")

# Data Table

st.markdown("---")
st.subheader("Detailed Data View")
with st.expander("Show Data Table"):
    st.dataframe(filtered_df.drop(columns=['year']).sort_values('popularity', ascending=False))

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by Antigravity")
