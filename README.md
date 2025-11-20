# RDF Movies proyect

En el siguiente repositorio, lo que intentamos hacer es unir dos bases de datos para crear consultas a partir de grafos rdfs: Netflix y IMdB. 

El flujo del trabajo consiste en ejecutar tres scripts de python, que se ejecutan luego de descargar las bases de datos desde Kaggle tanto de [Netflix](https://www.kaggle.com/datasets/shivamb/netflix-shows) como [ImDB](https://www.kaggle.com/datasets/ashirwadsangwan/imdb-dataset). Los conjuntos de datos son tales que nteflix contiene un único archivo .csv, mientras que IMDb contiene múltiples archivos TSV, que queremos convertir en un único archivo .csv.

Como parte del proceso Extract-Load-Transform (ETL), el proyecto utiliza tres fuentes principales:

1. netflix_titles.csv
- Catálogo de títulos de Netflix
- Incluye: título, director, país, género, año, duración, rating
2. title.basics.tsv
- Datos básicos de IMDb
- Identificadores únicos (tconst) y títulos primarios
3. title.ratings.tsv
- Ratings de IMDb
- Promedio de calificaciones (averageRating)

Códigos de Python:

1. El archivo ´merge_titles.py´ crea ´netflix_imdb_movies.csv´ a partir de ´title.ratings.tsv´, ´title.basics.tsv´ y ´netflix_titles.csv´. Más específicamente este script:
- Lee netflix_titles.csv y filtra solo películas (no series)
- Combina con title.basics.tsv usando el título como clave
- Añade ratings de title.ratings.tsv usando tconst
- Elimina duplicados y datos incompletos
- Genera: netflix_imdb_movies.csv
Resultado: Un CSV unificado con datos de Netflix + IMDb (4013 filas de datos x 13 features)

2. El archivo ´build_rdf.py´ crea ´netflix_imdb_movies.ttl´ a partir de ´netflix_imdb_movies.csv´. Más específicamente, este script:
Este script:
- Lee netflix_imdb_movies.csv
- Filtra películas de los últimos 30 años
- Extrae todos los directores únicos
- Crea recursos RDF para cada director usando FOAF
- Genera: directors.ttl
Donde cada director tiene:
- Tipo: foaf:Person
- Nombre: foaf:name
- URI única y persistente

3. El archivo ´build_directors.py´ crea directors.ttl a partir de ´netflix_imdb_movies.csv´. Este script:
- Lee netflix_imdb_movies.csv
- Filtra películas con rating válido
- Selecciona la mejor película de cada año (últimos 30 años)
- Crea recursos RDF usando múltiples vocabularios Schema.org (Movie, ratingValue, datePublished, etc.) Dublin Core (DCTERMS) para metadatos, FOAF para personas, RDFS para etiquetas
- Enlaza con directores del archivo directors.ttl
- Genera: netflix_imdb_movies.ttl

El proyecto utiliza los siguientes estándares de la Web Semántica:
1. SCHEMA.ORG:
- schema:Movie, schema:director, schema:ratingValue
- schema:datePublished, schema:genre,
schema:countryOfOrigin
2. DUBLIN CORE (DCTERMS):
- dc:title, dc:date, dc:subject, dc:coverage
- Para metadatos descriptivos
3. FOAF (Friend of a Friend):
- foaf:Person, foaf:name
- Para representar directores
4. RDFS:
- rdfs:label, rdfs:seeAlso
- Para etiquetas y referencias

Cada película en el RDF contiene tripletas que contienen:
- Título (rdfs:label, dc:title)
- Director(es) - enlace a recursos en directors.ttl
- País(es) de origen (dc:coverage, schema:countryOfOrigin)
- Géneros (dc:subject, schema:genre)
- Año de publicación (dc:issued, schema:datePublished)
- Rating de IMDb (schema:ratingValue)
- Duración (schema:duration en formato ISO 8601)
- Clasificación de contenido (schema:contentRating)
- Enlace a IMDb (rdfs:seeAlso, schema:sameAs)

Se generaron 13 consultas usando el lenguaje de consulta Sparql. SPARQL no es un lenguaje de programación en el sentido tradicional, sino un lenguaje de consulta diseñado específicamente para consultar bases de datos que utilizan el modelo de datos RDF (Resource Description Framework). Estas consultas se pueden ver o bien como tablas o bien como grafos en la referencia de la [Universidad de Chile](https://rdfplayground.dcc.uchile.cl) Las consultas que hicimos están en el archivo ´sparql_queries.rq´, y son las siguientes: 

1. Las top 5 películas con mejor rating.
2. Los países que producen más películas.
3. Los géneros más comunes para las películas.
4. Películas de más de dos horas con rating mayor a 8.5.
5. Películas posteriores a 2020 con rating mayor a 8.0.
6. Las películas que son coproducciones, es decir, producciones de múltiples países.
7. Rating promedio por década.
8. Las películas con más de 3 géneros y rating mayor o igual a 8.0.
9. Los mejores documentales, que al fin y al cabo son clasificados como películas.
10. Directores que se repiten.
11. Películas con sus directores y rating mayor o igual a 8.5.
12. Directores con mejor rating promedio.
13. Análisis de directores por década.

Los resultados de nuestro proyecto son los siguientes. En primer lugar, logramos transformar datos tabulares a RDF, implementando el uso de vocabularios estándar (Schema.org, Dublin Core, FOAF, etc), haciendo consultas con el lenguaje Sparql, y por último logramos la separación de datos relacionados (películas vs directores).

Otra ventaja de este trabajo es que podemos hacer análisis de tendencias cinematográficas, integración con otros datasets de la web, o bien la creación de APIs semánticas para aplicaciones web. 
Como conclusiones, podemos decir que este proyecto puede servir como una forma complementaria de aportar a un sistema de recomendación de películas. 

Por otro lado, esta combinación de conjuntos de datos tiene
la desventaja de que es algo incompleto, porque si hacemos una revisión de algunas de las películas más conocidas (como lo son The Revenant o Blade Runner 2049), estas no están. Esto quiere decir que o bien Netflix, o bien ImDB no contienen muchas películas y/o documentales. Para mitigar este defecto, podríamos crear un web scrapper para complementar nuestro dataset con otros que estén disponibles en internet y que sean más extensos abarcando más películas.
Por otro lado, es notable que la mayoría de las películas provengan de estados unidos, lo cual evidencia el sesgo de la fuente de dichos datos (plataformas que son en inglés principalmente).

Como detalles más técnicos, utilizamos ambientes virtuales para poder instalar las librerías o dependencias necesarias, que se encuentran en el archivo requirements.txt. El uso de ambientes virtuales tiene la ventaja de permitirnos aislar el proyecto y por ende poder reutilizarlo sin confundirnos con librerías, manteniendo el peso del proyecto óptimo en caso de que quisiéramos hacer despliegue de alguna aplicación relacionada al mismo.

Creación de ambiente virtual:
python3 -m venv .venv

Activación del ambiente virtual:
source .venv/bin/activate

Instalar las dependencias: 
pip install -r requirements.txt

Actualizar el archivo con las dependencias instaladas:
pip freeze > requirements.txt

Para desactivar el ambiente virtual:
deactivate

Por último, dejamos un pequeño esquema que resume el flujo de los archivos:
```
netflix_titles.csv
        │
        ▼
 title.basics.tsv → merge_titles.py → netflix_imdb_movies.csv
        ▲
        │
 title.ratings.tsv
```
