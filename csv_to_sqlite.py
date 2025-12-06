import sqlite3
import pandas as pd
import glob
import os
import time

# --- Configuration ---
INPUT_DIR = 'book_word_counts_output'
DB_NAME = 'project_books.db'
CHUNK_SIZE = 1_000_000  # Process 1 million rows at a time to save RAM

def get_csv_files(folder_path):
    # Find the actual CSV file inside the Spark output folder
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {folder_path}")
    return csv_files

def create_database():
    # Delete existing DB if we are re-running to avoid duplicates
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed old database: {DB_NAME}")

    # Connect to SQLite (creates the file)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Table Structure
    # specific data types help SQLite optimize storage
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS word_counts (
        book_id INTEGER,
        word TEXT,
        count INTEGER
    );
    """
    cursor.execute(create_table_sql)
    conn.commit()
    return conn

def process_csv_to_sqlite(conn, csv_files):
    total_rows = 0
    start_time = time.time()

    for file_path in csv_files:
        print(f"Processing file: {file_path}")
        
        # Read CSV in chunks
        # This acts like a stream, so we never hold 2GB in RAM
        chunk_iterator = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
        
        for i, chunk in enumerate(chunk_iterator):
            # Write chunk to SQL
            # if_exists='append' adds to the table we created
            # index=False prevents pandas from adding its own row numbers
            chunk.to_sql('word_counts', conn, if_exists='append', index=False)
            
            rows_in_chunk = len(chunk)
            total_rows += rows_in_chunk
            
            elapsed = time.time() - start_time
            print(f"  ... Batch {i+1}: Inserted {rows_in_chunk:,} rows. (Total: {total_rows:,} | Time: {elapsed:.2f}s)")

    return total_rows

def add_index(conn):
    print("\n--- Creating Index (The Magic Step) ---")
    print("This might take a minute, but it makes future queries instant.")
    
    start_time = time.time()
    # Create an index on book_id so we can look up specific books instantly
    conn.execute("CREATE INDEX idx_book_id ON word_counts (book_id)")
    
    # Optional: Index on 'word' if you plan to search "Where does 'whale' appear?"
    # conn.execute("CREATE INDEX idx_word ON word_counts (word)")
    
    conn.commit()
    print(f"Index created in {time.time() - start_time:.2f} seconds.")

def verify_data(conn):
    print("\n--- Verification: Checking Moby Dick (Book 15) ---")
    
    # SQL Query to prove it works
    query = "SELECT word, count FROM word_counts WHERE book_id = 15 ORDER BY count DESC LIMIT 5"
    
    result_df = pd.read_sql_query(query, conn)
    print(result_df)

def main():
    print(f"--- Starting Conversion: CSV to SQLite ({DB_NAME}) ---")
    
    try:
        csv_files = get_csv_files(INPUT_DIR)
        conn = create_database()
        
        # 1. Insert Data
        total_rows = process_csv_to_sqlite(conn, csv_files)
        print(f"\nSuccessfully inserted {total_rows:,} rows.")
        
        # 2. Optimize
        add_index(conn)
        
        # 3. Verify
        verify_data(conn)
        
        conn.close()
        print("\n--- Database Ready ---")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()