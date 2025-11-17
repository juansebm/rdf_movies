import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, XSD
from datetime import date
from decimal import Decimal, InvalidOperation

df = pd.read_csv('netflix_imdb_movies.csv')
# Filtrar solo películas con rating válido
df = df[df['averageRating'].notna()]
# Agrupar por año y tomar la mejor película de cada año
df = df.loc[df.groupby('release_year')['averageRating'].idxmax()]
# Ordenar por año descendente y tomar los 30 años más recientes
df = df.sort_values('release_year', ascending=False).head(30)
base_uri = 'http://raw.githubusercontent.com/juansebm/rdf_movies/main/netflix_imdb_movies.ttl'
netflix_ns = Namespace(f'{base_uri}#')
# Usar el mismo namespace que build_directors.py (apunta al archivo raw de GitHub)
directors_base_uri = 'http://raw.githubusercontent.com/juansebm/rdf_movies/main/directors.ttl'
directors_ns = Namespace(f'{directors_base_uri}#')
schema = Namespace('http://schema.org/')
social = Namespace('http://raw.githubusercontent.com/juansebm/lab10_webofdata/main/social.ttl#')

g = Graph(base=base_uri)
# Ya no generamos g_directors aquí, se hace en build_directors.py

# Bindings para el grafo principal
g.bind('rdf', RDF, override=True, replace=True)
g.bind('rdfs', RDFS, override=True, replace=True)
g.bind('foaf', FOAF, override=True, replace=True)
g.bind('dc', DCTERMS, override=True, replace=True)
g.bind('xsd', XSD, override=True, replace=True)
g.bind('schema', schema, override=True, replace=True)
g.bind('social', social, override=True, replace=True)
g.bind('netflix', netflix_ns, override=True, replace=True)
g.bind('directors', directors_ns, override=True, replace=True)

# Los directores se generan en build_directors.py

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
    # Usar rdfs:label en lugar de schema:name
    g.add((movie, RDFS.label, Literal(row['title'])))
    # También dc:title para compatibilidad
    g.add((movie, DCTERMS.title, Literal(row['title'])))
    
    # Director(es) - referenciando desde directors.ttl (generado por build_directors.py)
    if isinstance(row.get('director'), str) and pd.notna(row.get('director')):
        for director in [d.strip() for d in row['director'].split(',') if d.strip()]:
            # Crear nombre seguro para URI (igual que en build_directors.py)
            safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in director)
            # URI del director apuntando al archivo raw de GitHub
            director_uri = directors_ns[f"director_{safe_name}"]
            # Relación con la película usando schema:director
            g.add((movie, schema.director, director_uri))
    
    # País(es) - usar dc:coverage
    if isinstance(row['country'], str):
        for country in [c.strip() for c in row['country'].split(',') if c.strip()]:
            g.add((movie, DCTERMS.coverage, Literal(country)))
            # También mantener schema:countryOfOrigin
            g.add((movie, schema.countryOfOrigin, Literal(country)))
    
    # Géneros - usar dc:subject
    if isinstance(row['listed_in'], str):
        for genre in [c.strip() for c in row['listed_in'].split(',') if c.strip()]:
            g.add((movie, DCTERMS.subject, Literal(genre)))
            # También mantener schema:genre
            g.add((movie, schema.genre, Literal(genre)))
    
    # Fecha añadida - usar dc:date
    if isinstance(row['date_added'], str):
        g.add((movie, DCTERMS.date, Literal(row['date_added'])))
    
    # Año de publicación - usar dcterms:issued
    if not pd.isna(row['release_year']):
        g.add((movie, DCTERMS.issued, Literal(int(row['release_year']), datatype=XSD.gYear)))
        # También mantener schema:datePublished
        g.add((movie, schema.datePublished, Literal(int(row['release_year']), datatype=XSD.gYear)))
    
    # Clasificación de contenido - mantener schema
    if isinstance(row['rating'], str):
        g.add((movie, schema.contentRating, Literal(row['rating'])))
    
    # Duración - mantener schema
    if isinstance(row['duration'], str) and row['duration'].endswith(' min'):
        minutes = row['duration'].split(' ')[0]
        if minutes.isdigit():
            g.add((movie, schema.duration, Literal(f'PT{minutes}M', datatype=XSD.duration)))
    
    # Rating - mantener schema
    rating = row.get('averageRating')
    if pd.notna(rating):
        try:
            rating_value = Decimal(str(rating))
        except (InvalidOperation, TypeError, ValueError):
            rating_value = None
        if rating_value is not None:
            g.add((movie, schema.ratingValue, Literal(rating_value, datatype=XSD.decimal)))
    
    # Enlace a IMDb - usar rdfs:seeAlso
    if isinstance(row.get('tconst'), str):
        imdb_uri = URIRef(f'https://www.imdb.com/title/{row["tconst"]}/')
        g.add((movie, RDFS.seeAlso, imdb_uri))
        # También mantener schema:sameAs
        g.add((movie, schema.sameAs, imdb_uri))

# Guardar películas
g.serialize('netflix_imdb_movies.ttl', format='turtle')
print("Archivo netflix_imdb_movies.ttl generado")





