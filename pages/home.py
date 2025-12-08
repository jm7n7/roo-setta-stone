import dash
from dash import dcc, html
from data_loader import THEME

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.H1("The Roo-Setta Stone", style={'textAlign': 'center', 'color': THEME['text_dark'], 'fontSize': '56px', 'marginBottom': '15px', 'fontFamily': "'Playfair Display', serif"}),
        html.P("Deciphering the Project Gutenberg Library with Big Data", style={'textAlign': 'center', 'fontSize': '24px', 'color': THEME['accent'], 'fontStyle': 'italic', 'marginBottom': '20px'}),
        html.H3("Created by Brady Maes and Joseph Marinello", style={'textAlign': 'center', 'fontSize': '18px', 'color': THEME['text_light'], 'marginBottom': '60px', 'fontWeight': 'normal'}),
        
        # Cards
        html.Div([
            html.Div([
                html.H3("🎯 The Goal", style={'color': THEME['primary'], 'borderBottom': f"2px solid {THEME['secondary']}", 'paddingBottom': '10px'}),
                html.P("To process and analyze the vast Project Gutenberg library (~24,000 books) to uncover linguistic fingerprints and literary trends using modern Big Data architecture.", style={'lineHeight': '1.6', 'fontSize': '18px'})
            ], style={'flex': '1', 'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '10px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'margin': '0 20px', 'minWidth': '300px'}),
            
            html.Div([
                html.H3("⚙️ The Method", style={'color': THEME['primary'], 'borderBottom': f"2px solid {THEME['secondary']}", 'paddingBottom': '10px'}),
                html.P("We employed a classic MapReduce strategy using PySpark to clean, tokenize, and count over 1.4 billion words. The results are indexed in SQLite for real-time querying.", style={'lineHeight': '1.6', 'fontSize': '18px'})
            ], style={'flex': '1', 'backgroundColor': 'white', 'padding': '40px', 'borderRadius': '10px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'margin': '0 20px', 'minWidth': '300px'})
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginBottom': '60px', 'flexWrap': 'wrap', 'gap': '20px'}),
        
        # Navigation Buttons (Reordered to match Nav Bar)
        html.Div([
            # 1. Search
            dcc.Link(html.Button('🔍 Book Search', style={'padding': '20px 30px', 'fontSize': '18px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'width': '250px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.2)'}), href='/search'),
            
            # 2. Games
            dcc.Link(html.Button('🎮 Game Hub', style={'padding': '20px 30px', 'fontSize': '18px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'width': '250px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.2)'}), href='/games'),

            # 3. Analysis
            dcc.Link(html.Button('📊 Data Analysis', style={'padding': '20px 30px', 'fontSize': '18px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'width': '250px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.2)'}), href='/analysis'),
            
            # 4. Pairings
            dcc.Link(html.Button('💞 Literary Pairings', style={'padding': '20px 30px', 'fontSize': '18px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer', 'width': '250px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.2)'}), href='/pairings'),

        ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap', 'gap': '20px'})

    ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '40px'})
])
