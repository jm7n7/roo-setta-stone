import pandas as pd
import ast
import os

# Configuration
CSV_PATH = 'gutenberg_metadata.csv'

# Theme colors - Literary/Library inspired
THEME = {
    'primary': '#8B4513',      # Saddle brown (book binding)
    'secondary': '#D4AF37',    # Gold (classic library)
    'accent': '#A0522D',       # Sienna (warm wood)
    'background': '#F5F5DC',   # Beige (aged paper)
    'card_bg': '#FFFFFF',      # White (fresh page)
    'text_dark': '#2C1810',    # Dark brown (ink)
    'text_light': '#5C4033',   # Medium brown
    'border': '#D2B48C',       # Tan (paper edge)
    'nav_bg': '#654321',       # Dark brown (leather)
}

def load_data():
    """Load and preprocess the CSV data"""
    if not os.path.exists(CSV_PATH):
        print("WARNING: Metadata CSV not found. Using dummy data.")
        return pd.DataFrame({
            'book_number': [15, 12, 84],
            'title': ['Moby Dick', 'Alice in Wonderland', 'Frankenstein'],
            'author': ['Herman Melville', 'Lewis Carroll', 'Mary Shelley'],
            'genres': [['Adventure'], ['Fantasy'], ['Horror']],
            'language': ['en', 'en', 'en']
        })

    df = pd.read_csv(CSV_PATH)
    # Convert genres string to list if needed
    if 'genres' in df.columns:
        df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    # Ensure book_number is int for merging
    if 'book_number' in df.columns:
        df['book_number'] = pd.to_numeric(df['book_number'], errors='coerce').fillna(0).astype(int)
        
    return df

# Load once when module is imported
df = load_data()