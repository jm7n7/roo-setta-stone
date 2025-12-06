import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from data_loader import THEME, df
import game_utils
import ast

dash.register_page(__name__, path='/little-red-herring')

layout = html.Div([
    dcc.Store(id='herring-store', data={}),
    
    html.Div([
        dcc.Link('← Back to Game Hub', href='/games', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
        html.H1("🐟 Little Red Herring", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("Three words belong to this book. One is an imposter. Find the Red Herring!", style={'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '20px', 'fontStyle': 'italic'}),
        
        # Start Screen
        html.Div(id='herring-start-screen', children=[
            html.Button('🕵️ Start Investigation', id='herring-start-btn', n_clicks=0, style={'padding': '20px 40px', 'fontSize': '24px', 'backgroundColor': THEME['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '12px', 'cursor': 'pointer', 'boxShadow': '0 4px 12px rgba(0,0,0,0.2)'}),
            html.P(id='herring-error-msg', style={'color': 'red', 'marginTop': '15px', 'fontWeight': 'bold'})
        ], style={'textAlign': 'center', 'marginBottom': '40px'}),
        
        # Game Interface
        html.Div(id='herring-game-interface', style={'display': 'none'}, children=[
            
            # Target Book Header
            html.Div([
                html.H2("The Book:", style={'color': THEME['secondary'], 'fontSize': '18px', 'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '10px'}),
                html.H1(id='herring-book-title', style={'color': THEME['text_dark'], 'fontSize': '42px', 'margin': '0 0 10px 0', 'fontFamily': "'Playfair Display', serif"}),
                html.H3(id='herring-book-author', style={'color': THEME['text_light'], 'fontSize': '22px', 'fontWeight': 'normal'}),
                # NEW: Genre Display
                html.P(id='herring-book-genre', style={'color': THEME['accent'], 'fontSize': '16px', 'marginTop': '15px', 'fontStyle': 'italic'})
            ], style={'textAlign': 'center', 'marginBottom': '50px', 'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': f'1px solid {THEME["border"]}', 'maxWidth': '800px', 'margin': '0 auto 50px auto'}),
            
            # Words Grid (2x2)
            html.Div(id='herring-words-grid', style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'maxWidth': '800px', 'margin': '0 auto'}),
            
            # Feedback & Next
            html.Div(id='herring-feedback-area', style={'textAlign': 'center', 'marginTop': '40px', 'display': 'none'}, children=[
                html.H2(id='herring-feedback-text', style={'marginBottom': '20px'}),
                html.Div(id='herring-feedback-detail', style={'fontSize': '18px', 'color': THEME['text_light'], 'marginBottom': '20px', 'maxWidth': '800px', 'margin': '0 auto 20px auto', 'lineHeight': '1.6'}),
                html.Button('Next Case →', id='herring-next-btn', n_clicks=0, style={'padding': '15px 35px', 'fontSize': '20px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer'})
            ])
        ])
    ])
])

@callback(
    [Output('herring-game-interface', 'style'),
     Output('herring-start-screen', 'style'),
     Output('herring-book-title', 'children'),
     Output('herring-book-author', 'children'),
     Output('herring-book-genre', 'children'), # Added genre output
     Output('herring-words-grid', 'children'),
     Output('herring-store', 'data'),
     Output('herring-feedback-area', 'style'),
     Output('herring-feedback-text', 'children'),
     Output('herring-feedback-detail', 'children'),
     Output('herring-error-msg', 'children')],
    [Input('herring-start-btn', 'n_clicks'),
     Input('herring-next-btn', 'n_clicks'),
     Input({'type': 'herring-word-btn', 'index': dash.ALL}, 'n_clicks')],
    [State('herring-store', 'data')]
)
def herring_game_logic(start_click, next_click, word_clicks, state):
    ctx = dash.callback_context
    if not ctx.triggered: return [no_update] * 11
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # 1. START / NEXT CASE
    if 'herring-start-btn' in trigger_id or 'herring-next-btn' in trigger_id:
        available_ids = df['book_number'].tolist()
        
        # Retry logic: Try 5 times to get a valid challenge
        challenge = None
        for _ in range(5):
            challenge = game_utils.get_red_herring_challenge(available_ids)
            if challenge:
                break
        
        # If still failing after retries, show error on start screen
        if not challenge: 
            return (
                no_update, {'display': 'block'}, # Keep start screen visible
                "", "", "", "", no_update, no_update, "", "", "",
                "⚠️ Could not generate a challenge (low data). Please try again!" # Error msg
            )
        
        target_meta = df[df['book_number'] == challenge['target_id']].iloc[0]
        
        # Helper for genres
        def format_genres(g):
            if isinstance(g, list): return ", ".join(g)
            return str(g)
        
        # Generate Buttons
        buttons = []
        for i, opt in enumerate(challenge['options']):
            buttons.append(html.Button(
                opt['word'], 
                id={'type': 'herring-word-btn', 'index': i}, 
                style={
                    'padding': '30px', 
                    'fontSize': '24px', 
                    'backgroundColor': THEME['card_bg'], 
                    'color': THEME['text_dark'],
                    'border': f'2px solid {THEME["secondary"]}', 
                    'borderRadius': '10px',
                    'cursor': 'pointer',
                    'textTransform': 'capitalize',
                    'width': '100%',
                    'transition': 'all 0.2s'
                }
            ))
            
        return (
            {'display': 'block'}, {'display': 'none'},
            target_meta['title'], target_meta['author'], format_genres(target_meta['genres']),
            buttons,
            challenge, # Save state
            {'display': 'none'}, "", "", "" # Clear error
        )

    # 2. GUESSING
    if 'herring-word-btn' in trigger_id:
        try:
            # Parse the trigger ID dictionary string safely
            trigger_dict = ast.literal_eval(trigger_id.split('.')[0])
            clicked_idx = trigger_dict['index']
        except:
            return [no_update] * 11

        options = state['options']
        clicked_opt = options[clicked_idx]
        is_correct = clicked_opt['is_herring']
        
        # Get metadata for feedback
        target_id = state['target_id']
        distractor_id = state['distractor_id']
        
        target_rows = df[df['book_number'] == target_id]
        target_title = target_rows.iloc[0]['title'] if not target_rows.empty else "Unknown Book"
        
        distractor_rows = df[df['book_number'] == distractor_id]
        distractor_title = distractor_rows.iloc[0]['title'] if not distractor_rows.empty else "Unknown Book"
        
        # Reveal Buttons
        new_buttons = []
        for i, opt in enumerate(options):
            bg_color = THEME['card_bg']
            border_color = THEME['secondary']
            opacity = "0.6" # Fade non-relevant words
            
            # Show Count on Reveal only for REAL words
            if not opt['is_herring']:
                count_display = f"{opt['count']:,} times"
            else:
                count_display = "IMPOSTER" # Hide fake count to avoid confusion
            
            if opt['is_herring']:
                # The Correct Answer (The Herring) -> Always Green
                bg_color = '#d4edda' 
                border_color = 'green'
                opacity = "1.0"
                    
            elif i == clicked_idx and not is_correct: 
                # User clicked a normal word (Wrong) -> Red
                bg_color = '#f8d7da'
                border_color = 'red'
                opacity = "1.0"
            
            new_buttons.append(html.Button(
                [
                    html.Div(opt['word'], style={'fontSize': '24px', 'fontWeight': 'bold', 'marginBottom': '5px'}),
                    html.Div(count_display, style={'fontSize': '16px', 'opacity': '0.9', 'fontStyle': 'italic'})
                ],
                id={'type': 'herring-word-btn-disabled', 'index': i},
                disabled=True,
                style={
                    'padding': '20px', 
                    'backgroundColor': bg_color, 
                    'color': THEME['text_dark'],
                    'border': f'3px solid {border_color}', 
                    'borderRadius': '10px',
                    'textTransform': 'capitalize',
                    'width': '100%',
                    'opacity': opacity
                }
            ))
            
        # Construct Feedback Text
        if is_correct:
            feedback_header = html.Span("🎉 You caught the Herring!", style={'color': 'green', 'fontSize': '32px', 'fontWeight': 'bold'})
            feedback_detail = html.Span([
                html.Span(f"'{clicked_opt['word']}'", style={'fontWeight': 'bold'}),
                " never appears in ",
                html.Span(f"'{target_title}'", style={'fontStyle': 'italic'}),
                ". It is actually a top word from ",
                html.Span(f"'{distractor_title}'", style={'fontStyle': 'italic'}),
                "."
            ])
        else:
            # Find what the actual herring was to explain
            herring_word = next(o['word'] for o in options if o['is_herring'])
            
            feedback_header = html.Span("❌ Incorrect!", style={'color': 'red', 'fontSize': '32px', 'fontWeight': 'bold'})
            feedback_detail = html.Span([
                "That word belongs here! ",
                html.Span(f"'{clicked_opt['word']}'", style={'fontWeight': 'bold'}),
                " appears ",
                html.Span(f"{clicked_opt['count']:,}", style={'fontWeight': 'bold'}),
                " times in this book. The real imposter was ",
                html.Span(f"'{herring_word}'", style={'fontWeight': 'bold'}),
                "."
            ])

        return (
            no_update, no_update, no_update, no_update, no_update,
            new_buttons,
            state,
            {'display': 'block', 'textAlign': 'center', 'marginTop': '40px'},
            feedback_header,
            feedback_detail,
            ""
        )

    return [no_update] * 11
