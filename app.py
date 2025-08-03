import streamlit as st
import pickle
import pandas as pd
import requests
import gzip
import os

# Function to fetch movie poster from OMDb API
def fetch_poster(movie_title):
    api_key = "63dfac01"  # Your OMDb API Key
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data.get("Poster", "https://via.placeholder.com/200")  # Default image if not found

# Function to recommend movies based on similarity matrix
def recommend(movie, movies, similarity):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []  # If movie not found, return empty lists

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_title = movies.iloc[i[0]]['title']
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))

    return recommended_movies, recommended_posters

# Google Drive download functions for large files with confirmation token handling
def download_file_from_google_drive(file_id, destination):
    if os.path.exists(destination):
        return  # Already downloaded

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# Google Drive file IDs (from your provided links)
MOVIES_FILE_ID = "1xqEaKwnVU5kNA-Idq4obSjts5ZGG_EB_"
SIMILARITY_FILE_ID = "1LGuTPZUJb20s3MFiuYuEi7hT79dTla-a"

# Download files if not present
download_file_from_google_drive(MOVIES_FILE_ID, "movies.pkl.gz")
download_file_from_google_drive(SIMILARITY_FILE_ID, "similarity.pkl.gz")

# Load compressed pickle files
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
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], caption=recommendations[i], use_container_width=True)
    else:
        st.error("No recommendations found! Please select a valid movie.")
