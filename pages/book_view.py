import dash
from dash import dcc, html, dash_table
import game_utils
from data_loader import THEME, df

# Handles /book/15, /book/123, etc.
dash.register_page(__name__, path_template="/book/<book_id>")

def layout(book_id=None):
    if not book_id: return html.Div("No book selected")
    
    # Get Metadata
    try:
        book_id_int = int(book_id)
        book_meta = df[df['book_number'] == book_id_int].iloc[0]
    except (ValueError, IndexError):
        return html.Div(html.H1("Book not found in metadata"))

    # Get Spark Data from SQLite
    stats_df = game_utils.get_book_word_counts(book_id_int, limit=None, remove_stopwords=False)
    
    if stats_df.empty:
         return html.Div([
            html.H1(f"Analysis for: {book_meta['title']}"),
            html.P("No analytics data found in database. Did you run the Spark job for this book?", style={'color': 'red'})
        ])

    return html.Div([
        dcc.Link('← Back to Explorer', href='/search', style={'fontSize': '18px', 'color': THEME['primary']}),
        html.H1(book_meta['title'], style={'marginTop': '20px'}),
        html.H3(f"by {book_meta['author']}", style={'color': THEME['text_light']}),
        
        # Stats Container
        html.Div([
            html.Div([
                html.H4(f"Detailed Word Counts (Total Unique Words: {len(stats_df):,})"),
                dash_table.DataTable(
                    data=stats_df.to_dict('records'),
                    columns=[{'name': 'Word', 'id': 'word'}, {'name': 'Count', 'id': 'count'}],
                    page_size=20,
                    style_header={'backgroundColor': THEME['primary'], 'color': 'white', 'fontWeight': 'bold'},
                    style_cell={'textAlign': 'left', 'fontFamily': 'sans-serif'},
                    style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': '#f9f9f9'}],
                    sort_action='native',
                    filter_action='native'
                )
            ], style={'width': '100%', 'display': 'block'})
        ], style={'marginTop': '40px', 'backgroundColor': 'white', 'padding': '30px', 'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.1)'})
    ])
