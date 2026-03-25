import streamlit as st
import pandas as pd 
import altair as alt

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="Netflix Insights",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Customizing the metric styling slightly via markdown
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 2.5rem;
    color: #E50914;
}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADING & CLEANING ---
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    df.drop_duplicates(inplace=True)

    # --- 🛠️ NEW FIX: Fix misplaced durations in the rating column ---
    misplaced = df['rating'].astype(str).str.contains('min|Season', case=False, na=False)
    df.loc[misplaced, 'duration'] = df.loc[misplaced, 'rating']
    df.loc[misplaced, 'rating'] = 'Unknown'
    # ----------------------------------------------------------------
    
    # Clean up missing values
    df.fillna({
        'director': 'Unknown', 
        'country': 'Unknown', 
        'cast': 'Unknown', 
        'rating': 'Unknown'
    }, inplace=True)
    
    # Process dates
    df["date_added"] = pd.to_datetime(df["date_added"], errors='coerce') 
    df.dropna(subset=['date_added'], inplace=True) 
    df["year_added"] = df["date_added"].dt.year.astype(int)
    
    # Process lists (explode ready)
    df['listed_in'] = df['listed_in'].astype(str).str.split(', ')
    df['country'] = df['country'].astype(str).str.split(', ')
    df['cast'] = df['cast'].astype(str).str.split(', ')
    
    return df

df = load_data()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", width=150)
st.sidebar.markdown("---")
st.sidebar.header("Filters ⚙️")

search = st.sidebar.text_input("🔍 Search for a Title, Director, or Actor")
type_filter = st.sidebar.multiselect("Content Type", df['type'].unique(), default=df['type'].unique())

min_year = int(df['year_added'].min())
max_year = int(df['year_added'].max())
year_filter = st.sidebar.slider("Year Added to Netflix", min_year, max_year, (min_year, max_year))

# Apply Filters
filtered_df = df[
    (df['type'].isin(type_filter)) &
    (df['year_added'].between(year_filter[0], year_filter[1]))
]

