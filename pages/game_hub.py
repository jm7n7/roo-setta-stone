import dash
from dash import dcc, html
from data_loader import THEME

dash.register_page(__name__, path='/games')

layout = html.Div([
    html.Div([
        html.H1("🎮 The Game Hub", style={'textAlign': 'center', 'color': THEME['text_dark'], 'marginBottom': '10px'}),
        html.P("Put your literary knowledge to the test with our data-driven challenges.", style={'textAlign': 'center', 'color': THEME['text_light'], 'marginBottom': '50px', 'fontSize': '18px', 'fontStyle': 'italic'}),
        
        # Games Grid
        html.Div([
            # Game 1: A Book with a Clue (Formerly Mystery)
            dcc.Link(html.Div([
                html.Div("🕵️", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("A Book with a Clue", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("We show you the 'Data Fingerprint' (Top 15 Words). You identify the book.", style={'color': '#666'}),
                html.Button("Play Now", style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'transition': 'transform 0.2s', 'width': '300px'}), href='/mystery', style={'textDecoration': 'none'}),

            # Game 2: Much Ado About Counting
            dcc.Link(html.Div([
                html.Div("✍️", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Much Ado About Counting", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("We show you a book. You guess which word appears most frequently.", style={'color': '#666'}),
                html.Button("Play Now", style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px'}), href='/much-ado', style={'textDecoration': 'none'}),

            # Game 3: Tale of Two Counts
            dcc.Link(html.Div([
                html.Div("⚔️", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Tale of Two Counts", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("Which book used the word more? A battle of frequency between two classics.", style={'color': '#666'}),
                html.Button("Play Now", style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px'}), href='/tale-of-counts', style={'textDecoration': 'none'}),

            # Game 4: Little Red Herring
            dcc.Link(html.Div([
                html.Div("🐟", style={'fontSize': '60px', 'marginBottom': '20px'}),
                html.H3("Little Red Herring", style={'color': THEME['primary'], 'marginBottom': '15px'}),
                html.P("One of these words doesn't belong in this book. Can you spot the imposter?", style={'color': '#666'}),
                html.Button("Play Now", style={'marginTop': '20px', 'padding': '10px 25px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
            ], className='game-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'width': '300px'}), href='/little-red-herring', style={'textDecoration': 'none'}),

        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '30px'})
    ])
])
