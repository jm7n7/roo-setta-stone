import dash
from dash import dcc, html, Input, Output, State, callback, no_update
from data_loader import THEME, df
import game_utils
import ast

dash.register_page(__name__, path='/mystery')

layout = html.Div([
    dcc.Store(id='clue-store', data={}),
    
    html.Div([
        dcc.Link('← Back to Game Hub', href='/games', style={'color': THEME['primary'], 'fontSize': '16px', 'marginBottom': '20px', 'display': 'inline-block', 'textDecoration': 'none'}),
        html.H1("🕵️ A Book with a Clue", style={'textAlign': 'center', 'color': THEME['text_dark']}),
        html.P("We found this 'Fingerprint' of words. Which book does it belong to?", style={'textAlign': 'center', 'marginBottom': '40px', 'fontSize': '20px', 'fontStyle': 'italic'}),
        
        # Start Screen
        html.Div(id='clue-start-screen', children=[
            html.Button('📂 Open Case File', id='clue-start-btn', n_clicks=0, style={'padding': '20px 40px', 'fontSize': '24px', 'backgroundColor': THEME['accent'], 'color': 'white', 'border': 'none', 'borderRadius': '12px', 'cursor': 'pointer', 'boxShadow': '0 4px 12px rgba(0,0,0,0.2)'}),
            html.P(id='clue-error-msg', style={'color': 'red', 'marginTop': '15px', 'fontWeight': 'bold'})
        ], style={'textAlign': 'center', 'marginBottom': '40px'}),
        
        # Game Interface
        html.Div(id='clue-game-interface', style={'display': 'none'}, children=[
            
            # Clues Container (The Fingerprint)
            html.Div([
                html.H3("EVIDENCE: Top 15 Words", style={'color': THEME['text_light'], 'marginBottom': '15px', 'textTransform': 'uppercase', 'letterSpacing': '1px'}),
                html.Div(id='clue-clues-display', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'gap': '10px'})
            ], style={'textAlign': 'center', 'marginBottom': '50px', 'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.05)', 'border': f'1px solid {THEME["border"]}', 'maxWidth': '800px', 'margin': '0 auto 50px auto'}),
            
            # Suspects Grid (4 Book Cards)
            html.Div(id='clue-options-grid', style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '25px', 'maxWidth': '1000px', 'margin': '0 auto'}),
            
            # Feedback & Next
            html.Div(id='clue-feedback-area', style={'textAlign': 'center', 'marginTop': '40px', 'display': 'none'}, children=[
                html.H2(id='clue-feedback-text', style={'marginBottom': '20px'}),
                html.Div(id='clue-feedback-detail', style={'fontSize': '18px', 'color': THEME['text_light'], 'marginBottom': '20px'}),
                html.Button('Next Case →', id='clue-next-btn', n_clicks=0, style={'padding': '15px 35px', 'fontSize': '20px', 'backgroundColor': THEME['primary'], 'color': 'white', 'border': 'none', 'borderRadius': '8px', 'cursor': 'pointer'})
            ])
        ])
    ])
])

