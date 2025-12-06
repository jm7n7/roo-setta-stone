import dash
from dash import dcc, html
from data_loader import THEME

dash.register_page(__name__, path='/pairings')

layout = html.Div([
    html.Div([
        html.H1("💞 Literary Pairings", style={'textAlign': 'center', 'color': THEME['text_dark'], 'marginBottom': '10px'}),
        html.P("Discover books that share surprising statistical similarities.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '50px', 'fontSize': '18px', 'fontStyle': 'italic'}),
        
        # Pairings Grid
        html.Div([
            
            # Card 1: Unique Word Twins (Placeholder)
            dcc.Link(html.Div([
                html.Div("👯", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Unique Word Twins", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("Books that share the exact same number of unique words.", style={'color': '#666'}),
                html.Button("Explore Pairings", disabled=True, style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': '#ccc', 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px', 'opacity': '0.7'}), href='/unique-twins', style={'textDecoration': 'none'}),

            # Card 2: Individual Word Twins (Placeholder)
            dcc.Link(html.Div([
                html.Div("🔡", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Individual Word Twins", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("Books that use a specific word the exact same number of times.", style={'color': '#666'}),
                html.Button("Explore Pairings", disabled=True, style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': '#ccc', 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px', 'opacity': '0.7'}), href='/word-twins', style={'textDecoration': 'none'}),

        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '30px'})
    ])
])