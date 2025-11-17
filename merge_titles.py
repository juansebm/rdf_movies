import pandas as pd
from rich.progress import Progress

with Progress(transient=True) as progress:
    task = progress.add_task('', total=4)
    netflix = pd.read_csv('netflix_titles.csv')
    progress.advance(task)
    movies = netflix[netflix['type'].eq('Movie')]
    basics = pd.read_csv('title.basics.tsv', sep='\t', dtype=str, na_values='\\N', usecols=['tconst', 'primaryTitle'])
    progress.advance(task)
    ratings = pd.read_csv('title.ratings.tsv', sep='\t', dtype={'tconst': str}, na_values='\\N', usecols=['tconst', 'averageRating'])
    progress.advance(task)
    merged = movies.merge(basics, left_on='title', right_on='primaryTitle')
    merged = merged.merge(ratings, on='tconst', how='left')
    merged = merged.drop_duplicates(subset='show_id')
    merged = merged.replace(r'^\s*$', pd.NA, regex=True)
    merged = merged.dropna(subset=['show_id', 'title', 'tconst', 'averageRating'])
    cols = [columna for columna in movies.columns if columna != 'description']
    merged[cols + ['tconst', 'averageRating']].to_csv('netflix_imdb_movies.csv', index=False)
    progress.advance(task)

