import streamlit as st
import requests
import openai
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings

# Configurer la page Streamlit
st.set_page_config(page_title="Générateur de Poèmes RAG", layout="wide")

# URL de l'API PoetryDB
POETRYDB_API = "https://poetrydb.org"

# Récupérer la clé API de l'utilisateur
api_key = st.text_input("Entrez votre clé API OpenAI :", type="password")

# Configurer OpenAI avec la clé API fournie
if api_key:
    openai.api_key = api_key

# Fonction pour récupérer des poèmes via PoetryDB
def fetch_poems_from_api(theme):
    try:
        response = requests.get(f"{POETRYDB_API}/lines/{theme}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Erreur lors de la récupération des poèmes : {str(e)}")
        return None

# Fonction pour générer des embeddings et les stocker dans Chroma
def create_vector_store(poems):
    embeddings_model = OpenAIEmbeddings()  # Utilise les embeddings OpenAI
    texts = [poem['lines'][0] for poem in poems]  # Utilisation de la première ligne
    embeddings = embeddings_model.embed_documents(texts)

    # Initialiser Chroma comme magasin de vecteurs
    vector_store = Chroma.from_texts(texts, embeddings)
    return vector_store

# Fonction pour récupérer des poèmes similaires
def retrieve_similar_poems(user_input, vector_store):
    user_embedding = OpenAIEmbeddings().embed_query(user_input)
    similar_poems = vector_store.similarity_search(user_input, k=5)
    return similar_poems

# Fonction pour générer un nouveau poème inspiré des poèmes récupérés
def generate_poem(theme, length, style, similar_poems):
    poem_texts = "\n\n".join([p['lines'][0] for p in similar_poems])

    # Utiliser le modèle ChatCompletion pour générer un nouveau poème
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": "You are a poet."},
            {"role": "user", "content": f"Créez un poème sur le thème '{theme}' en style {style}, et d'une longueur {length} lignes. Utilisez ces poèmes comme source d'inspiration : {poem_texts}"}
        ],
        max_tokens=200
    )
    return response['choices'][0]['message']['content'].strip()

# Interface utilisateur pour entrer les paramètres du poème
st.sidebar.title("Personnalisez votre poème")
theme = st.text_input("Thème (ex : amour, nature, mélancolie)")
length = st.selectbox("Longueur", ["court", "moyen", "long"])
style = st.selectbox("Style", ["vers libres", "sonnet", "haïku", "limerick"])

if st.button("Générer un poème") and api_key:
    with st.spinner("Récupération des poèmes et génération de votre poème personnalisé..."):
        poems = fetch_poems_from_api(theme)
        if poems:
            vector_store = create_vector_store(poems)
            similar_poems = retrieve_similar_poems(theme, vector_store)
            generated_poem = generate_poem(theme, length, style, similar_poems)
            st.success("Votre poème est prêt !")
            st.write(generated_poem)
        else:
            st.error("Aucun poème trouvé pour le thème sélectionné.")
