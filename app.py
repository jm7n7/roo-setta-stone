import dash
from dash import dcc, html
from data_loader import THEME

# Initialize the Dash app with Pages support
app = dash.Dash(__name__, use_pages=True, suppress_callback_exceptions=True)
app.title = "The Roo-Setta Stone"

app.layout = html.Div([
    # Navigation Bar
    html.Nav([
        html.Div([
            html.Div([
                html.H2("🦘 The Roo-Setta Stone", style={'color': THEME['secondary'], 'fontFamily': "'Playfair Display', serif", 'margin': 0}),
                html.P("Big Data Powered Exploration", style={'color': '#E8D5B7', 'margin': 0, 'fontSize': '14px'})
            ]),
            html.Div([
                dcc.Link('🏠 Home', href='/', className='nav-link', style={'color': THEME['secondary'], 'margin': '0 15px', 'textDecoration': 'none', 'fontSize': '18px'}),
                dcc.Link('🔍 Book Search', href='/search', className='nav-link', style={'color': THEME['secondary'], 'margin': '0 15px', 'textDecoration': 'none', 'fontSize': '18px'}),
                dcc.Link('🎮 Game Hub', href='/games', className='nav-link', style={'color': THEME['secondary'], 'margin': '0 15px', 'textDecoration': 'none', 'fontSize': '18px'}),
                # NEW: Data Analysis Link
                dcc.Link('📊 Data Analysis', href='/analysis', className='nav-link', style={'color': THEME['secondary'], 'margin': '0 15px', 'textDecoration': 'none', 'fontSize': '18px'}),
                dcc.Link('💞 Literary Pairings', href='/pairings', className='nav-link', style={'color': THEME['secondary'], 'margin': '0 15px', 'textDecoration': 'none', 'fontSize': '18px'}),
            ])
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'maxWidth': '1200px', 'margin': '0 auto'})
    ], style={'backgroundColor': THEME['nav_bg'], 'padding': '20px 40px', 'marginBottom': '30px'}),
    
    # This acts as the router outlet
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)
