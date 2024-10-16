import openai
import streamlit as st

# Configurer la page Streamlit
st.set_page_config(page_title="Générateur de Poèmes", layout="wide")

st.markdown("""
## Générateur de Poèmes : Créez des poèmes personnalisés avec l'IA
Choisissez un thème, un style et une longueur, et laissez l'IA générer de magnifiques vers pour vous !
""")

# Récupérer la clé API de l'utilisateur
api_key = st.text_input("Entrez votre clé API OpenAI :", type="password")

# Configurer OpenAI avec la clé API fournie
if api_key:
    openai.api_key = api_key

# Fonction pour générer un poème à l'aide d'OpenAI
def generate_poem(theme, length, style):
    try:
        # Utilisation de la nouvelle interface ChatCompletion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Utiliser "gpt-4" si disponible
            messages=[
                {"role": "system", "content": "You are a poet."},
                {"role": "user", "content": f"Créez un poème sur le thème '{theme}', en style {style}, et d'une longueur {length}."}
            ],
            max_tokens=150  # Ajustez en fonction de la longueur du poème
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Erreur lors de la génération : {str(e)}"

# Interface utilisateur pour entrer les paramètres du poème
st.sidebar.title("Personnalisez votre poème")
theme = st.text_input("Thème (ex : amour, nature, mélancolie)")
length = st.selectbox("Longueur", ["court", "moyen", "long"])
style = st.selectbox("Style", ["vers libres", "sonnet", "haïku", "limerick"])

# Générer le poème lorsque l'utilisateur appuie sur le bouton
if st.button("Générer un poème") and api_key:
    with st.spinner("Génération de votre poème..."):
        generated_poem = generate_poem(theme, length, style)
        st.success("Votre poème est prêt !")
        st.write(generated_poem)
