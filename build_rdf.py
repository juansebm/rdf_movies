import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, XSD
from datetime import date
from decimal import Decimal, InvalidOperation

df = pd.read_csv('netflix_imdb_movies.csv')
df = df[df['release_year'] == 2021]
df = df.sort_values('averageRating', ascending=False).head(40)
base_uri = 'http://raw.githubusercontent.com/juansebm/rdf_movies/main/netflix_imdb_movies.ttl'
netflix_ns = Namespace(f'{base_uri}#')
schema = Namespace('http://schema.org/')
social = Namespace('http://raw.githubusercontent.com/juansebm/lab10_webofdata/main/social.ttl#')

g = Graph(base=base_uri)
g.bind('rdf', RDF, override=True, replace=True)
g.bind('rdfs', RDFS, override=True, replace=True)
g.bind('foaf', FOAF, override=True, replace=True)
g.bind('dc', DCTERMS, override=True, replace=True)
g.bind('xsd', XSD, override=True, replace=True)
g.bind('schema1', schema, override=True, replace=True)
g.bind('social', social, override=True, replace=True)
g.bind('netflix', netflix_ns, override=True, replace=True)

document = URIRef(base_uri)
catalog = URIRef(f'{base_uri}#catalog')
g.add((document, RDF.type, FOAF.Document))
g.add((document, DCTERMS.date, Literal(date.today(), datatype=XSD.date)))
g.add((document, DCTERMS.title, Literal("Netflix & IMDb Movies dataset", lang='en')))
g.add((document, FOAF.primaryTopic, catalog))
g.add((document, DCTERMS.creator, catalog))
g.add((catalog, RDF.type, schema.Dataset))
g.add((catalog, RDFS.label, Literal("Netflix & IMDb Movies", lang='en')))
g.add((catalog, DCTERMS.description, Literal("Dataset linking Netflix titles with IMDb identifiers and ratings.", lang='en')))

for row in df.to_dict('records'):
    movie = netflix_ns[row['show_id']]
    g.add((catalog, schema.hasPart, movie))
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
            g.add((movie, schema.duration, Literal(f'PT{minutes}M', datatype=XSD.duration)))
    rating = row.get('averageRating')
    if pd.notna(rating):
        try:
            rating_value = Decimal(str(rating))
        except (InvalidOperation, TypeError, ValueError):
            rating_value = None
        if rating_value is not None:
            g.add((movie, schema.ratingValue, Literal(rating_value, datatype=XSD.decimal)))
    if isinstance(row.get('tconst'), str):
        g.add((movie, schema.sameAs, URIRef(f'https://www.imdb.com/title/{row["tconst"]}/')))

g.serialize('netflix_imdb_movies.ttl', format='turtle')





