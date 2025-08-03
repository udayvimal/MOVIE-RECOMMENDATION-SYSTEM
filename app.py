import streamlit as st
import pickle
import pandas as pd
import requests
import os

poster_cache = {}

def fetch_poster(movie_title):
    st.write(f"DEBUG: fetch_poster called for: {movie_title}")
    if movie_title in poster_cache:
        st.write(f"DEBUG: Using cached poster for {movie_title}")
        return poster_cache[movie_title]

    api_key = "63dfac01"
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        st.write(f"DEBUG: Sending request to OMDb for {movie_title}")
        response = requests.get(url, timeout=3)
        st.write(f"DEBUG: Response status code: {response.status_code}")
        data = response.json()
        poster_url = data.get("Poster", "https://via.placeholder.com/200")
        st.write(f"DEBUG: Poster URL: {poster_url}")
    except Exception as e:
        st.write(f"ERROR: Exception fetching poster for {movie_title}: {e}")
        poster_url = "https://via.placeholder.com/200"
    
    poster_cache[movie_title] = poster_url
    return poster_url

def recommend(movie, movies, similarity):
    st.write(f"DEBUG: recommend called for movie: {movie}")
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        st.write(f"DEBUG: Found movie index: {movie_index}")
    except IndexError:
        st.error("Selected movie not found in database.")
        return [], []

    distances = similarity[movie_index]
    st.write(f"DEBUG: Retrieved similarity distances, length: {len(distances)}")
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    st.write(f"DEBUG: Top recommendations indices and scores: {movie_list}")

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_title = movies.iloc[i[0]].title
        st.write(f"DEBUG: Recommendation: {movie_title} with score {i[1]}")
        recommended_movies.append(movie_title)
        poster_url = fetch_poster(movie_title)
        recommended_posters.append(poster_url)

    st.write(f"DEBUG: Total recommendations made: {len(recommended_movies)}")
    return recommended_movies, recommended_posters

# List files in current directory to debug file presence
st.write("DEBUG: Files in current directory:", os.listdir("."))

try:
    with open("movies.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    st.write("DEBUG: Loaded movies.pkl successfully.")
except Exception as e:
    st.error(f"ERROR loading movies.pkl: {e}")
    st.stop()

try:
    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)
    st.write("DEBUG: Loaded similarity.pkl successfully.")
except Exception as e:
    st.error(f"ERROR loading similarity.pkl: {e}")
    st.stop()

movies = pd.DataFrame(movies_dict)
st.write(f"DEBUG: Movies dataframe loaded with {len(movies)} entries.")

st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox("🔍 Select a movie:", movies["title"].values)

if st.button("Recommend"):
    st.write(f"DEBUG: Recommend button clicked for movie: {selected_movie_name}")
    with st.spinner("Fetching recommendations..."):
        try:
            recommendations, posters = recommend(selected_movie_name, movies, similarity)
            st.write(f"DEBUG: Recommendations: {recommendations}")
        except Exception as e:
            st.error(f"ERROR during recommendation: {e}")
            recommendations, posters = [], []

    if recommendations:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], caption=recommendations[i], use_container_width=True)
    else:
        st.error("No recommendations found! Please select a valid movie.")
