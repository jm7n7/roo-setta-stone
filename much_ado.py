import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from data_loader import THEME, df
import game_utils
import ast  # Added missing import

dash.register_page(__name__, path='/much-ado')

layout = html.Div([
    dcc.Store(id='ado-store', data={}),
    
    html.Div([
        dcc.Link('← Back to Game Hub', href='/games', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
        html.H1("✍️ Much Ado About Counting", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Which of these words appears most frequently in this book?", style={'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '20px', 'fontStyle': 'italic'}),
        
        # Start Screen
        html.Div(id='ado-start-screen', children=[
            html.Button('🎭 Start Game', id='ado-start-btn', n_clicks=0, style={'padding': '20px 40px', 'fontSize': '24px', 'backgroundColor': THEME['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '12px', 'cursor': 'pointer', 'boxShadow': '0 4px 12px rgba(0,0,0,0.2)'})
        ], style={'textAlign': 'center', 'marginBottom': '40px'}),
        
        # Game Interface
        html.Div(id='ado-game-interface', style={'display': 'none'}, children=[
            
            # Book Card Container
            html.Div([
                html.Div([
                    html.H3(id='ado-book-title', style={'color': THEME['text_dark'], 'marginBottom': '10px'}),
                    html.P(id='ado-book-author', style={'color': THEME['text_light'], 'fontSize': '18px'}),
                    html.P(id='ado-book-genre', style={'color': THEME['accent'], 'fontSize': '14px', 'fontStyle': 'italic'})
                ], className='book-card', style={'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)', 'textAlign': 'center', 'maxWidth': '600px', 'margin': '0 auto', 'border': f'1px solid {THEME["border"]}'})
            ], style={'marginBottom': '40px'}),
            
            # Words Grid (2x2)
            html.Div(id='ado-words-grid', style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'maxWidth': '800px', 'margin': '0 auto'}),
            
            # Feedback & Next
            html.Div(id='ado-feedback-area', style={'textAlign': 'center', 'marginTop': '40px', 'display': 'none'}, children=[
                html.H2(id='ado-feedback-text', style={'marginBottom': '20px'}),
                html.Button('Next Round →', id='ado-next-btn', n_clicks=0, style={'padding': '15px 35px', 'fontSize': '20px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer'})
            ])
        ])
    ])
])

@callback(
    [Output('ado-game-interface', 'style'),
     Output('ado-start-screen', 'style'),
     Output('ado-book-title', 'children'),
     Output('ado-book-author', 'children'),
     Output('ado-book-genre', 'children'),
     Output('ado-words-grid', 'children'),
     Output('ado-store', 'data'),
     Output('ado-feedback-area', 'style'),
     Output('ado-feedback-text', 'children')],
    [Input('ado-start-btn', 'n_clicks'),
     Input('ado-next-btn', 'n_clicks'),
     Input({'type': 'ado-word-btn', 'index': dash.ALL}, 'n_clicks')],
    [State('ado-store', 'data')]
)
def ado_game_logic(start_click, next_click, word_clicks, state):
    ctx = dash.callback_context
    if not ctx.triggered: return [no_update] * 9
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # 1. START / NEXT ROUND
    if 'ado-start-btn' in trigger_id or 'ado-next-btn' in trigger_id:
        # Pick random book
        random_row = df.sample(1).iloc[0]
        book_id = int(random_row['book_number'])
        
        # Get Challenge Data
        challenge = game_utils.get_much_ado_challenge(book_id)
        
        # Retry if book has insufficient data
        retries = 0
        while not challenge and retries < 5:
            random_row = df.sample(1).iloc[0]
            book_id = int(random_row['book_number'])
            challenge = game_utils.get_much_ado_challenge(book_id)
            retries += 1
            
        if not challenge: return [no_update] * 9

        # Generate Buttons (Standard State)
        buttons = []
        for i, (word, count) in enumerate(challenge['options']):
            btn = html.Button(
                word, 
                id={'type': 'ado-word-btn', 'index': i}, 
                style={
                    'padding': '30px', 
                    'fontSize': '24px', 
                    'backgroundColor': THEME['card_bg'], 
                    'color': THEME['text_dark'],
                    'border': f'2px solid {THEME["secondary"]}', 
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'textTransform': 'capitalize',
                    'width': '100%'
                }
            )
            buttons.append(btn)
            
        def format_genres(g):
            if isinstance(g, list): return ", ".join(g)
            return str(g)

        return (
            {'display': 'block'}, {'display': 'none'},
            random_row['title'], random_row['author'], format_genres(random_row['genres']),
            buttons,
            challenge, # Save state
            {'display': 'none'}, ""
        )

    # 2. GUESSING (User clicked a word)
    if 'ado-word-btn' in trigger_id:
        # Get index of clicked button
        clicked_idx = ast.literal_eval(trigger_id.split('.')[0])['index']
        
        # Check correctness
        correct_word = state['correct_word']
        options = state['options'] # List of [word, count]
        
        selected_word = options[clicked_idx][0]
        is_correct = (selected_word == correct_word)
        
        # Re-render buttons with colors & counts
        new_buttons = []
        for i, (word, count) in enumerate(options):
            
            # Determine Color
            bg_color = THEME['card_bg']
            text_color = THEME['text_dark']
            border_color = THEME['secondary']
            
            if word == correct_word:
                bg_color = '#d4edda' # Greenish
                border_color = 'green'
                text_color = 'green'
            elif i == clicked_idx and not is_correct:
                bg_color = '#f8d7da' # Reddish
                border_color = 'red'
                text_color = 'red'
                
            # Update Button Content to show COUNT
            new_buttons.append(html.Button(
                [
                    html.Div(word, style={'fontSize': '24px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    html.Div(f"{count:,} times", style={'fontSize': '16px', 'opacity': '0.8'})
                ],
                id={'type': 'ado-word-btn-disabled', 'index': i}, # Change ID to disable click handling
                disabled=True,
                style={
                    'padding': '20px', 
                    'backgroundColor': bg_color, 
                    'color': text_color,
                    'border': f'3px solid {border_color}', 
                    'borderRadius': '10px',
                    'textTransform': 'capitalize',
                    'width': '100%'
                }
            ))
            
        feedback_text = "🎉 Correct!" if is_correct else "❌ Wrong!"
        feedback_color = "green" if is_correct else "red"
        feedback_header = html.Span(feedback_text, style={'color': feedback_color, 'fontSize': '32px', 'fontWeight': 'bold'})

        return (
            no_update, no_update, no_update, no_update, no_update,
            new_buttons, # Update grid with reveal
            state,
            {'display': 'block', 'textAlign': 'center', 'marginTop': '40px'}, feedback_header
        )

    return [no_update] * 9