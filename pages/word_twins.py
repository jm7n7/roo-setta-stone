import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import pandas as pd
import sqlite3
import game_utils
from data_loader import THEME, df

dash.register_page(__name__, path='/word-twins')

# --- Helper: Book Card Component ---
def get_book_card(book_id, count):
    """
    Generates a card specifically for the Word Twins view.
    """
    # Safe Metadata Lookup
    try:
        row = df[df['book_number'] == int(book_id)].iloc[0]
    except (IndexError, ValueError):
        return html.Div(f"Unknown Book ID: {book_id}", style={'color': 'red', 'padding': '10px'})

    genres = row['genres']
    genre_str = ", ".join(genres[:2]) if isinstance(genres, list) else str(genres)

    return dcc.Link(html.Div([
        # Title
        html.H4(row['title'], style={'margin': '0 0 5px 0', 'color': THEME['text_dark'], 'fontSize': '16px', 'fontFamily': "'Playfair Display', serif", 'whiteSpace': 'nowrap', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}),
        
        # Author
        html.P(row['author'], style={'margin': '0 0 2px 0', 'color': THEME['text_light'], 'fontSize': '13px', 'fontStyle': 'italic', 'whiteSpace': 'nowrap', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}),
        
        # NEW: Book ID
        html.P(f"ID: {book_id}", style={'margin': '0 0 10px 0', 'color': '#aaa', 'fontSize': '11px'}),
        
        # The Match Statistic
        html.Div([
            html.Span("Count: ", style={'color': '#666', 'fontSize': '12px'}),
            html.Span(f"{count:,}", style={'color': THEME['primary'], 'fontWeight': 'bold', 'fontSize': '16px'})
        ], style={'backgroundColor': '#f8f9fa', 'padding': '5px 10px', 'borderRadius': '4px', 'display': 'inline-block', 'border': f'1px solid {THEME["border"]}'})

    ], style={
        'backgroundColor': 'white',
        'padding': '15px',
        'borderRadius': '8px',
        'border': f'1px solid {THEME["border"]}',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)',
        'textAlign': 'center',
        'transition': 'transform 0.2s',
        'height': '100%',
        'width': '200px', 
        'display': 'inline-block',
        'verticalAlign': 'top',
        'marginRight': '15px',
        'marginBottom': '20px' 
    }), href=f"/book/{book_id}", style={'textDecoration': 'none'})

# --- Main Layout ---
layout = html.Div([
    dcc.Link('← Back to Pairings Hub', href='/pairings', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
    
    html.Div([
        html.H1("🔡 Individual Word Twins", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Find books that use a specific word the EXACT same number of times.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '30px', 'fontStyle': 'italic'}),
        
        # Search Bar Container
        html.Div([
            dcc.Input(
                id='word-twin-input', 
                type='text', 
                placeholder='Type a word (e.g., whale, love, death)...', 
                n_submit=0,
                style={'width': '60%', 'padding': '15px', 'fontSize': '18px', 'borderRadius': '8px 0 0 8px', 'border': f'1px solid {THEME["border"]}', 'outline': 'none'}
            ),
            html.Button(
                'Find Twins', 
                id='word-twin-btn', 
                n_clicks=0, 
                style={'padding': '15px 30px', 'fontSize': '18px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '0 8px 8px 0', 'cursor': 'pointer'}
            )
        ], style={'display': 'flex', 'justifyContent': 'center', 'maxWidth': '800px', 'margin': '0 auto 50px auto'}),
        
        # Loading Spinner & Results Container
        dcc.Loading(
            id="loading-word-twins",
            type="dot",
            color=THEME['primary'],
            children=html.Div(id='word-twin-results')
        )
    ])
])

# --- Logic: Find Clumps ---
def search_word_clumps(target_word):
    """
    Searches the DB for a word, groups by count, and returns clumps > 1.
    """
    conn = sqlite3.connect(game_utils.DB_PATH)
    target_word = target_word.lower().strip()
    
    # 1. Fetch all occurrences of the word
    query = "SELECT book_id, count FROM word_counts WHERE word = ?"
    try:
        df_results = pd.read_sql_query(query, conn, params=(target_word,))
    except Exception as e:
        conn.close()
        return None, f"Database Error: {e}"
    finally:
        conn.close()
        
    if df_results.empty:
        return None, "Word not found in any book."
        
    # 2. Group by 'count' to find ties
    clumps = df_results.groupby('count')['book_id'].apply(list)
    
    # 3. Filter: Keep only counts where len(books) > 1
    twins = clumps[clumps.apply(len) > 1]
    
    # 4. Sort: Sort by the Count Value (Descending)
    twins = twins.sort_index(ascending=False)
    
    return twins, None

# --- Callback ---
@callback(
    Output('word-twin-results', 'children'),
    [Input('word-twin-btn', 'n_clicks'), Input('word-twin-input', 'n_submit')],
    State('word-twin-input', 'value'),
    prevent_initial_call=True
)
def update_word_twins(n_clicks, n_submit, word):
    if not word:
        return html.Div("Please enter a word to search.", style={'textAlign': 'center', 'color': '#999'})
    
    # Run Search
    twins_series, error = search_word_clumps(word)
    
    if error:
        return html.Div(error, style={'textAlign': 'center', 'color': 'red', 'marginTop': '20px'})
        
    if twins_series.empty:
        return html.Div([
            html.H3(f"No twins found for '{word}'", style={'color': THEME['text_dark']}),
            html.P("Plenty of books use this word, but no two books use it the exact same number of times.", style={'color': '#666'})
        ], style={'textAlign': 'center', 'marginTop': '40px', 'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '12px'})

    # --- Build the UI for Results ---
    results_ui = []
    
    # Summary Header
    total_clumps = len(twins_series)
    total_books_involved = sum(len(ids) for ids in twins_series)
    
    results_ui.append(html.Div([
        html.H3(f"Found {total_clumps} Groups ({total_books_involved} Books Total)", style={'color': THEME['primary'], 'borderBottom': f'2px solid {THEME["secondary"]}', 'paddingBottom': '10px', 'display': 'inline-block'})
    ], style={'textAlign': 'center', 'marginBottom': '30px'}))
    
    # Iterate through the groups
    for count_val, book_ids in twins_series.items():
        
        # Create cards
        cards = [get_book_card(bid, count_val) for bid in book_ids]
        
        group_section = html.Div([
            # Group Header (The Count)
            html.Div([
                html.Span(f"Count: {count_val:,}", style={'fontSize': '20px', 'fontWeight': 'bold', 'color': 'white', 'backgroundColor': THEME['accent'], 'padding': '5px 15px', 'borderRadius': '20px'}),
                html.Span(f" ({len(book_ids)} books)", style={'marginLeft': '10px', 'color': THEME['text_light'], 'fontStyle': 'italic'})
            ], style={'marginBottom': '15px'}),
            
            # Cards Container (Flex Row)
            html.Div(cards, style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': '15px',
                'padding': '15px',
                'backgroundColor': '#fafafa',
                'borderRadius': '8px'
            })
        ], style={
            'marginBottom': '40px', 
            'backgroundColor': 'white', 
            'padding': '20px', 
            'paddingBottom': '35px', # Ensures bottom cards don't touch the edge
            'borderRadius': '12px', 
            'boxShadow': '0 2px 8px rgba(0,0,0,0.05)'
        })
        
        results_ui.append(group_section)
        
    return html.Div(results_ui, style={'maxWidth': '1000px', 'margin': '0 auto'})