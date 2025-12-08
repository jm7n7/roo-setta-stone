import dash
from dash import dcc, html
from data_loader import THEME

dash.register_page(__name__, path='/analysis')

layout = html.Div([
    html.Div([
        html.H1("📊 Data Analysis Hub", style={'textAlign': 'center', 'color': THEME['text_dark'], 'marginBottom': '10px'}),
        html.P("Explore the Project Gutenberg library through the lens of data visualization.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '50px', 'fontSize': '18px', 'fontStyle': 'italic'}),
        
        # Analysis Cards Grid
        html.Div([
            
            # Card 1: Distributions
            dcc.Link(html.Div([
                html.Div("📈", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Distributions", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("Analyze the spread of word counts and vocabulary sizes across the entire library.", style={'color': '#666'}),
                html.Button("View Charts", style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px', 'transition': 'transform 0.2s'}), href='/analysis/distributions', style={'textDecoration': 'none'}),

            # Card 2: Authors
            dcc.Link(html.Div([
                html.Div("✒️", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Author Stats", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("Compare the vocabulary depth and linguistic habits of the top authors.", style={'color': '#666'}),
                html.Button("View Charts", style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px', 'transition': 'transform 0.2s'}), href='/analysis/authors', style={'textDecoration': 'none'}),

        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '30px'})
    ])
])