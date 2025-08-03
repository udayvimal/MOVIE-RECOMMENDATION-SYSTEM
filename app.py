import streamlit as st
import pickle
import pandas as pd
import requests

# Function to fetch movie poster from OMDb API
def fetch_poster(movie_title):
    api_key = "63dfac01"  # Your OMDb API Key
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data.get("Poster", "https://via.placeholder.com/200")  # Default image if not found

# Function to recommend movies
def recommend(movie, movies, similarity):
    """Recommend movies and fetch posters."""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []  # Return empty lists if movie is not found

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    
    for i in movies_list:
        movie_title = movies.iloc[i[0]]['title']
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))  # Fetch poster
    
    return recommended_movies, recommended_posters

# Load movie dataset
import pickle
import pandas as pd
import gzip
import requests
import os

# Google Drive download function
def download_file_from_google_drive(url, dest_path):
    if not os.path.exists(dest_path):
        response = requests.get(url)
        with open(dest_path, 'wb') as f:
            f.write(response.content)

# Direct download URLs
MOVIES_URL = "https://drive.google.com/uc?export=download&id=1xqEaKwnVU5kNA-Idq4obSjts5ZGG_EB_"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1LGuTPZUJb20s3MFiuYuEi7hT79dTla-a"

# Download only if not already present
download_file_from_google_drive(MOVIES_URL, "movies.pkl.gz")
download_file_from_google_drive(SIMILARITY_URL, "similarity.pkl.gz")

# Load files
with gzip.open("movies.pkl.gz", "rb") as f:
    movies_dict = pickle.load(f)

with gzip.open("similarity.pkl.gz", "rb") as f:
    similarity = pickle.load(f)

movies = pd.DataFrame(movies_dict)

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    '🔍 Select a movie:',
    movies['title'].values
)

if st.button('Recommend'):
    recommendations, posters = recommend(selected_movie_name, movies, similarity)

    if recommendations:
        # Display movies with posters in a row
        cols = st.columns(5)  # 5 columns for 5 movies
        for i in range(5):
            with cols[i]:
                st.image(posters[i], caption=recommendations[i], use_container_width=True)
    else:
        st.error("No recommendations found! Please select a valid movie.")

