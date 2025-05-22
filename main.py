from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet
from fastapi.middleware.cors import CORSMiddleware

# Descargar recursos necesarios de NLTK
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

def load_movies():
    df = pd.read_csv(r"./Dataset/netflix_titles.csv")[['show_id','title','release_year','listed_in','rating','description']]
    df.columns = ['id','title','year','category','rating','overview']
    return df.fillna('').to_dict(orient='records')

movies_list = load_movies()

def get_synonyms(word):
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

app = FastAPI(title='Mi aplicación de películas', version='1.0.0')

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', tags=['Home'])
def home():
    return HTMLResponse('<h1> Bienvenido a la API de películas </h1>')

@app.get('/movies', tags=['Movies'])
def get_all_movies():
    if movies_list:
        return movies_list
    raise HTTPException(status_code=500, detail="No hay datos de películas disponibles")

@app.get('/movies/{id}', tags=['Movies'])
def get_movie(id: str):
    movie = next((m for m in movies_list if m['id'] == id), None)
    if movie:
        return movie
    raise HTTPException(status_code=404, detail="Película no encontrada")

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    query_words = word_tokenize(query.lower())
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
    results = [m for m in movies_list if any(s in m['category'].lower() for s in synonyms)]
    return JSONResponse(content={
        "respuesta": "Aquí tienes algunas películas relacionadas." if results else "No encontré películas en esa categoría.",
        "peliculas": results
    })

@app.get('/movies/', tags=['Movies'])
def get_movies_by_category(category: str):
    results = [m for m in movies_list if category.lower() in m['category'].lower()]
    return results