@callback(
    [Output('clue-game-interface', 'style'),
     Output('clue-start-screen', 'style'),
     Output('clue-clues-display', 'children'),
     Output('clue-options-grid', 'children'),
     Output('clue-store', 'data'),
     Output('clue-feedback-area', 'style'),
     Output('clue-feedback-text', 'children'),
     Output('clue-feedback-detail', 'children'),
     Output('clue-error-msg', 'children')],
    [Input('clue-start-btn', 'n_clicks'),
     Input('clue-next-btn', 'n_clicks'),
     Input({'type': 'clue-book-btn', 'index': dash.ALL}, 'n_clicks')],
    [State('clue-store', 'data')]
)
def clue_game_logic(start_click, next_click, book_clicks, state):
    ctx = dash.callback_context
    if not ctx.triggered: return [no_update] * 9
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # 1. START / NEXT CASE
    if 'clue-start-btn' in trigger_id or 'clue-next-btn' in trigger_id:
        available_ids = df['book_number'].tolist()
        
        # Retry logic
        challenge = None
        for _ in range(5):
            challenge = game_utils.get_book_clue_challenge(available_ids)
            if challenge: break
        
        if not challenge: 
            return (
                no_update, {'display': 'block'}, 
                "", "", no_update, no_update, "", "",
                "⚠️ Could not generate a challenge (Low data). Please try again!"
            )
        
        # Generate Clue Badges
        clue_badges = [html.Span(word, style={'padding': '8px 15px', 'backgroundColor': '#f0f0f0', 'color': '#333', 'borderRadius': '20px', 'fontSize': '16px', 'fontWeight': 'bold', 'border': '1px solid #ddd'}) for word in challenge['clues']]
        
        # Generate Book Cards (The Suspects)
        suspect_cards = []
        
        # Helper to format genres
        def format_genres(g):
            if isinstance(g, list): return ", ".join(g)
            return str(g)

        for i, book_id in enumerate(challenge['options']):
            # Get metadata for this book
            book_meta = df[df['book_number'] == book_id].iloc[0]
            
            # Fetch Stats
            stats = game_utils.get_book_stats(book_id)
            stats_text = f"{stats['total_words']:,} Words | {stats['unique_words']:,} Unique"
            
            card = html.Button(
                [
                    html.H3(book_meta['title'], style={'fontSize': '20px', 'color': THEME['text_dark'], 'marginBottom': '10px', 'minHeight': '50px'}),
                    html.P(book_meta['author'], style={'color': THEME['text_light'], 'fontSize': '16px', 'marginBottom': '5px'}),
                    html.P(format_genres(book_meta['genres']), style={'color': THEME['accent'], 'fontSize': '12px', 'fontStyle': 'italic', 'marginBottom': '10px'}),
                    # Display Stats on Button
                    html.Div(stats_text, style={'fontSize': '14px', 'color': THEME['text_dark'], 'fontWeight': 'bold', 'opacity': '0.8', 'paddingTop': '10px', 'borderTop': f'1px solid {THEME["border"]}'})
                ],
                id={'type': 'clue-book-btn', 'index': i},
                style={
                    'padding': '25px', 
                    'backgroundColor': 'white', 
                    'border': f'2px solid {THEME["border"]}', 
                    'borderRadius': '12px',
                    'cursor': 'pointer',
                    'textAlign': 'center',
                    'width': '100%',
                    'transition': 'all 0.2s',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.05)'
                }
            )
            suspect_cards.append(card)
            
        return (
            {'display': 'block'}, {'display': 'none'},
            clue_badges,
            suspect_cards,
            challenge, # Save state
            {'display': 'none'}, "", "", ""
        )

    # 2. GUESSING
    if 'clue-book-btn' in trigger_id:
        try:
            trigger_dict = ast.literal_eval(trigger_id.split('.')[0])
            clicked_idx = trigger_dict['index']
        except:
            return [no_update] * 9

        options = state['options'] # List of Book IDs
        target_id = state['target_id']
        
        clicked_id = options[clicked_idx]
        is_correct = (clicked_id == target_id)
        
        # Re-render cards with feedback
        new_cards = []
        for i, book_id in enumerate(options):
            book_meta = df[df['book_number'] == book_id].iloc[0]
            
            # Fetch Stats (Re-fetch needed to display on disabled buttons)
            stats = game_utils.get_book_stats(book_id)
            stats_text = f"{stats['total_words']:,} Words | {stats['unique_words']:,} Unique"
            
            # Default Styles
            bg_color = 'white'
            border_color = THEME['border']
            opacity = "0.6"
            
            if book_id == target_id:
                # The True Culprit -> Green
                bg_color = '#d4edda'
                border_color = 'green'
                opacity = "1.0"
            elif i == clicked_idx and not is_correct:
                # Wrong Guess -> Red
                bg_color = '#f8d7da'
                border_color = 'red'
                opacity = "1.0"
                
            # Helper to format genres
            def format_genres(g):
                if isinstance(g, list): return ", ".join(g)
                return str(g)

            new_cards.append(html.Button(
                [
                    html.H3(book_meta['title'], style={'fontSize': '20px', 'color': THEME['text_dark'], 'marginBottom': '10px', 'minHeight': '50px'}),
                    html.P(book_meta['author'], style={'color': THEME['text_light'], 'fontSize': '16px', 'marginBottom': '5px'}),
                    html.P(format_genres(book_meta['genres']), style={'color': THEME['accent'], 'fontSize': '12px', 'fontStyle': 'italic', 'marginBottom': '10px'}),
                    # Keep Stats visible
                    html.Div(stats_text, style={'fontSize': '14px', 'color': THEME['text_dark'], 'fontWeight': 'bold', 'opacity': '0.8', 'paddingTop': '10px', 'borderTop': f'1px solid {border_color}'}) # Use dynamic border color
                ],
                id={'type': 'clue-book-btn-disabled', 'index': i},
                disabled=True,
                style={
                    'padding': '25px', 
                    'backgroundColor': bg_color, 
                    'border': f'3px solid {border_color}', 
                    'borderRadius': '12px',
                    'textAlign': 'center',
                    'width': '100%',
                    'opacity': opacity,
                    'boxShadow': 'none'
                }
            ))
            
        feedback_text = "🎉 You found the book!" if is_correct else "❌ Not quite!"
        feedback_color = "green" if is_correct else "red"
        
        detail_text = html.Span([
            "These words appear most frequently in this book."
        ])
        
        return (
            no_update, no_update, no_update,
            new_cards,
            state,
            {'display': 'block', 'textAlign': 'center', 'marginTop': '40px'},
            html.Span(feedback_text, style={'color': feedback_color, 'fontSize': '32px', 'fontWeight': 'bold'}),
            detail_text,
            ""
        )

    return [no_update] * 9