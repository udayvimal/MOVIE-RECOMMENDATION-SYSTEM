import streamlit as st
import pickle
import pandas as pd
import requests

poster_cache = {}

def fetch_poster(movie_title):
    if movie_title in poster_cache:
        return poster_cache[movie_title]
    
    api_key = "63dfac01"
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        poster_url = data.get("Poster", "https://via.placeholder.com/200")
        st.write(f"Fetched poster for {movie_title}")
    except Exception as e:
        st.write(f"Error fetching poster for {movie_title}: {e}")
        poster_url = "https://via.placeholder.com/200"
    
    poster_cache[movie_title] = poster_url
    return poster_url

def recommend(movie, movies, similarity):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Selected movie not found in database.")
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        poster = fetch_poster(movie_title)
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

with open("movies.pkl", "rb") as f:
    movies_dict = pickle.load(f)

with open("similarity.pkl", "rb") as f:
    similarity = pickle.load(f)

movies = pd.DataFrame(movies_dict)

st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox("🔍 Select a movie:", movies["title"].values)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        recommendations, posters = recommend(selected_movie_name, movies, similarity)
    
    if recommendations:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i], caption=recommendations[i], use_container_width=True)
    else:
        st.error("No recommendations found! Please select a valid movie.")
