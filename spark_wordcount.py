from pyspark.sql import SparkSession
import re
import os
import sys

# --- Environment Setup ---
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# --- Configuration ---
INPUT_DIR = 'project_books_clean'
OUTPUT_DIR = 'book_word_counts_output'
PARTITION_COUNT = 200 

def tokenize_and_map(file_data):
    """
    Input: (full_file_path, content_string)
    
    Logic:
    1. Extract Book ID.
    2. Clean/Tokenize text (handling both straight ' and curly ’ apostrophes).
    3. Emit ((book_id, word), 1)
    """
    full_path, content = file_data
    
    # --- 1. ID Extraction ---
    filename = os.path.basename(full_path)
    try:
        book_id = filename.split('_')[0]
    except IndexError:
        book_id = filename 
        
    # --- 2. Tokenization & Cleaning ---
    content = content.lower()
    
    # UPDATED REGEX:
    # [a-z]+        : Match start of word
    # (?: ... )?    : Optional non-capturing group
    # ['’]          : Match EITHER standard apostrophe OR curly apostrophe
    # [a-z]+        : Match following letters
    words = re.findall(r"[a-z]+(?:['’][a-z]+)?", content)
    
    results = []
    for word in words:
        results.append(((book_id, word), 1))
            
    return results

def main():
    spark = SparkSession.builder \
        .appName("GutenbergBookWordCount") \
        .getOrCreate()

    print(f"--- Starting Job: Processing {INPUT_DIR} ---")

    # 1. Ingest
    input_rdd = spark.sparkContext.wholeTextFiles(f"{INPUT_DIR}/*.txt", minPartitions=PARTITION_COUNT)

    # 2. Map
    mapped_rdd = input_rdd.flatMap(tokenize_and_map)

    # 3. Reduce
    counts_rdd = mapped_rdd.reduceByKey(lambda a, b: a + b)

    # 4. Transform
    final_rdd = counts_rdd.map(lambda x: (x[0][0], x[0][1], x[1]))

    # 5. DataFrame & Export
    df = final_rdd.toDF(["book_id", "word", "count"])

    print("--- Analysis Complete. Writing to CSV ---")
    
    df.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(OUTPUT_DIR)
        
    spark.stop()

if __name__ == "__main__":
    main()