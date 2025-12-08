import dash
from dash import dcc, html, dash_table, Input, Output, callback, no_update
import plotly.express as px
import plotly.io as pio
import pandas as pd
import sqlite3
import os
import game_utils
from data_loader import THEME, df as df_meta

dash.register_page(__name__, path='/analysis/authors')

# --- Load Static Plots & Data ---
PLOT_DIR = 'assets/plots'

def load_static_fig(filename):
    path = os.path.join(PLOT_DIR, filename)
    if os.path.exists(path):
        return pio.read_json(path)
    else:
        return {"layout": {"title": "Plot not found.", "xaxis": {"visible": False}, "yaxis": {"visible": False}}}

def load_table_data():
    path = os.path.join(PLOT_DIR, 'author_top_words.json')
    if os.path.exists(path):
        return pd.read_json(path)
    else:
        return pd.DataFrame()

fig_scatter = load_static_fig('author_scatter.json')
fig_bar = load_static_fig('author_bar.json')
fig_hapax = load_static_fig('author_hapax.json')
df_table = load_table_data()

# --- Data Prep for Dropdown ---
author_counts = df_meta['author'].value_counts().sort_values(ascending=False)
author_options = [{'label': f"{auth} ({count} books)", 'value': auth} for auth, count in author_counts.items()]
default_author = author_counts.index[0] if not author_counts.empty else None

# --- Helper: Dynamic Author Words ---
def get_top_words_for_author(author_name, word_type):
    conn = sqlite3.connect(game_utils.DB_PATH)
    books = df_meta[df_meta['author'] == author_name]
    if books.empty:
        conn.close()
        return pd.DataFrame()
    book_ids = books['book_number'].tolist()
    id_list = ",".join(map(str, book_ids))
    
    query = f"SELECT word, count FROM word_counts WHERE book_id IN ({id_list})"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        conn.close()
        return pd.DataFrame()
    conn.close()
    
    if df.empty: return pd.DataFrame()

    stopwords = game_utils.STOPWORDS
    if word_type == 'stop':
        df_filtered = df[df['word'].isin(stopwords)]
        title_color = THEME['secondary']
    else:
        df_filtered = df[~df['word'].isin(stopwords)]
        title_color = THEME['primary']
        
    top_words = df_filtered.groupby('word')['count'].sum().sort_values(ascending=False).head(15).reset_index()
    return top_words, title_color


# --- Main Layout ---
layout = html.Div([
    dcc.Link('← Back to Analysis Hub', href='/analysis', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
    
    html.Div([
        html.H1("✒️ Author Analysis", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Comparing the linguistic habits of authors with multiple works in the library.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '40px', 'fontStyle': 'italic'}),
        
        # Row 1: Static Plots
        html.Div([
            html.Div([
                html.H3("Vocabulary vs. Verbosity", style={'color': THEME['primary'], 'marginBottom': '10px'}),
                dcc.Graph(figure=fig_scatter)
            ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'marginBottom': '30px'}),
            
            html.Div([
                html.H3("The Vocabulary Leaderboard", style={'color': THEME['primary'], 'marginBottom': '10px'}),
                dcc.Graph(figure=fig_bar, style={'height': '600px'})
            ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'marginBottom': '30px'}),
        ]),

        # Row 2: Dynamic Explorer
        html.Div([
            html.H3("🔎 Deep Dive: Author Word Usage", style={'color': THEME['primary'], 'borderBottom': f'2px solid {THEME["secondary"]}', 'paddingBottom': '10px', 'marginBottom': '20px', 'display': 'inline-block'}),
            html.Div([
                html.Div([
                    html.Label("Select Author:", style={'fontWeight': 'bold'}),
                    dcc.Dropdown(id='author-select', options=author_options, value=default_author, clearable=False)
                ], style={'flex': 1, 'marginRight': '20px'}),
                html.Div([
                    html.Label("Word Type:", style={'fontWeight': 'bold'}),
                    dcc.RadioItems(id='word-type-select', options=[{'label': 'Stop Words', 'value': 'stop'}, {'label': 'Content Words', 'value': 'content'}], value='content', inline=False)
                ], style={'flex': 0, 'minWidth': '200px'})
            ], style={'display': 'flex', 'marginBottom': '20px', 'backgroundColor': '#f9f9f9', 'padding': '15px', 'borderRadius': '8px'}),
            dcc.Loading(type="dot", color=THEME['primary'], children=dcc.Graph(id='author-word-graph'))
        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'marginBottom': '30px'}),

        # Row 3: Signature Words Table
        html.Div([
            html.H3("🏆 Signature Words (Top 50 Authors)", style={'color': THEME['primary'], 'borderBottom': f'2px solid {THEME["secondary"]}', 'paddingBottom': '10px', 'marginBottom': '20px', 'display': 'inline-block'}),
            dash_table.DataTable(
                data=df_table.to_dict('records'),
                columns=[{'name': 'Author', 'id': 'Author'}, {'name': 'Total Books', 'id': 'Books'}, {'name': 'Signature Word', 'id': 'Signature Word'}, {'name': 'Total Count', 'id': 'Count'}],
                style_table={'overflowX': 'auto'},
                style_header={'backgroundColor': THEME['primary'], 'color': 'white', 'fontWeight': 'bold', 'textAlign': 'left', 'padding': '12px'},
                style_cell={'textAlign': 'left', 'padding': '12px', 'fontSize': '14px'},
                style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}],
                page_size=10,
                sort_action='native'
            )
        ], style={'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'marginBottom': '30px'}),

        # Row 4: Hapax Legomena (Updated)
        html.Div([
            html.H3("🧪 The 'One-Hit Wonder' Ratio (Hapax Legomena)", style={'color': THEME['primary'], 'borderBottom': f'2px solid {THEME["secondary"]}', 'paddingBottom': '10px', 'marginBottom': '20px', 'display': 'inline-block'}),
            html.P("Comparing the Top 20 most prolific authors against 20 'Casual' authors (those with only 2-3 books). Does writing more force you to recycle words, or invent new ones?", style={'color': '#666', 'marginBottom': '20px'}),
            dcc.Graph(figure=fig_hapax, style={'height': '800px'}) # Increased height to fit 40 bars
        ], style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)'})

    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'paddingBottom': '50px'})
])

# --- Callback ---
@callback(
    Output('author-word-graph', 'figure'),
    [Input('author-select', 'value'), Input('word-type-select', 'value')]
)
def update_author_graph(author, word_type):
    if not author: return no_update
    df_words, color_hex = get_top_words_for_author(author, word_type)
    if df_words.empty: return {"layout": {"title": "No data", "xaxis": {"visible": False}, "yaxis": {"visible": False}}}
    
    fig = px.bar(df_words, x='word', y='count', title=f"Top 15 Words used by {author}", color_discrete_sequence=[color_hex])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font={'family': "Sans-Serif", 'color': THEME['text_dark']},
        title={'font': {'family': "'Playfair Display', serif", 'size': 24}},
        xaxis=dict(title=None), yaxis=dict(title="Count", showgrid=True, gridcolor='#e0e0e0')
    )
    return fig