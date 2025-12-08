import dash
from dash import dcc, html, Input, Output, State, callback, no_update
import plotly.express as px
import plotly.io as pio
import pandas as pd
import sqlite3
import os
import game_utils
from data_loader import THEME

dash.register_page(__name__, path='/analysis/distributions')

# --- Load Static Plots ---
PLOT_DIR = 'assets/plots'

def load_static_fig(filename):
    """Loads a pre-generated Plotly JSON file"""
    path = os.path.join(PLOT_DIR, filename)
    if os.path.exists(path):
        return pio.read_json(path)
    else:
        return {
            "layout": {
                "title": "Plot not found. Run generate_plots.py first.",
                "xaxis": {"visible": False}, 
                "yaxis": {"visible": False}
            }
        }

# Load Plots
fig_vocab = load_static_fig('dist_vocab.json')
fig_zipf  = load_static_fig('dist_zipf.json') # NEW

# --- Helper for Dynamic Plot ---
def get_word_distribution(target_word):
    conn = sqlite3.connect(game_utils.DB_PATH)
    target_word = target_word.lower().strip()
    query = "SELECT count FROM word_counts WHERE word = ?"
    try:
        df = pd.read_sql_query(query, conn, params=(target_word,))
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        conn.close()


# --- Layout ---
layout = html.Div([
    dcc.Link('← Back to Analysis Hub', href='/analysis', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
    
    html.Div([
        html.H1("📈 Library Distributions", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Analyze the shape of the Project Gutenberg library.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '40px', 'fontStyle': 'italic'}),
        
        # 1. Static Graphs Row
        html.Div([
            # Graph 1: Vocabulary Size
            html.Div([
                dcc.Graph(figure=fig_vocab)
            ], style={'flex': '1', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'marginRight': '20px'}),
            
            # Graph 2: Zipf's Law (NEW)
            html.Div([
                dcc.Graph(figure=fig_zipf)
            ], style={'flex': '1', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})
            
        ], style={'display': 'flex', 'marginBottom': '50px', 'flexWrap': 'wrap'}),

        # 2. Dynamic Section: Word Distribution
        html.Div([
            html.H3("Search Word Distribution", style={'color': THEME['primary'], 'borderBottom': f'2px solid {THEME["secondary"]}', 'paddingBottom': '10px', 'marginBottom': '20px', 'display': 'inline-block'}),
            html.P("See how frequently a specific word appears across the entire collection.", style={'color': '#666', 'marginBottom': '20px'}),
            
            # Input Area
            html.Div([
                dcc.Input(
                    id='dist-word-input', 
                    type='text', 
                    placeholder='Type a word (e.g. whale)...', 
                    n_submit=0,
                    style={'width': '60%', 'padding': '15px', 'fontSize': '18px', 'borderRadius': '8px 0 0 8px', 'border': f'1px solid {THEME["border"]}', 'outline': 'none'}
                ),
                html.Button(
                    'Plot Distribution', 
                    id='dist-word-btn', 
                    n_clicks=0, 
                    style={'padding': '15px 30px', 'fontSize': '18px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '0 8px 8px 0', 'cursor': 'pointer'}
                )
            ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '30px'}),
            
            # Dynamic Graph
            dcc.Loading(
                id="loading-word-dist",
                type="dot",
                color=THEME['primary'],
                children=dcc.Graph(id='word-dist-graph', style={'display': 'none'})
            )
        ], style={'marginTop': '30px', 'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})

    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'paddingBottom': '50px'})
])

# --- Callbacks ---

@callback(
    [Output('word-dist-graph', 'figure'),
     Output('word-dist-graph', 'style')],
    [Input('dist-word-btn', 'n_clicks'), Input('dist-word-input', 'n_submit')],
    State('dist-word-input', 'value'),
    prevent_initial_call=True
)
def plot_word_distribution(n_clicks, n_submit, word):
    if not word: return no_update, {'display': 'none'}
    
    df_word = get_word_distribution(word)
    
    if df_word.empty:
        layout = {
            "title": f"No data found for '{word}'",
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
            "paper_bgcolor": 'rgba(0,0,0,0)',
            "plot_bgcolor": 'rgba(0,0,0,0)'
        }
        return {"data": [], "layout": layout}, {'display': 'block'}

    # 98th Percentile Cap Logic
    cap = df_word['count'].quantile(0.98)
    safe_cap = max(cap, 10) 
    max_val = df_word['count'].max()
    
    if max_val > safe_cap * 1.5:
        plot_df = df_word[df_word['count'] <= safe_cap]
        title_suffix = f" (Outliers Removed)"
    else:
        plot_df = df_word
        title_suffix = ""

    fig = px.histogram(
        plot_df, 
        x='count',
        nbins=40,
        title=f"Frequency: '{word}'{title_suffix}",
        color_discrete_sequence=[THEME['primary']]
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=f"Occurrences of '{word}' in a Book",
        yaxis_title="Number of Books",
        font={'family': "Sans-Serif", 'color': THEME['text_dark']},
        title_font={'family': "'Playfair Display', serif", 'size': 24},
        bargap=0.1,
        xaxis=dict(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor=THEME['border']),
        yaxis=dict(showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor=THEME['border'])
    )

    return fig, {'display': 'block'}