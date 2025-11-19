import pandas as pd
from rich.progress import Progress

with Progress(transient=True) as progress:
    task = progress.add_task('', total=5)
    # Leer Netflix y filtrar solo películas
    netflix = pd.read_csv('netflix_titles.csv')
    movies = netflix[netflix['type'].eq('Movie')]
    progress.advance(task)
    
    # Leer IMDb basics y filtrar solo películas (titleType == 'movie')
    basics = pd.read_csv('title.basics.tsv', sep='\t', dtype=str, na_values='\\N', 
                        usecols=['tconst', 'titleType', 'primaryTitle', 'startYear'])
    basics = basics[basics['titleType'].eq('movie')]
    # Convertir startYear a numérico (puede tener '\\N' para valores faltantes)
    basics['startYear'] = pd.to_numeric(basics['startYear'], errors='coerce')
    progress.advance(task)
    
    # Leer ratings
    ratings = pd.read_csv('title.ratings.tsv', sep='\t', dtype={'tconst': str}, na_values='\\N', 
                         usecols=['tconst', 'averageRating'])
    progress.advance(task)
    
    # Convertir release_year a numérico para el merge
    movies['release_year'] = pd.to_numeric(movies['release_year'], errors='coerce')
    
    # Merge por título Y año
    merged = movies.merge(basics, 
                          left_on=['title', 'release_year'], 
                          right_on=['primaryTitle', 'startYear'],
                          how='inner')
    merged = merged.merge(ratings, on='tconst', how='left')
    merged = merged.drop_duplicates(subset='show_id')
    merged = merged.replace(r'^\s*$', pd.NA, regex=True)
    merged = merged.dropna(subset=['show_id', 'title', 'tconst', 'averageRating'])
    progress.advance(task)
    
    cols = [columna for columna in movies.columns if columna != 'description']
    merged[cols + ['tconst', 'averageRating']].to_csv('netflix_imdb_movies.csv', index=False)
    progress.advance(task)

