import sqlite3
import pandas as pd
import random

DB_PATH = 'project_books.db'

# A standard list of stopwords to filter out for the "Game" and "Clean" views
STOPWORDS = set([
    'the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 
    'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'this', 
    'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 
    'were', 'we', 'when', 'your', 'can', 'said', 'there', 'use', 'an', 'each', 
    'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 
    'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 
    'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go', 
    'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 
    'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'mr', 'mrs', 'miss', 'said',
    's', 't', 'don', 've', 'll', 're', 'm', 'd' # Added common contractions just in case
])

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Helper to verify which books actually exist in the DB
def filter_valid_book_ids(candidate_ids):
    """
    Takes a list of IDs (from CSV) and returns only those 
    that actually exist in the SQLite database.
    """
    conn = get_db_connection()
    try:
        # Get all distinct book IDs that have data
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT book_id FROM word_counts")
        # Set of IDs present in DB
        db_ids = set(row[0] for row in cursor.fetchall())
        
        # Return intersection (IDs in both CSV and DB)
        valid_ids = [bid for bid in candidate_ids if bid in db_ids]
        return valid_ids
    except Exception as e:
        print(f"Error filtering IDs: {e}")
        return []
    finally:
        conn.close()

def get_book_stats(book_id):
    """
    Returns the total word count and total unique word count for a book.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Sum of counts = Total words in book
        # Count of rows = Unique words found
        cursor.execute("SELECT SUM(count), COUNT(word) FROM word_counts WHERE book_id = ?", (book_id,))
        result = cursor.fetchone()
        
        total_words = result[0] if result[0] else 0
        unique_words = result[1] if result[1] else 0
        
        return {
            'total_words': total_words, 
            'unique_words': unique_words
        }
    except Exception as e:
        print(f"Error fetching stats for book {book_id}: {e}")
        return {'total_words': 0, 'unique_words': 0}
    finally:
        conn.close()

def get_book_word_counts(book_id, limit=None, remove_stopwords=True):
    """
    Fetches word counts for a specific book.
    Returns a DataFrame: [word, count]
    
    SMART FETCH UPDATE:
    If we are removing stopwords, we initially fetch 10x the requested limit
    from SQL to ensure we have enough words left after filtering.
    """
    conn = get_db_connection()
    
    query = """
    SELECT word, count 
    FROM word_counts 
    WHERE book_id = ? 
    ORDER BY count DESC 
    """
    
    params = [book_id]
    
    # Decide how many rows to ask SQL for
    fetch_limit = limit
    if limit is not None and remove_stopwords:
        # Fetch a buffer (10x) because top words are mostly stopwords
        fetch_limit = limit * 10
    
    if fetch_limit is not None:
        query += " LIMIT ?"
        params.append(fetch_limit)
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
        
        if remove_stopwords:
            # Filter out stopwords using the set
            df = df[~df['word'].str.lower().isin(STOPWORDS)]
        
        # If we fetched a buffer, truncate back to the user's requested limit
        if limit is not None:
            df = df.head(limit)
        
        return df
    except Exception as e:
        print(f"Error fetching data for book {book_id}: {e}")
        return pd.DataFrame(columns=['word', 'count'])
    finally:
        conn.close()

def get_mystery_book_clues(book_id, difficulty='easy'):
    """
    Gets 'Signature Words' for a book to use as clues.
    These are high-frequency words that are NOT stopwords.
    """
    # For clues, we still want a small limit so we don't fetch 10,000 words
    df = get_book_word_counts(book_id, limit=50, remove_stopwords=True)
    
    if df.empty:
        return []
    
    # Simple difficulty logic:
    # Easy = Top unique words (e.g., 'whale', 'ahab')
    # Hard = Words further down the list (more obscure)
    if difficulty == 'easy':
        clues = df['word'].head(5).tolist()
    else:
        clues = df['word'].iloc[10:15].tolist()
        
    return clues

def get_stat_attack_challenge(available_book_ids):
    """
    Picks two random books and finds a common word between them.
    Returns dict with book IDs, the word, and the counts.
    """
    # Filter IDs first to ensure we pick books with data
    valid_ids = filter_valid_book_ids(available_book_ids)
    if len(valid_ids) < 2: return None

    # Try a few times to find a good match
    for _ in range(10):
        try:
            id1, id2 = random.sample(valid_ids, 2)
            
            # Get top 200 words for both (filtered)
            df1 = get_book_word_counts(id1, limit=200, remove_stopwords=True)
            df2 = get_book_word_counts(id2, limit=200, remove_stopwords=True)
            
            if df1.empty or df2.empty: continue
            
            # Find common words
            common_words = list(set(df1['word']) & set(df2['word']))
            
            if not common_words: continue
            
            # Pick a random word from the intersection
            target_word = random.choice(common_words)
            
            count1 = int(df1[df1['word'] == target_word].iloc[0]['count'])
            count2 = int(df2[df2['word'] == target_word].iloc[0]['count'])
            
            # Avoid cases where counts are identical or too close (boring)
            if count1 == count2: continue
            
            return {
                'id_1': id1,
                'id_2': id2,
                'word': target_word,
                'count_1': count1,
                'count_2': count2
            }
            
        except Exception as e:
            print(f"Error generating stat attack: {e}")
            continue
            
    return None

def get_much_ado_challenge(book_id):
    """
    Generates a 'Most Frequent Word' challenge for a specific book.
    Returns:
    - correct_word: (word, count)
    - options: List of 4 (word, count) tuples, shuffled
    """
    # Get top 200 words (filtered)
    df = get_book_word_counts(book_id, limit=200, remove_stopwords=True)
    
    if len(df) < 50:
        return None
        
    # 1. Pick Winner (From Top 10)
    winner_row = df.iloc[random.randint(0, 5)] # Pick from absolute top
    winner = (winner_row['word'], int(winner_row['count']))
    
    # 2. Pick 3 Distractors (From Rank 50-150)
    # They look like real words but are statistically less frequent
    distractors_df = df.iloc[50:150].sample(3)
    distractors = [(r['word'], int(r['count'])) for _, r in distractors_df.iterrows()]
    
    # Combine and Shuffle
    options = [winner] + distractors
    random.shuffle(options)
    
    return {
        'correct_word': winner[0],
        'options': options # List of (word, count)
    }

def get_red_herring_challenge(available_book_ids):
    """
    Generates a 'Find the Imposter' challenge.
    Returns:
    - target_id: The ID of the book we display
    - options: List of dicts [{'word': 'whale', 'is_herring': False}, ...]
    """
    # Filter IDs first to ensure we pick books with data
    valid_ids = filter_valid_book_ids(available_book_ids)
    if len(valid_ids) < 2: return None

    for _ in range(10): # Retry loop
        try:
            target_id, distractor_id = random.sample(valid_ids, 2)
            
            # INCREASED LIMIT: Use top 200 words to ensure we find enough candidates
            df_target = get_book_word_counts(target_id, limit=200, remove_stopwords=True)
            target_words = set(df_target['word'].tolist())
            
            if len(target_words) < 20: continue
            
            # INCREASED LIMIT: Use top 200 words for distractor as well
            df_distractor = get_book_word_counts(distractor_id, limit=200, remove_stopwords=True)
            distractor_words = df_distractor['word'].tolist()
            
            if len(distractor_words) < 20: continue
            
            # Find a "Red Herring": A top word in Distractor that is NOT in Target's top list
            candidates = [w for w in distractor_words if w not in target_words]
            
            if not candidates: continue
            
            herring_word = random.choice(candidates)
            # Retrieve count for herring in distractor book for metadata
            herring_count = int(df_distractor[df_distractor['word'] == herring_word].iloc[0]['count'])
            
            # Pick 3 "True" words from Target
            true_words = random.sample(list(target_words), 3)
            
            # Build Options
            options = []
            options.append({
                'word': herring_word, 
                'is_herring': True, 
                'origin': distractor_id,
                'count': herring_count # Count from origin (Distractor)
            })
            
            for w in true_words:
                # Retrieve count for true word in target book
                w_count = int(df_target[df_target['word'] == w].iloc[0]['count'])
                options.append({
                    'word': w, 
                    'is_herring': False, 
                    'origin': target_id,
                    'count': w_count # Count from origin (Target)
                })
                
            random.shuffle(options)
            
            return {
                'target_id': target_id,
                'distractor_id': distractor_id,
                'options': options
            }
            
        except Exception as e:
            print(f"Error generating red herring: {e}")
            continue
            
    return None

def get_book_clue_challenge(available_book_ids):
    """
    Generates a 'Match the Words to the Book' challenge.
    Returns:
    - target_id: The correct book ID
    - clues: List of Top 15 words
    - options: List of 4 book IDs (1 Correct + 3 Random Distractors)
    """
    valid_ids = filter_valid_book_ids(available_book_ids)
    if len(valid_ids) < 4: return None # Need at least 4 valid books

    for _ in range(10):
        try:
            # 1. Pick Target and Distractors
            target_id = random.choice(valid_ids)
            distractors = random.sample([bid for bid in valid_ids if bid != target_id], 3)
            
            # 2. Get Clues (Top 15 Words)
            # SMART FETCH is handled inside get_book_word_counts now.
            # We ask for 15, it fetches 150, filters, and returns 15.
            df_target = get_book_word_counts(target_id, limit=15, remove_stopwords=True)
            
            if len(df_target) < 15: continue
            
            clues = df_target['word'].tolist()
            
            # 3. Build Options List
            options = [target_id] + distractors
            random.shuffle(options)
            
            return {
                'target_id': target_id,
                'clues': clues,
                'options': options
            }
            
        except Exception as e:
            print(f"Error generating book clue challenge: {e}")
            continue
            
    return None