"""
Imagina que esta API es una biblioteca de películas:
La función load_movies es como un bibliotecario que carga el catálogo de libros (películas) cuando se abre la biblioteca.
La función get_movies muestra todo el catálogo cuando alguien lo pide.
La función get_movies(id) es como si alguien preguntara por un libro específico, es decir por su código de identificación.
La función chatbot(query) es un asistente que busca libros según palabras clave y sinónimo.
La función get_movies_by_category (category) ayuda a encontrar películas según su género (acción, comedia, etc.)
"""

# Importamos las herramientas necesarias para construir nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse sirve para páginas web, JSONResponse para respuestas en formato JSON.
import pandas as pd # Pandas nos ayuda a manejar datos en tablas como si fuera un Excel.
import nltk # NLTK es una librería para procesar texto y analizar palabras.
from nltk.tokenize import word_tokenize # Se usa para dividir un texto en palabras individuales.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinónimos de palabras.
from fastapi.middleware.cors import CORSMiddleware # Permite que nuestra API sea accedida desde otras aplicaciones web (como React, Angular, etc.)

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador

# Descargar recursos necesarios de NLTK
nltk.download('punkt', quiet=True) # Paquete para dividir frases en palabras.
nltk.download('wordnet', quiet=True) # Paquete para encontrar sinónimos de palabras en inglés.

# Función para cargar las películas desde un archivo CSV
def load_movies():
    #Leemos el archivo que contiene información de películas y seleccionamos las columnas más importantes.
    df = pd.read_csv(r"./Dataset/netflix_titles.csv")[['show_id','title','release_year','listed_in','rating','description']]
    
    # Renombramos las columnas para que sean más fáciles de entender.
    df.columns = ['id','title','year','category','rating','overview']
    
    # Llenamos los espacios vacios con un texto vacio y convertimos los datos en diccionarios.
    return df.fillna('').to_dict(orient='records')

# Cargamos las películas al iniciar la API, para no leer el archivo cada vez que alguien pregunte por ellas.
movies_list = load_movies()

#Función para encontrar sinónimos de una palabra.

def get_synonyms(word):
    # Usamos wordnet para obtener distintas palabras que significan lo mismo.
    # Esta función devuelve un conjunto de sinónimos en minúsculas.
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicación FastAPI, que será el motor de nuestra API.
# Esto inicializa la API con un nombre y una versión.
app = FastAPI(title='Mi aplicación de películas By Miguel', version='1.0.0')


# Configuramos CORS para aceptar solicitudes desde cualquier origen (útil para frontend separado)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # El * significa que acepta peticiones desde cualquier dominio (no recomendado en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de inicio: Cuando alguien entra a la API sin especificar nada, verá un mensaje de bienvenida.
@app.get('/', tags=['Home'])
def home():
    # Cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida.
    return HTMLResponse('<h1> Bienvenido a la API de películas </h1>') # h1 hace referencia para los títulos más grandes

# Obteniendo la lista de películas
# Creamos una ruta para obtener todas las películas

# Ruta para obtener todas las películas disponibles.

@app.get('/movies', tags=['Movies'])
def get_all_movies():
    # Si hay películas, las enviamos, si no, mostramos un error.
    if movies_list:
        return movies_list
    raise HTTPException(status_code=500, detail="No hay datos de películas disponibles")

#Ruta para obtener una película específica por su ID
@app.get('/movies/{id}', tags=['Movies'])
def get_movie(id: str):
    #Buscamos en la lista de películas la que tenga el mismo ID
    movie = next((m for m in movies_list if m['id'] == id), None) # next devuelve el primer resultado que coincida, o None si no hay
    if movie:
        return movie
    raise HTTPException(status_code=404, detail="Película no encontrada")

# Ruta del chatbot que responde con películas según palabras clave de la categoría
@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    #Dividimos la consulta en palabras clave, para entender mejor la intención del usuario
    query_words = word_tokenize(query.lower()) # Convierte una frase como "quiero acción y comedia" en ['quiero', 'acción', 'y', 'comedia']
    
    #Buscamos sinónimos de las palabras clave para ampliar la búsqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
    
    # Filtramos la lista de películas buscando coincidencias en la categoría
    results = [m for m in movies_list if any(s in m['category'].lower() for s in synonyms)]
    
    #Si encontramos películas, enviamos la lista; si no, mostramos un mensaje de que no se encontraron coincidencias.
    return JSONResponse(content={
        "respuesta": "Aquí tienes algunas películas relacionadas." if results else "No encontré películas en esa categoría.",
        "peliculas": results
    })

# Ruta para busca películas por categoría específica

@app.get('/movies/', tags=['Movies'])
def get_movies_by_category(category: str):
    # Filtramos la lista de películas según la categoría ingresada.
    # Por ejemplo: si se busca "comedy", devolverá todas las películas que incluyan esa palabra en la categoría.
    results = [m for m in movies_list if category.lower() in m['category'].lower()]
    return results
