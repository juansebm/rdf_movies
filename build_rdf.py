import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

df = pd.read_csv('netflix_imdb_movies.csv')
schema = Namespace('http://schema.org/')
ex = Namespace('http://example.org/netflix/')
g = Graph()
g.bind('schema', schema)
g.bind('ex', ex)

for row in df.to_dict('records'):
    movie = ex[row['show_id']]
    g.add((movie, RDF.type, schema.Movie))
    g.add((movie, schema.name, Literal(row['title'])))
    if isinstance(row['country'], str):
        for country in [c.strip() for c in row['country'].split(',') if c.strip()]:
            g.add((movie, schema.countryOfOrigin, Literal(country)))
    if isinstance(row['listed_in'], str):
        for genre in [c.strip() for c in row['listed_in'].split(',') if c.strip()]:
            g.add((movie, schema.genre, Literal(genre)))
    if isinstance(row['date_added'], str):
        g.add((movie, schema.dateAdded, Literal(row['date_added'])))
    if not pd.isna(row['release_year']):
        g.add((movie, schema.datePublished, Literal(int(row['release_year']), datatype=XSD.gYear)))
    if isinstance(row['rating'], str):
        g.add((movie, schema.contentRating, Literal(row['rating'])))
    if isinstance(row['duration'], str) and row['duration'].endswith(' min'):
        minutes = row['duration'].split(' ')[0]
        if minutes.isdigit():
            g.add((movie, schema.duration, Literal(f'PT{minutes}M')))
    if isinstance(row.get('averageRating'), (int, float)) and pd.notna(row['averageRating']):
        g.add((movie, schema.ratingValue, Literal(row['averageRating'], datatype=XSD.decimal)))
    if isinstance(row.get('tconst'), str):
        g.add((movie, schema.sameAs, URIRef(f'https://www.imdb.com/title/{row["tconst"]}/')))

g.serialize('netflix_imdb_movies.ttl', format='turtle')





