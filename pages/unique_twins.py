import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import pandas as pd
import json
import os
import game_utils  # NEW: Imported to fetch word stats
from data_loader import THEME, df

dash.register_page(__name__, path='/unique-twins')

# --- Load Twins Data ---
JSON_FILE = 'unique_twins.json'
TWINS_DATA = {}
VALID_BOOK_IDS = []

def load_data_simple():
    """Simple loader that trusts the JSON structure"""
    global TWINS_DATA, VALID_BOOK_IDS
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r') as f:
                TWINS_DATA = json.load(f)
            # Create list of integer IDs for filtering (JSON keys are strings)
            VALID_BOOK_IDS = [int(k) for k in TWINS_DATA.keys()]
            print(f"✅ Loaded {len(TWINS_DATA)} books with twins.")
        except Exception as e:
            print(f"❌ Error loading unique_twins.json: {e}")

load_data_simple()

# --- Helper: Universal Book Card Component ---
def get_book_card(book_id, score=None, is_active=False):
    """
    Generates a polished card for a book.
    Now includes: Book ID, Total Words, and Unique Words.
    """
    # 1. Safe Metadata Lookup
    try:
        row = df[df['book_number'] == int(book_id)].iloc[0]
    except (IndexError, ValueError):
        return html.Div(f"Unknown Book ID: {book_id}", style={'color': 'red', 'padding': '10px'})

    # 2. Fetch Word Statistics from SQLite
    # This queries the DB for every card to get exact counts
    stats = game_utils.get_book_stats(int(book_id))
    total_words = stats.get('total_words', 0)
    unique_words = stats.get('unique_words', 0)

    # 3. Format Data
    genres = row['genres']
    genre_str = ", ".join(genres[:2]) if isinstance(genres, list) else str(genres)

    # 4. Dynamic Styles
    card_bg = '#e8f0fe' if is_active else 'white'
    border_color = THEME['primary'] if is_active else THEME['border']
    shadow = '0 4px 8px rgba(0,0,0,0.1)' if is_active else '0 2px 4px rgba(0,0,0,0.05)'

    # 5. Build Content
    content = [
        # Title & Author
        html.H4(row['title'], style={'margin': '0 0 5px 0', 'color': THEME['text_dark'], 'fontSize': '16px', 'fontFamily': "'Playfair Display', serif"}),
        html.P(row['author'], style={'margin': '0 0 5px 0', 'color': THEME['text_light'], 'fontSize': '13px', 'fontStyle': 'italic'}),
        
        # Genre
        html.P(genre_str, style={'margin': '0 0 10px 0', 'color': THEME['accent'], 'fontSize': '11px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
        
        # NEW: Stats Footer (ID, Words, Unique)
        html.Div([
            html.Span(f"ID: {book_id}", style={'fontWeight': 'bold', 'marginRight': '10px', 'color': THEME['primary']}),
            html.Span(f"{total_words:,} Words", style={'marginRight': '10px'}),
            html.Span(f"{unique_words:,} Unique")
        ], style={
            'borderTop': f'1px solid {THEME["border"]}', 
            'paddingTop': '8px', 
            'fontSize': '11px', 
            'color': '#666',
            'display': 'flex',
            'flexWrap': 'wrap',
            'justifyContent': 'space-between'
        })
    ]
    
    # Optional Score Badge (For Matches)
    if score:
        content.insert(0, html.Div(f"{score}% Match", style={
            'position': 'absolute', 'top': '10px', 'right': '10px',
            'backgroundColor': '#d4edda', 'color': '#155724', 'padding': '2px 8px', 
            'borderRadius': '10px', 'fontSize': '11px', 'fontWeight': 'bold',
            'border': '1px solid #c3e6cb'
        }))

    return html.Div(content, style={
        'position': 'relative',
        'backgroundColor': card_bg,
        'padding': '15px',
        'borderRadius': '8px',
        'border': f'1px solid {border_color}',
        'boxShadow': shadow,
        'transition': 'all 0.2s ease-in-out',
        'textAlign': 'left'
    })

# --- Main Layout ---
layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='selected-book-store', data=None),

    dcc.Link('← Back to Pairings Hub', href='/pairings', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
    
    html.Div([
        html.H1("👯 Unique Word Twins", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("These books share an extraordinarily high percentage of their unique vocabulary.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '40px', 'fontStyle': 'italic'}),
        
        # Flex Container
        html.Div([
            
            # LEFT: Scrollable Selection List
            html.Div([
                html.H3(f"Select a Book ({len(VALID_BOOK_IDS)})", style={'color': THEME['secondary'], 'borderBottom': f'2px solid {THEME["border"]}', 'paddingBottom': '10px', 'marginBottom': '15px'}),
                
                html.Div(id='twins-book-grid', style={
                    'display': 'flex', 
                    'flexDirection': 'column',
                    'gap': '10px', 
                    'maxHeight': '700px', 
                    'overflowY': 'auto',
                    'paddingRight': '10px',
                    'scrollbarWidth': 'thin'
                })
            ], style={'width': '35%', 'minWidth': '300px'}),
            
            # RIGHT: Results View
            html.Div([
                html.Div(id='selected-twin-view', children=[
                    html.Div([
                        html.Div("👈", style={'fontSize': '50px', 'marginBottom': '20px'}),
                        html.H2("Select a book from the list", style={'color': '#ccc'}),
                        html.P("Click on a card to reveal its literary twins.", style={'color': '#ccc'})
                    ], style={'textAlign': 'center', 'marginTop': '150px'})
                ], style={'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'minHeight': '500px'})
            ], style={'width': '60%', 'marginLeft': '5%'})
            
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'flex-start'})
    ])
])

# --- Callbacks ---

@callback(
    Output('twins-book-grid', 'children'),
    [Input('url', 'pathname'), Input('selected-book-store', 'data')]
)
def generate_book_list(pathname, selected_id):
    """Generates the scrollable list of books on the left."""
    if not VALID_BOOK_IDS:
        return html.Div("No matched books found in JSON.", style={'color': 'red', 'padding': '20px'})
    
    # Filter Metadata
    mask = df['book_number'].astype(int).isin(VALID_BOOK_IDS)
    valid_books_df = df[mask].sort_values('title')
    
    buttons = []
    for _, row in valid_books_df.iterrows():
        b_id = int(row['book_number'])
        is_active = (selected_id == b_id)

        # Generate Card (Now includes stats)
        card_content = get_book_card(b_id, is_active=is_active)
        
        buttons.append(html.Button(
            card_content,
            id={'type': 'twin-source-btn', 'index': b_id},
            style={'background': 'none', 'border': 'none', 'padding': '0', 'cursor': 'pointer', 'width': '100%', 'textAlign': 'left'}
        ))
    return buttons

@callback(
    [Output('selected-twin-view', 'children'),
     Output('selected-book-store', 'data')],
    Input({'type': 'twin-source-btn', 'index': dash.ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def display_matches(n_clicks):
    """Displays the matches for the clicked book."""
    ctx = dash.callback_context
    if not ctx.triggered: return no_update, no_update
    
    trigger_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
    book_id = trigger_id['index']
    
    matches = TWINS_DATA.get(str(book_id))
    if not matches: return html.Div("No matches found."), book_id
    
    # Header
    source_row = df[df['book_number'] == int(book_id)].iloc[0]
    header = html.Div([
        html.H4("LITERARY TWINS FOR:", style={'color': THEME['accent'], 'letterSpacing': '2px', 'fontSize': '12px', 'marginBottom': '10px'}),
        html.H1(source_row['title'], style={'color': THEME['text_dark'], 'fontSize': '32px', 'fontFamily': "'Playfair Display', serif", 'margin': '0 0 5px 0'}),
        html.P(f"by {source_row['author']}", style={'color': THEME['text_light'], 'fontSize': '16px', 'fontStyle': 'italic', 'marginBottom': '30px', 'borderBottom': f'2px solid {THEME["secondary"]}', 'paddingBottom': '20px'})
    ])
    
    # Match Cards
    sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)
    match_cards = [html.Div(get_book_card(m['id'], score=m['score']), style={'marginBottom': '15px'}) for m in sorted_matches]
        
    return html.Div([header, html.H3(f"Found {len(match_cards)} Match(es):", style={'color': THEME['text_dark'], 'marginBottom': '20px'}), html.Div(match_cards)]), book_id