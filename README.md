# The Roo-Setta Stone

A Big Data powered web application for analyzing and exploring the Project Gutenberg library (~24,000 books). Built with PySpark for distributed processing and Dash for interactive visualization.

**Created by:** Brady Maes and Joseph Marinello

## Overview

The Roo-Setta Stone processes and analyzes the vast Project Gutenberg library to uncover linguistic fingerprints and literary trends using modern Big Data architecture. The project employs a classic MapReduce strategy using PySpark to clean, tokenize, and count over 1.4 billion words, with results indexed in SQLite for real-time querying.

## Features

- **🔍 Book Search**: Search and explore books from the Gutenberg metadata with a detailed view of individual books with word frequency analysis
- **📊 Data Analysis Hub**: Explore library-wide statistics and author comparisons:
  - **Distributions**: Analyze vocabulary size distributions and Zipf's Law validation
  - **Author Stats**: Compare vocabulary depth, verbosity, and linguistic habits of top authors
- **🎮 Game Hub**: Interactive games based on book analysis:
  - Little Red Herring
  - Much Ado About Counting
  - A Book with a Clue
  - Tale of Two Counts
- **💞 Literary Pairings**: Discover unique book pairings and relationships:
  - **Unique Word Twins**: Books that share an extraordinarily high percentage of their unique vocabulary
  - **Individual Word Twins**: Books that use a specific word the exact same number of times

## Setup

### Prerequisites

- Python 3.7+
- Java (required for PySpark)
- PySpark 3.0.0+

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Pipeline Setup

The following steps will create all required data files from scratch. Run them in order:

**Step 1: Scrape Book Metadata**
```bash
# Run the Jupyter notebook to create gutenberg_metadata.csv
jupyter notebook book_web_scrapper.ipynb
```
This creates `gutenberg_metadata.csv` with book metadata from Project Gutenberg.

**Step 2: Download Books**
```bash
# Run the Jupyter notebook to download all books
jupyter notebook book_web_downloader.ipynb
```
This creates the `project_books_raw/` folder and downloads all book text files (~24,278 files).

**Step 3: Clean Book Files**
```bash
python book_file_cleanup.py
```
This creates the `project_books_clean/` folder with cleaned book text files (removes Gutenberg headers/footers).

**Step 4: Process Word Counts with PySpark**
```bash
python spark_wordcount.py
```
This performs the PySpark MapReduce job and creates the `book_word_counts_output/` folder with word count data.

**Step 5: Convert to SQLite Database**
```bash
python csv_to_sqlite.py
```
This transforms the word count CSV files into `project_books.db` SQLite database for fast querying.

**Step 6: Generate Static Plots (Optional)**
```bash
python generate_plots.py
```
This generates pre-computed visualizations for the Data Analysis Hub. The application will work without this step, but some charts may not be available.

**Step 7: Run the Application**
```bash
python app.py
```

**Step 8: Open in Browser**
Navigate to `http://localhost:8050` in your web browser.

## Data Processing

The project includes several data processing scripts:

- **`book_file_cleanup.py`**: Cleans raw book text files
- **`spark_wordcount.py`**: PySpark MapReduce job to count words across all books
- **`csv_to_sqlite.py`**: Converts processed word count data to SQLite database
- **`generate_plots.py`**: Generates static visualization plots for the Data Analysis Hub
- **`data_loader.py`**: Loads and preprocesses metadata for the web application
- **`find_unique_twins.py`**: Finds unique book pairings based on word patterns

## Project Structure

```
.
├── app.py                    # Main Dash application
├── requirements.txt          # Python dependencies
├── gutenberg_metadata.csv    # Book metadata (required)
├── project_books.db          # SQLite database with word counts
├── data_loader.py            # Data loading utilities
├── game_utils.py             # Game logic utilities
├── pages/                    # Dash page components
│   ├── home.py               # Home page
│   ├── search.py             # Book search page
│   ├── analysis_hub.py       # Data analysis hub landing page
│   ├── distributions.py      # Distribution analysis page
│   ├── authors.py            # Author statistics page
│   ├── game_hub.py           # Game hub landing page
│   ├── pairings_hub.py       # Literary pairings hub page
│   ├── unique_twins.py       # Unique word twins page
│   ├── word_twins.py         # Individual word twins page
│   ├── book_view.py          # Individual book viewer
│   ├── little_red_herring.py # Game: Little Red Herring
│   ├── much_ado.py           # Game: Much Ado About Counting
│   ├── mystery.py            # Game: A Book with a Clue
│   └── tale_of_counts.py     # Game: Tale of Two Counts
├── assets/                   # Static assets (CSS, images, plots)
│   ├── style.css             # Custom styles
│   └── plots/                # Pre-generated visualization plots
├── project_books_raw/        # Raw book text files (~24,278 files)
├── project_books_clean/      # Cleaned book text files (~24,278 files)
├── book_word_counts_output/  # Spark output directory
├── unique_twins.json         # Pre-computed unique word twins data
├── generate_plots.py         # Script to generate static plots
└── README.md                 # This file
```

## Technologies

- **Dash**: Web framework for building interactive dashboards
- **PySpark**: Distributed data processing
- **SQLite**: Lightweight database for querying word counts
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualizations

## Customization

- **Styling**: Update theme colors in `data_loader.py` (THEME dictionary)
- **Game Logic**: Modify game files in the `pages/` directory
- **Data Processing**: Adjust Spark jobs in `spark_wordcount.py`
- **Database Schema**: Modify `csv_to_sqlite.py` for different data structures

## Notes

- The application processes approximately 24,000 books from Project Gutenberg
- Word count processing handles over 1.4 billion words using distributed computing
- The SQLite database enables fast queries for interactive features
- All book text files are stored in cleaned format for efficient processing
