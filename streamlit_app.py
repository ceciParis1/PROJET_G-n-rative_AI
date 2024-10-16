import streamlit as st
import requests
import faiss
import numpy as np
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Set up Streamlit page
st.set_page_config(page_title="Poem Generator", layout="wide")

st.markdown("""
## Poem Generator: Create Personalized Poems with AI
Choose the theme, style, and length, and let the AI generate beautiful verses for you!
""")

# PoetryDB API endpoint
POETRYDB_API = "https://poetrydb.org"

# Get the API key from the user
api_key = st.text_input("Enter your Google API Key:", type="password", key="api_key_input")

# Function to fetch poems from PoetryDB API
def fetch_poems_from_api(theme):
    try:
        response = requests.get(f"{POETRYDB_API}/lines/{theme}")
        if response.status_code == 200:
            return response.json()  # Return poem data
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching poems: {str(e)}")
        return None

# Function to generate embeddings and store them in FAISS
def create_vector_store(poems, api_key):
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    
    # Get embeddings for each poem
    poem_embeddings = embeddings_model.embed_texts([poem['lines'][0] for poem in poems])

    # Create FAISS index
    dimension = len(poem_embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(np.array(poem_embeddings))
    
    # Save the index to disk
    faiss.write_index(index, 'poem_faiss_index')

# Function to load FAISS index and retrieve similar poems
def retrieve_similar_poems(user_input, api_key):
    index = faiss.read_index('poem_faiss_index')
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    user_embedding = embeddings_model.embed_text(user_input)

    D, I = index.search(np.array([user_embedding]), k=5)  # Retrieve 5 closest poems
    return I

# Function to generate a new poem inspired by existing poems
def generate_poem(theme, length, style, api_key, poems):
    if poems:
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, google_api_key=api_key)
        poem_texts = "\n\n".join([p['lines'][0:5] for p in poems])  # First 5 lines of each poem as inspiration
        
        prompt_template = """
        Create a poem with the following details:
        - Theme: {theme}
        - Style: {style}
        - Length: {length}
        Use this context of existing poetry to inspire your poem:
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

# Sidebar for user input
with st.sidebar:
    st.title("Customize Your Poem")
    theme = st.text_input("Theme (e.g., love, nature, melancholy)")
    length = st.selectbox("Length", ["short", "medium", "long"])
    style = st.selectbox("Style", ["free verse", "sonnet", "haiku", "limerick"])

    if st.button("Generate Poem") and api_key:
        with st.spinner("Fetching poems and generating your custom poem..."):
            poems = fetch_poems_from_api(theme)
            if poems:
                create_vector_store(poems, api_key)
                generated_poem = generate_poem(theme, length, style, api_key, poems)
                st.success("Your poem is ready!")
                st.write(generated_poem)
            else:
                st.error("No poems found for the selected theme.")
