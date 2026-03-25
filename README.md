# Netflix Dashboard Streamlit

An interactive data dashboard built with Streamlit to explore the Netflix titles dataset. The app helps analyze content trends, genres, countries, ratings, cast presence, and movie duration distributions with filters and charts.

## Project Overview

This project reads `netflix_titles.csv`, cleans and transforms the data, and presents a visual analytics dashboard.

Main goals:
- Explore Netflix catalog patterns quickly.
- Filter by content type and year range.
- Search titles, directors, and cast.
- Visualize trends with Altair charts.

## Features

- Data cleaning pipeline with cached loading for faster app performance.
- Fix for misplaced values where duration text appears in the `rating` column.
- Sidebar filters:
	- Search text input.
	- Content type multiselect.
	- Year-added range slider.
- Dashboard visuals:
	- Top genres.
	- Top countries.
	- Content added over time.
	- Movie vs TV Show mix (donut chart).
	- Most featured actors.
	- Maturity rating distribution.
	- Movie duration histogram.
- Expandable raw data table view.

## Tech Stack

- Python
- Streamlit
- Pandas
- Altair

## Dataset

- File: `netflix_titles.csv`
- Contains metadata for Netflix titles such as type, title, director, cast, country, date added, release year, rating, duration, and listed genres.

## Project Structure

- `app.py` - Streamlit app entry point and all dashboard logic.
- `netflix_titles.csv` - Source dataset used by the app.
- `README.md` - Project documentation.

## How to Run Locally

1. Clone the repository:

```bash
git clone https://github.com/e-neuro/netflix-dashboard-streamlit.git
cd netflix-dashboard-streamlit
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install streamlit pandas altair
```

4. Run the app:

```bash
streamlit run app.py
```

5. Open the local URL shown in terminal (usually `http://localhost:8501`).

## Future Improvements

- Add requirements file for one-step dependency installation.
- Add deployment instructions (Streamlit Community Cloud).
- Add automated data quality checks.
