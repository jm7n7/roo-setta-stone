import os

# 1. Setup Directories
raw_folder = 'project_books_raw'
clean_folder = 'project_books_clean'

# Ensure the output folder exists
os.makedirs(clean_folder, exist_ok=True)

# 2. Get list of files
files = [f for f in os.listdir(raw_folder) if f.endswith('.txt')]

if not files:
    print("No .txt files found in project_books_raw!")
    exit()

print(f"Found {len(files)} files. Starting cleanup...")

success_count = 0
fallback_count = 0

# 3. Loop through all files
for filename in files:
    input_path = os.path.join(raw_folder, filename)
    output_path = os.path.join(clean_folder, filename)
    
    # Read the file
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()
    except UnicodeDecodeError:
        # Fallback for older encodings if UTF-8 fails (common in Gutenberg)
        with open(input_path, 'r', encoding='latin-1') as f:
            raw_text = f.read()

    # 4. Define Markers
    # Most Gutenberg books follow this pattern, though some vary slightly.
    start_marker = "*** START OF"
    end_marker = "*** END OF"

    # 5. Find Indices
    start_index = raw_text.find(start_marker)
    end_index = raw_text.find(end_marker)

    # 6. Logic to Slice the Text
    if start_index != -1 and end_index != -1:
        # We found both!
        
        # We don't just want to start at the marker, we want to find the END of the marker line.
        # Usually the marker line ends with "***", so we look for the newline after the start index.
        start_of_content = raw_text.find('\n', start_index) + 1
        
        # Slice the text
        clean_text = raw_text[start_of_content:end_index]
        
        # Strip extra whitespace from ends
        clean_text = clean_text.strip()
        
        success_count += 1
    else:
        # Fallback: If markers aren't found, keep original text for now so we don't lose data
        clean_text = raw_text
        fallback_count += 1
        print(f"Warning: Markers not found in {filename} - Copied raw.")

    # 7. Write the cleaned file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(clean_text)

print(f"--- Processing Complete ---")
print(f"Successfully cleaned: {success_count}")
print(f"Fallback (copied raw): {fallback_count}")