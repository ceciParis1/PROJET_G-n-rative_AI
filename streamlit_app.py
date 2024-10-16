import streamlit as st
import requests
from langchain.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Configurer la page Streamlit
st.set_page_config(page_title="Générateur de Poèmes", layout="wide")

st.markdown("""
## Générateur de Poèmes : Créez des poèmes personnalisés avec l'IA
Choisissez un thème, un style et une longueur, et laissez l'IA générer de magnifiques vers pour vous !
""")

# URL de l'API PoetryDB
POETRYDB_API = "https://poetrydb.org"

# Récupérer la clé API de l'utilisateur
api_key = st.text_input("Entrez votre clé API Google :", type="password", key="api_key_input")

# Fonction pour récupérer les poèmes via l'API PoetryDB
def fetch_poems_from_api(theme):
    try:
        response = requests.get(f"{POETRYDB_API}/lines/{theme}")
        if response.status_code == 200:
            return response.json()  # Retourne les données des poèmes
        else:
            return None
    except Exception as e:
        st.error(f"Erreur lors de la récupération des poèmes : {str(e)}")
        return None

# Fonction pour générer des embeddings et les stocker dans Chroma
def create_vector_store(poems, api_key):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    embeddings = embeddings_model.embed([poem['lines'][0] for poem in poems])  # Utiliser 'embed' au lieu de 'embed_texts'

    # Initialiser le magasin de vecteurs Chroma
    vector_store = Chroma.from_texts([poem['lines'][0] for poem in poems], embeddings)

    return vector_store

# Fonction pour récupérer des poèmes similaires avec Chroma
def retrieve_similar_poems(user_input, api_key, vector_store):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    user_embedding = embeddings_model.embed(user_input)  # Assurez-vous que cette méthode existe

    similar_poems = vector_store.similarity_search(user_input, k=5)
    return similar_poems

# Fonction pour générer un nouveau poème inspiré des poèmes existants
def generate_poem(theme, length, style, api_key, poems):
    if poems:
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, google_api_key=api_key)
        poem_texts = "\n\n".join([p['lines'][0] for p in poems])  # Utiliser la première ligne de chaque poème comme inspiration
        
        prompt_template = """
        Créez un poème avec les détails suivants :
        - Thème : {theme}
        - Style : {style}
        - Longueur : {length}
        Utilisez ce contexte de poésie existante pour inspirer votre poème :
        {poem_texts}
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["theme", "style", "length", "poem_texts"])
        chain = model.create_prompt_chain(prompt)
        
        new_poem = chain.run({
            "theme": theme,
            "style": style,
            "length": length,
            "poem_texts": poem_texts
        })
        return new_poem

# Barre latérale pour l'entrée utilisateur
with st.sidebar:
    st.title("Personnalisez votre poème")
    theme = st.text_input("Thème (ex : amour, nature, mélancolie)")
    length = st.selectbox("Longueur", ["court", "moyen", "long"])
    style = st.selectbox("Style", ["vers libres", "sonnet", "haïku", "limerick"])

    if st.button("Générer un poème") and api_key:
        with st.spinner("Récupération des poèmes et génération de votre poème personnalisé..."):
            poems = fetch_poems_from_api(theme)
            if poems:
                vector_store = create_vector_store(poems, api_key)
                generated_poem = generate_poem(theme, length, style, api_key, poems)
                st.success("Votre poème est prêt !")
                st.write(generated_poem)
            else:
                st.error("Aucun poème trouvé pour le thème sélectionné.")
