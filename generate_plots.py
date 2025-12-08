import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import sqlite3
import os
import game_utils
from data_loader import THEME, df as df_meta

# --- Configuration ---
PLOT_DIR = 'assets/plots'
os.makedirs(PLOT_DIR, exist_ok=True)

def apply_custom_style(fig):
    """Applies the Roo-Setta Stone theme."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': "Sans-Serif", 'color': THEME['text_dark']},
        title={
            'font': {'family': "'Playfair Display', serif", 'size': 24},
            'y': 0.95, 'x': 0.5, 'xanchor': 'center'
        },
        xaxis=dict(
            showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor=THEME['border'],
            linewidth=1, title_font={'size': 14, 'family': "Sans-Serif"}, title_standoff=15
        ),
        yaxis=dict(
            showgrid=True, gridcolor='#e0e0e0', showline=True, linecolor=THEME['border'],
            linewidth=1, title_font={'size': 14}, title_standoff=15
        ),
        bargap=0.05,
        margin=dict(l=60, r=40, t=80, b=60)
    )
    return fig

def fetch_library_stats():
    """Helper: Fetches base stats."""
    print("   -> Querying Base Library Stats...")
    conn = sqlite3.connect(game_utils.DB_PATH)
    query = """
    SELECT book_id, SUM(count) as total_words, COUNT(word) as unique_words 
    FROM word_counts GROUP BY book_id
    """
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error fetching stats: {e}")
        conn.close()
        return pd.DataFrame()

# ==========================================
# 1. DISTRIBUTION PLOTS
# ==========================================
def generate_distribution_plots():
    print("--- Generating Distribution Plots ---")
    df_stats = fetch_library_stats()
    
    if df_stats.empty: return

    print("   -> Building Vocabulary Histogram...")
    fig_unique = px.histogram(
        df_stats, x='unique_words', nbins=50, 
        title='Distribution of Vocabulary Size',
        color_discrete_sequence=[THEME['secondary']]
    )
    fig_unique.update_xaxes(title_text="Unique Words (Vocabulary)")
    fig_unique.update_yaxes(title_text="Number of Books")
    fig_unique = apply_custom_style(fig_unique)
    pio.write_json(fig_unique, os.path.join(PLOT_DIR, 'dist_vocab.json'))
    print("✅ Distributions Saved.")

# ==========================================
# 2. ZIPF'S LAW PLOT (OPTIMIZED)
# ==========================================
def generate_zipf_plot():
    print("--- Generating Zipf's Law Plot ---")
    conn = sqlite3.connect(game_utils.DB_PATH)
    
    print("   -> Querying Word Frequencies (Heavy Query)...")
    query_zipf = "SELECT word, SUM(count) as frequency FROM word_counts GROUP BY word ORDER BY frequency DESC"
    
    try:
        df_zipf = pd.read_sql_query(query_zipf, conn)
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return

    conn.close()
    
    if not df_zipf.empty:
        df_zipf['rank'] = range(1, len(df_zipf) + 1)
        
        # --- OPTIMIZATION: Downsample for GitHub/Web Performance ---
        total_points = len(df_zipf)
        if total_points > 5000:
            print(f"   -> Downsampling from {total_points:,} points to reduce file size...")
            # 1. Keep the Top 1,000 words exactly (Critical for the head of the curve)
            head = df_zipf.iloc[:1000]
            
            # 2. Sample the Tail (Keep every 50th word)
            # This drastically reduces size while keeping the visual "cloud" shape
            tail = df_zipf.iloc[1000::50] 
            
            df_zipf = pd.concat([head, tail])
            print(f"   -> New point count: {len(df_zipf):,}")
        # -----------------------------------------------------------

        print("   -> Building Log-Log Scatter Plot...")
        fig_zipf = px.scatter(
            df_zipf, x='rank', y='frequency', log_x=True, log_y=True,
            title="Zipf's Law Validation", hover_data=['word'],
            color_discrete_sequence=[THEME['primary']], opacity=0.5
        )
        fig_zipf.update_xaxes(title_text="Rank (Log Scale)")
        fig_zipf.update_yaxes(title_text="Frequency (Log Scale)")
        fig_zipf = apply_custom_style(fig_zipf)
        
        pio.write_json(fig_zipf, os.path.join(PLOT_DIR, 'dist_zipf.json'))
        print("✅ Zipf Plot Saved.")
    else:
        print("Skipping: No Zipf data found.")

# ==========================================
# 3. AUTHOR PLOTS
# ==========================================
def generate_author_plots():
    print("--- Generating Author Plots ---")
    
    df_stats = fetch_library_stats()
    if df_stats.empty: return

    print("   -> Filtering Metadata...")
    author_counts = df_meta['author'].value_counts()
    valid_authors = author_counts[author_counts > 1].index.tolist()
    
    df_authors_filtered = df_meta[df_meta['author'].isin(valid_authors)].copy()
    df_authors_filtered['book_number'] = df_authors_filtered['book_number'].astype(int)
    df_stats['book_id'] = df_stats['book_id'].astype(int)

    merged_df = pd.merge(df_authors_filtered, df_stats, left_on='book_number', right_on='book_id', how='inner')

    if merged_df.empty: return

    author_stats = merged_df.groupby('author').agg({
        'total_words': 'mean',
        'unique_words': 'mean',
        'book_number': 'count'
    }).rename(columns={'book_number': 'book_count'}).reset_index()

    # Scatter Plot
    print("   -> Building Author Scatter Plot (Outliers Removed)...")
    cap_total = author_stats['total_words'].quantile(0.98)
    cap_unique = author_stats['unique_words'].quantile(0.98)
    
    scatter_df = author_stats[
        (author_stats['total_words'] <= cap_total) & 
        (author_stats['unique_words'] <= cap_unique)
    ]
    
    fig_scatter = px.scatter(
        scatter_df, 
        x='total_words', 
        y='unique_words', 
        hover_name='author', 
        size='book_count',
        title="Vocabulary vs. Verbosity (Outliers Removed)", 
        color_discrete_sequence=[THEME['accent']], 
        opacity=0.7
    )
    
    fig_scatter.update_traces(showlegend=False)
    fig_scatter.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=10, color=THEME['accent']),
        name='Size: Book Count'
    ))
    fig_scatter.update_layout(showlegend=True)
    
    fig_scatter.update_xaxes(title_text="Average Book Length (Words)")
    fig_scatter.update_yaxes(title_text="Average Vocabulary (Unique Words)")
    fig_scatter = apply_custom_style(fig_scatter)
    pio.write_json(fig_scatter, os.path.join(PLOT_DIR, 'author_scatter.json'))

    # Bar Chart
    print("   -> Building Top Authors Bar Chart...")
    top_vocab = author_stats.sort_values('unique_words', ascending=False).head(20)
    fig_bar = px.bar(
        top_vocab, x='unique_words', y='author', orientation='h',
        title="Top 20 Authors by Average Vocabulary", color_discrete_sequence=[THEME['primary']]
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_bar.update_xaxes(title_text="Average Unique Words per Book")
    fig_bar.update_yaxes(title_text="")
    fig_bar = apply_custom_style(fig_bar)
    pio.write_json(fig_bar, os.path.join(PLOT_DIR, 'author_bar.json'))

    print("✅ Author Plots Saved.")

# ==========================================
# 4. TOP WORDS TABLE
# ==========================================
def generate_top_word_table():
    print("--- Generating Author Signature Words Table ---")
    
    top_authors_series = df_meta['author'].value_counts().head(50)
    top_authors = top_authors_series.index.tolist()
    
    results = []
    
    conn = sqlite3.connect(game_utils.DB_PATH)
    stopwords = game_utils.STOPWORDS
    stopwords_sql = "'" + "','".join(stopwords) + "'"
    
    for author in top_authors:
        books = df_meta[df_meta['author'] == author]
        book_ids = books['book_number'].tolist()
        id_list = ",".join(map(str, book_ids))
        
        query = f"""
        SELECT word, SUM(count) as total_count
        FROM word_counts
        WHERE book_id IN ({id_list})
          AND word NOT IN ({stopwords_sql})
        GROUP BY word
        ORDER BY total_count DESC
        LIMIT 1
        """
        try:
            df_res = pd.read_sql_query(query, conn)
            if not df_res.empty:
                top_word = df_res.iloc[0]['word']
                count = int(df_res.iloc[0]['total_count'])
                book_count = int(top_authors_series[author])
                results.append({'Author': author, 'Books': book_count, 'Signature Word': top_word, 'Count': count})
        except Exception as e:
            print(f"Error processing {author}: {e}")
            
    conn.close()
    
    df_results = pd.DataFrame(results)
    df_results.to_json(os.path.join(PLOT_DIR, 'author_top_words.json'), orient='records')
    print("✅ Table Data Saved.")

# ==========================================
# 5. HAPAX LEGOMENA
# ==========================================
def generate_hapax_plot():
    print("--- Generating Hapax Legomena Plot (Top vs Bottom) ---")
    
    author_counts = df_meta['author'].value_counts()
    multi_book_counts = author_counts[author_counts > 1]
    
    if len(multi_book_counts) < 40:
        print("Not enough multi-book authors to do a Top 20/Bottom 20 split.")
        target_authors = multi_book_counts.index.tolist()
        labels = {auth: 'All' for auth in target_authors}
    else:
        top_20 = multi_book_counts.head(20)
        bottom_20 = multi_book_counts.tail(20)
        
        labels = {}
        for auth in top_20.index:
            labels[auth] = 'Top 20 (Prolific)'
        for auth in bottom_20.index:
            labels[auth] = 'Bottom 20 (Fewest Books)'
            
        target_authors = list(labels.keys())

    results = []
    conn = sqlite3.connect(game_utils.DB_PATH)
    
    print("   -> Calculating Ratios...")
    for author in target_authors:
        books = df_meta[df_meta['author'] == author]
        book_ids = books['book_number'].tolist()
        id_list = ",".join(map(str, book_ids))
        
        query = f"""
        SELECT word, SUM(count) as total_count
        FROM word_counts
        WHERE book_id IN ({id_list})
        GROUP BY word
        """
        
        try:
            df_words = pd.read_sql_query(query, conn)
            if not df_words.empty:
                total_unique = len(df_words)
                hapax_count = len(df_words[df_words['total_count'] == 1])
                ratio = (hapax_count / total_unique) * 100 if total_unique > 0 else 0
                
                results.append({
                    'Author': author,
                    'Hapax Ratio': ratio,
                    'Group': labels[author],
                    'Unique Words': total_unique,
                    'Hapax Words': hapax_count
                })
        except Exception as e:
            print(f"Error for {author}: {e}")
            
    conn.close()
    
    if not results: return
    
    df_hapax = pd.DataFrame(results).sort_values('Hapax Ratio', ascending=True)
    
    print("   -> Building Plot...")
    
    fig_hapax = px.bar(
        df_hapax, 
        x='Hapax Ratio', 
        y='Author', 
        orientation='h',
        title="One-Hit Wonders: Prolific vs. Casual Authors",
        color='Group', 
        color_discrete_map={
            'Top 20 (Prolific)': THEME['primary'],   
            'Bottom 20 (Fewest Books)': THEME['secondary']
        },
        hover_data=['Unique Words', 'Hapax Words']
    )
    
    fig_hapax.update_layout(yaxis={'categoryorder':'total ascending'})
    fig_hapax.update_xaxes(title_text="Percentage of Vocabulary Used Only Once")
    fig_hapax.update_yaxes(title_text="")
    fig_hapax = apply_custom_style(fig_hapax)
    
    pio.write_json(fig_hapax, os.path.join(PLOT_DIR, 'author_hapax.json'))
    print("✅ Hapax Plot Saved.")

if __name__ == "__main__":
    # Run all generators to freshen assets
    generate_distribution_plots()
    generate_zipf_plot() 
    generate_author_plots()
    generate_top_word_table()
    generate_hapax_plot()