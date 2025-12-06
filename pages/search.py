import dash
from dash import dcc, html, Input, Output, State, callback
from data_loader import THEME, df

dash.register_page(__name__, path='/search')

layout = html.Div([
    html.Div([
        html.H1("Library Explorer", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Search the metadata, then click a book to see the Spark analysis.", style={'textAlign': 'center', 'fontStyle': 'italic'}),
        
        html.Div([
            dcc.Input(id='search-input', type='text', placeholder='Search title, author...', style={'width': '70%', 'padding': '12px', 'fontSize': '18px', 'borderRadius': '8px', 'border': f'1px solid {THEME["border"]}'}),
            html.Button('Search', id='search-btn', style={'marginLeft': '10px', 'padding': '12px 24px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'fontSize': '18px', 'cursor': 'pointer'})
        ], style={'textAlign': 'center', 'marginTop': '30px'}),
    ]),
    html.Div(id='search-results', style={'marginTop': '40px'})
])

@callback(
    Output('search-results', 'children'),
    Input('search-btn', 'n_clicks'),
    State('search-input', 'value')
)
def search_books(n_clicks, term):
    if not term: return html.Div()
    term = term.lower()
    results = df[df['title'].str.lower().str.contains(term, na=False) | df['author'].str.lower().str.contains(term, na=False)].head(12)
    
    if results.empty: return html.P("No results found.", style={'textAlign': 'center'})
    
    cards = []
    for _, row in results.iterrows():
        cards.append(dcc.Link(
            html.Div([
                html.H3(row['title'], style={'fontSize': '18px', 'margin': '0 0 10px 0', 'color': THEME['text_dark']}),
                html.P(row['author'], style={'color': THEME['text_light'], 'fontSize': '14px'}),
                html.P(f"ID: {row['book_number']}", style={'fontSize': '12px', 'color': '#999'})
            ], className='book-card', style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 2px 5px rgba(0,0,0,0.1)', 'border': f'1px solid {THEME["border"]}'}),
            href=f"/book/{row['book_number']}", style={'textDecoration': 'none'}
        ))
    
    return html.Div(cards, style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fill, minmax(250px, 1fr))', 'gap': '20px'})
