import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from data_loader import THEME, df
import game_utils
import pandas as pd

dash.register_page(__name__, path='/tale-of-counts')

layout = html.Div([
    dcc.Store(id='tale-store', data={}),
    
    html.Div([
        dcc.Link('← Back to Game Hub', href='/games', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
        html.H1("⚔️ Tale of Two Counts", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Who used the word more?", style={'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '20px', 'fontStyle': 'italic'}),
        
        # Start Screen
        html.Div(id='tale-start-screen', children=[
            html.Button('⚔️ Start Battle', id='tale-start-btn', n_clicks=0, style={'padding': '20px 40px', 'fontSize': '24px', 'backgroundColor': THEME['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '12px', 'cursor': 'pointer', 'boxShadow': '0 4px 12px rgba(0,0,0,0.2)'})
        ], style={'textAlign': 'center', 'marginBottom': '40px'}),
        
        # Game Interface
        html.Div(id='tale-game-interface', style={'display': 'none'}, children=[
            
            # Word Display Container (Centered)
            html.Div([
                html.Div([
                    html.H3("Target Word", style={'color': THEME['text_light'], 'marginBottom': '5px'}),
                    html.H1(id='tale-target-word', style={'color': THEME['primary'], 'fontSize': '48px', 'margin': '10px 0', 'textTransform': 'uppercase', 'letterSpacing': '2px'})
                ], style={'textAlign': 'center', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '12px', 'display': 'inline-block', 'border': f'2px solid {THEME["border"]}'})
            ], style={'textAlign': 'center', 'marginBottom': '40px'}),
            
            # Cards Container
            html.Div([
                # Book 1 Card
                html.Div([
                    html.H3(id='tale-book1-title', style={'color': THEME['text_dark'], 'minHeight': '60px'}),
                    html.P(id='tale-book1-author', style={'color': THEME['text_light'], 'marginBottom': '5px'}),
                    html.P(id='tale-book1-genre', style={'color': THEME['accent'], 'fontSize': '14px', 'marginBottom': '20px', 'fontStyle': 'italic'}),
                    html.Button("Select This Book", id='tale-btn-1', n_clicks=0, style={'width': '100%', 'padding': '15px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'fontSize': '18px', 'cursor': 'pointer'}),
                    html.Div(id='tale-result-1', style={'marginTop': '15px', 'fontSize': '24px', 'fontWeight': 'bold'})
                ], className='book-card', style={'flex': '1', 'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'textAlign': 'center', 'margin': '0 20px', 'border': f'1px solid {THEME["border"]}'}),
                
                # VS Badge
                html.Div([
                    html.H1("VS", style={'color': THEME['accent'], 'fontSize': '48px', 'margin': '0'})
                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'}),
                
                # Book 2 Card
                html.Div([
                    html.H3(id='tale-book2-title', style={'color': THEME['text_dark'], 'minHeight': '60px'}),
                    html.P(id='tale-book2-author', style={'color': THEME['text_light'], 'marginBottom': '5px'}),
                    html.P(id='tale-book2-genre', style={'color': THEME['accent'], 'fontSize': '14px', 'marginBottom': '20px', 'fontStyle': 'italic'}),
                    html.Button("Select This Book", id='tale-btn-2', n_clicks=0, style={'width': '100%', 'padding': '15px', 'backgroundColor': THEME['secondary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'fontSize': '18px', 'cursor': 'pointer'}),
                    html.Div(id='tale-result-2', style={'marginTop': '15px', 'fontSize': '24px', 'fontWeight': 'bold'})
                ], className='book-card', style={'flex': '1', 'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'textAlign': 'center', 'margin': '0 20px', 'border': f'1px solid {THEME["border"]}'})
            ], style={'display': 'flex', 'justifyContent': 'center', 'maxWidth': '1000px', 'margin': '0 auto'}),
            
            # Feedback & Next Button
            html.Div(id='tale-feedback-area', style={'textAlign': 'center', 'marginTop': '40px', 'display': 'none'}, children=[
                html.H2(id='tale-feedback-text', style={'marginBottom': '20px'}),
                html.Button('Next Battle →', id='tale-next-btn', n_clicks=0, style={'padding': '15px 35px', 'fontSize': '20px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer'})
            ])
        ])
    ])
])

@callback(
    [Output('tale-game-interface', 'style'),
     Output('tale-start-screen', 'style'),
     Output('tale-book1-title', 'children'),
     Output('tale-book1-author', 'children'),
     Output('tale-book1-genre', 'children'),
     Output('tale-book2-title', 'children'),
     Output('tale-book2-author', 'children'),
     Output('tale-book2-genre', 'children'),
     Output('tale-target-word', 'children'),
     Output('tale-store', 'data'),
     Output('tale-result-1', 'children'),
     Output('tale-result-2', 'children'),
     Output('tale-feedback-area', 'style'),
     Output('tale-feedback-text', 'children'),
     Output('tale-btn-1', 'disabled'),
     Output('tale-btn-2', 'disabled')],
    [Input('tale-start-btn', 'n_clicks'),
     Input('tale-next-btn', 'n_clicks'),
     Input('tale-btn-1', 'n_clicks'),
     Input('tale-btn-2', 'n_clicks')],
    [State('tale-store', 'data')]
)
def tale_game_logic(start_click, next_click, btn1_click, btn2_click, state):
    ctx = dash.callback_context
    if not ctx.triggered: return [no_update] * 16
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # 1. START or NEXT ROUND
    if trigger_id in ['tale-start-btn', 'tale-next-btn']:
        available_ids = df['book_number'].tolist()
        game_data = game_utils.get_stat_attack_challenge(available_ids)
        
        if not game_data: return [no_update] * 16
        
        # Ensure we have valid integers for lookup
        id1 = int(game_data['id_1'])
        id2 = int(game_data['id_2'])
        
        # Safe Metadata Lookup
        row1 = df[df['book_number'] == id1]
        row2 = df[df['book_number'] == id2]
        
        # Fallback if book ID exists in DB but not in CSV (shouldn't happen, but safe)
        if row1.empty or row2.empty:
             # Just retry silently by returning no_update and letting user click again, 
             # or ideally recurse, but for safety we just stop.
             return [no_update] * 16

        b1 = row1.iloc[0]
        b2 = row2.iloc[0]
        
        # Safe String Conversion (Handles NaNs in CSV)
        t1 = str(b1['title']) if pd.notna(b1['title']) else "Unknown Title"
        a1 = str(b1['author']) if pd.notna(b1['author']) else "Unknown Author"
        
        t2 = str(b2['title']) if pd.notna(b2['title']) else "Unknown Title"
        a2 = str(b2['author']) if pd.notna(b2['author']) else "Unknown Author"
        
        def format_genres(g):
            if isinstance(g, list): return ", ".join(g)
            if pd.isna(g): return ""
            return str(g)
            
        g1 = format_genres(b1['genres'])
        g2 = format_genres(b2['genres'])
        
        return (
            {'display': 'block'}, {'display': 'none'},
            t1, a1, g1,
            t2, a2, g2,
            game_data['word'], game_data,
            "", "", {'display': 'none'}, "", False, False
        )
        
    # 2. GUESSING
    if trigger_id in ['tale-btn-1', 'tale-btn-2']:
        c1, c2 = state['count_1'], state['count_2']
        user_chose_1 = (trigger_id == 'tale-btn-1')
        winner_is_1 = c1 > c2
        is_correct = (user_chose_1 and winner_is_1) or (not user_chose_1 and not winner_is_1)
        
        feedback_text = "🎉 Correct!" if is_correct else "❌ Wrong!"
        feedback_color = "green" if is_correct else "red"
        res1 = html.Span(f"{c1:,} times", style={'color': 'green' if winner_is_1 else '#666'})
        res2 = html.Span(f"{c2:,} times", style={'color': 'green' if not winner_is_1 else '#666'})
        feedback_header = html.Span(feedback_text, style={'color': feedback_color, 'fontSize': '32px', 'fontWeight': 'bold'})
        
        return (
            no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, state,
            res1, res2, {'display': 'block', 'textAlign': 'center', 'marginTop': '40px'}, feedback_header, True, True
        )

    return [no_update] * 16