if search:
    mask = (
        filtered_df['title'].str.contains(search, case=False, na=False) |
        filtered_df['director'].str.contains(search, case=False, na=False) |
        filtered_df['cast'].astype(str).str.contains(search, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

# --- 4. HEADER & METRICS ---
st.title("🍿 Netflix Global Content Dashboard")
st.markdown("A deep dive into the Netflix catalog, trends, genres, and cast distributions.")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Titles", value=f"{len(filtered_df):,}")
with col2:
    st.metric(label="Movies 🎬", value=f"{len(filtered_df[filtered_df['type'] == 'Movie']):,}")
with col3:
    st.metric(label="TV Shows 📺", value=f"{len(filtered_df[filtered_df['type'] == 'TV Show']):,}")

st.divider()

# --- 5. CHARTS ROW 1: GENRES & COUNTRIES ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Top 10 Genres")
    genres = filtered_df.explode('listed_in')
    top_genres = genres['listed_in'].value_counts().head(10).reset_index()
    top_genres.columns = ['Genre', 'Count']
    
    genre_chart = alt.Chart(top_genres).mark_bar(color='#E50914').encode(
        x=alt.X('Count:Q', title=''),
        y=alt.Y('Genre:N', sort='-x', title=''),
        tooltip=['Genre', 'Count']
    ).properties(height=320)
    st.altair_chart(genre_chart, use_container_width=True)

with col_right:
    st.subheader("Top 10 Countries")
    countries = filtered_df.explode('country')
    top_countries = countries[countries['country'] != 'Unknown']['country'].value_counts().head(10).reset_index()
    top_countries.columns = ['Country', 'Count']
    
    # Swapped to Steel Blue
    country_chart = alt.Chart(top_countries).mark_bar(color='#4A90E2').encode(
        x=alt.X('Count:Q', title=''),
        y=alt.Y('Country:N', sort='-x', title=''),
        tooltip=['Country', 'Count']
    ).properties(height=320)
    st.altair_chart(country_chart, use_container_width=True)

st.write("") 

# --- 6. CHARTS ROW 2: OVER TIME & CONTENT MIX ---
col_bottom_left, col_bottom_right = st.columns([2, 1])

with col_bottom_left:
    st.subheader("Content Added Over Time")
    year_data = filtered_df['year_added'].value_counts().sort_index().reset_index()
    year_data.columns = ['Year', 'Count']

    line_chart = alt.Chart(year_data).mark_area(
        line={'color': '#E50914'}, 
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color='#E50914', offset=0), 
                   alt.GradientStop(color='white', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('Year:O', title='Year Added'),  
        y=alt.Y('Count:Q', title='Number of Titles Added'),
        tooltip=['Year', 'Count']
    ).properties(height=320)
    st.altair_chart(line_chart, use_container_width=True)

with col_bottom_right:
    st.subheader("Content Mix")
    type_counts = filtered_df['type'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']

    donut_chart = alt.Chart(type_counts).mark_arc(innerRadius=65).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(
            field="Type", 
            type="nominal", 
            # Swapped secondary color to Steel Blue
            scale=alt.Scale(domain=['Movie', 'TV Show'], range=['#E50914', '#4A90E2']),
            legend=alt.Legend(title=None, orient="bottom", labelFontSize=14) 
        ),
        tooltip=['Type', 'Count']
    ).properties(height=320)
    st.altair_chart(donut_chart, use_container_width=True)

st.write("") 

# --- 7. CHARTS ROW 3: ACTORS & MATURITY RATINGS ---
col_act, col_rat = st.columns(2)

with col_act:
    st.subheader("Most Featured Actors")
    actors = filtered_df.explode('cast')
    top_actors = actors[actors['cast'] != 'Unknown']['cast'].value_counts().head(10).reset_index()
    top_actors.columns = ['Actor', 'Count']

    # Swapped to Steel Blue
    actor_chart = alt.Chart(top_actors).mark_bar(color='#4A90E2').encode(
        x=alt.X('Count:Q', title=''),
        y=alt.Y('Actor:N', sort='-x', title=''),
        tooltip=['Actor', 'Count']
    ).properties(height=320)
    st.altair_chart(actor_chart, use_container_width=True)

with col_rat:
    st.subheader("Maturity Ratings Distribution")
    rating_counts = filtered_df[filtered_df['rating'] != 'Unknown']['rating'].value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']

    rating_chart = alt.Chart(rating_counts).mark_bar(color='#E50914').encode(
        x=alt.X('Rating:N', sort='-y', title='', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Count:Q', title=''),
        tooltip=['Rating', 'Count']
    ).properties(height=320)
    st.altair_chart(rating_chart, use_container_width=True)

st.write("") 

# --- 8. CHART ROW 4: MOVIE DURATION HISTOGRAM ---
st.subheader("Movie Duration Distribution")
movies_df = filtered_df[filtered_df['type'] == 'Movie'].copy()
movies_df = movies_df.dropna(subset=['duration'])
movies_df['duration_mins'] = movies_df['duration'].astype(str).str.extract(r'(\d+)').astype(float)

duration_chart = alt.Chart(movies_df).mark_bar(color='#b20710', opacity=0.8).encode(
    x=alt.X('duration_mins:Q', bin=alt.Bin(maxbins=40), title='Duration (Minutes)'),
    y=alt.Y('count():Q', title='Number of Movies'),
    tooltip=[alt.Tooltip('count()', title='Movies in this range')]
).properties(height=350)
st.altair_chart(duration_chart, use_container_width=True)

# --- 9. RAW DATA TABLE ---
st.divider()
with st.expander("📂 View Raw Data Table"):
    st.dataframe(filtered_df.drop(columns=['duration_mins'], errors='ignore'), use_container_width=True)