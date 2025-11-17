"""
Script para generar directors.ttl con directores de los últimos 30 años.
"""
import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, XSD
from datetime import datetime

# Leer el CSV
df = pd.read_csv('netflix_imdb_movies.csv')

# Filtrar solo películas de los últimos 30 años
current_year = datetime.now().year
start_year = current_year - 30
df = df[df['release_year'] >= start_year]
df = df[df['release_year'] <= current_year]

print(f"Filtrando películas desde {start_year} hasta {current_year}")

# Base URI para directores - apuntar al archivo raw de GitHub
directors_base_uri = 'http://raw.githubusercontent.com/juansebm/rdf_movies/main/directors.ttl'
directors_ns = Namespace(f'{directors_base_uri}#')
schema = Namespace('http://schema.org/')
foaf = Namespace('http://xmlns.com/foaf/0.1/')

# Crear grafo con base URI
g = Graph(base=directors_base_uri)

# Bindings
g.bind('rdf', RDF, override=True, replace=True)
g.bind('rdfs', RDFS, override=True, replace=True)
g.bind('foaf', FOAF, override=True, replace=True)
g.bind('dc', DCTERMS, override=True, replace=True)
g.bind('xsd', XSD, override=True, replace=True)
g.bind('schema', schema, override=True, replace=True)
g.bind('directors', directors_ns, override=True, replace=True)

# Documento
document = URIRef('http://example.org/directors')
g.add((document, RDF.type, FOAF.Document))
g.add((document, DCTERMS.date, Literal(pd.Timestamp.now().date(), datatype=XSD.date)))
g.add((document, DCTERMS.title, Literal("Directors dataset - Last 30 years", lang='en')))
g.add((document, DCTERMS.description, Literal(f"Dataset of movie directors from Netflix & IMDb Movies (years {start_year}-{current_year}).", lang='en')))

# Recopilar todos los directores únicos de los últimos 30 años
directors_set = set()

for row in df.to_dict('records'):
    if isinstance(row.get('director'), str) and pd.notna(row.get('director')):
        for director in [d.strip() for d in row['director'].split(',') if d.strip()]:
            directors_set.add(director)

print(f"Encontrados {len(directors_set)} directores únicos de los últimos 30 años")

# Crear recursos para cada director apuntando al archivo raw de GitHub
for director in sorted(directors_set):
    # Crear nombre seguro para URI
    safe_name = ''.join(c if c.isalnum() or c in ('_', '-') else '_' for c in director)
    
    # URI del director apuntando al archivo raw de GitHub
    director_uri = directors_ns[f"director_{safe_name}"]
    
    # Añadir propiedades del director
    g.add((director_uri, RDF.type, FOAF.Person))
    g.add((director_uri, FOAF.name, Literal(director)))
    g.add((director_uri, RDFS.label, Literal(director)))

# Guardar archivo
g.serialize('directors.ttl', format='turtle')
print(f"Archivo directors.ttl generado con {len(directors_set)} directores")

