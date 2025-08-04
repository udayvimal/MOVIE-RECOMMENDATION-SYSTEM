import streamlit as st
import pickle
import pandas as pd
import requests
import os

# --------- Custom CSS ---------
st.markdown("""
<style>
/* Background Gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: #2c1a60;
    color: #ddd;
    font-weight: 500;
}

/* Title Gradient */
h1 {
    background: -webkit-linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg, #f093fb, #f5576c);
    color: white;
    font-weight: 600;
    border-radius: 8px;
    height: 45px;
    width: 150px;
    transition: background 0.3s ease;
}

.stButton>button:hover {
    background: linear-gradient(45deg, #f5576c, #f093fb);
}

/* Columns card style */
.movie-card {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    box-shadow: 0 8px 32px 0 rgba( 31, 38, 135, 0.37 );
    padding: 10px;
    text-align: center;
    margin-bottom: 15px;
    transition: transform 0.3s ease;
}
.movie-card:hover {
    transform: scale(1.05);
}

/* Poster image rounded corners */
img {
    border-radius: 12px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    transition: transform 0.3s ease;
}
img:hover {
    transform: scale(1.1);
}

/* Footer */
footer {
    text-align:center;
    color: #ddd;
    font-size: 13px;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Page config ----------
st.set_page_config(
    page_title="🎬 Movie Recommender",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="auto",
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🎞️ About This App")
    st.markdown("""
    Welcome to the **Movie Recommender System!**

    🔍 Select a movie from the dropdown  
    🎯 Get 5 personalized movie recommendations  
    🎨 Beautiful posters fetched live from OMDb API  
    """)
    st.markdown("---")
    st.markdown("### 👨‍💻 Developer")
    st.markdown("[Uday Vimal](https://github.com/udayvimal)  \nData Science & ML Enthusiast")
    st.markdown("---")
    with st.expander("📁 Show project files"):
        st.write(os.listdir())

# --------- Load data ---------
@st.cache_data(show_spinner=False)
def load_pickle_file(file_path):
    with open(file_path, "rb") as f:
        return pickle.load(f)

try:
    movies_dict = load_pickle_file("movies.pkl")
    similarity = load_pickle_file("similarity.pkl")
except Exception as e:
    st.error(f"Failed to load data files: {e}")
    st.stop()

movies = pd.DataFrame(movies_dict)

# --------- Functions ---------
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
    except Exception:
        poster_url = "https://via.placeholder.com/200"

    poster_cache[movie_title] = poster_url
    return poster_url

def recommend(movie, movies, similarity):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.warning("⚠️ Movie not found in dataset.")
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return recommended_movies, recommended_posters

# --------- UI ---------
st.markdown("<h1>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:18px; color:#eee;'>Select a movie below and get 5 similar recommendations with stunning posters.</p>", unsafe_allow_html=True)

selected_movie = st.selectbox("🔍 Select a movie:", options=movies["title"].values, help="Start typing to search your favorite movie.")

st.write("")  # spacing

recommend_btn = st.button("Recommend 🎯")

if recommend_btn:
    with st.spinner("Finding best matches..."):
        recs, posters = recommend(selected_movie, movies, similarity)

    if recs:
        st.markdown("---")
        st.subheader("🎥 Your Movie Recommendations")
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            with col:
                # Use markdown with CSS class for nice card effect
                st.markdown(
                    f"""
                    <div class="movie-card">
                        <img src="{posters[idx]}" alt="{recs[idx]}" style="width:100%; height:auto;"/>
                        <h4 style="margin-top:8px; color:#fff;">{recs[idx]}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.warning("No recommendations found. Please try another movie.")

# Footer
st.markdown(
    """
    <footer>
    Developed by <a href="https://github.com/udayvimal" target="_blank" style="color:#f093fb;">Uday Vimal</a> &bull; Powered by Streamlit
    </footer>
    """,
    unsafe_allow_html=True,
)
