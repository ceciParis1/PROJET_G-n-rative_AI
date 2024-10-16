# Poem Generator Using RAG Framework (Chroma Version)

This application uses the **PoetryDB API** to fetch existing poems as inspiration and **Google's Generative AI** to create new, custom poems based on user inputs such as theme, length, and style. The AI generates poems that are inspired by famous poems but does not copy them directly.

## Features

- **Custom Poem Generation**: Choose a theme (e.g., love, nature), a style (e.g., sonnet, haiku), and a length, and the AI generates a new poem for you.
- **Poetry Database**: Uses the PoetryDB API to retrieve famous poems and uses them as inspiration.
- **Generative AI**: Leverages Google Generative AI models for creative poem generation.
- **Vector Store**: Uses Chroma for vector similarity search (instead of FAISS).

## How to Run

### Prerequisites
- **Google API Key**: Obtain a Google API key to interact with Google's Generative AI models. [Get your API key here](https://makersuite.google.com/app/apikey).
- **Streamlit**: Ensure that Streamlit is installed in your Python environment.

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/yourusername/poem-generator.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    streamlit run streamlit_app.py
    ```

## How to Use

1. Enter your Google API key.
2. Choose a theme, length, and style for the poem.
3. Click "Generate Poem" to get your personalized poem.

## API Documentation
- **PoetryDB API**: The app fetches poems via [PoetryDB](https://poetrydb.org/) to inspire new poems.
