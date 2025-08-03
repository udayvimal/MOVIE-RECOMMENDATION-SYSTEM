import streamlit as st
import pickle
import pandas as pd
import requests
import gzip

# Function to fetch movie poster from OMDb API
def fetch_poster(movie_title):
    api_key = "63dfac01"  # Your OMDb API Key
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data.get("Poster", "https://via.placeholder.com/200")  # Default if not found

# Function to recommend movies
def recommend(movie, movies, similarity):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))

    return recommended_movies, recommended_posters

# Load compressed data from local GitHub repo (via Git LFS)
with open("movies.pkl", "rb") as f:
    movies_dict = pickle.load(f)

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

movies = pd.DataFrame(movies_dict)

# Streamlit UI
st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "🔍 Select a movie:",
    movies["title"].values
)

if st.button("Recommend"):
    recommendations, posters = recommend(selected_movie_name, movies, similarity)

    if recommendations:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], caption=recommendations[i], use_container_width=True)
    else:
        st.error("No recommendations found! Please select a valid movie.")

