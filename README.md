# UGC Films Fetcher

A simple Python script to fetch film information from the UGC website using the requests module.

## Features

- Fetches film data from UGC's API endpoint
- Parses HTML content into structured JSON data
- Extracts film information including titles, genres, posters, and age restrictions
- Organizes films by sections (New Releases, Currently Showing, etc.)
- Simple and lightweight implementation
- No scraping - just HTTP requests

## Setup

### 1. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python ugc_films_fetcher.py
```

This will:
1. Fetch the main UGC films page and save it as `ugc_main_page.html`
2. Fetch film data from the API endpoint and save it as `ugc_films_data.html`

### Programmatic Usage

```python
from ugc_films_fetcher import UGCFilmsFetcher

# Create fetcher instance
fetcher = UGCFilmsFetcher()

# Fetch films data
films_data = fetcher.fetch_films_data()

# Save to file
if films_data:
    fetcher.save_data_to_file(films_data, 'my_films_data.html')
```

## API Endpoint

The script uses the UGC API endpoint:
```
https://www.ugc.fr/filmsAjaxAction!getFilmsAndFilters.action
```

With parameters:
- `filter`: Filter string (empty by default)
- `page`: Page number (30010 by default)
- `cinemaId`: Cinema ID filter (empty by default)
- `reset`: Reset parameter (true by default)

## Output

The script generates a structured JSON file:
- `ugc_films_data.json`: Parsed film data organized by sections with detailed information for each film

## Notes

- The API returns HTML content, which is parsed into structured JSON
- The script includes proper headers to mimic a real browser request
- All requests include timeout handling and error management
- Files are saved with UTF-8 encoding to properly handle French characters
- Extracted data includes film titles, IDs, genres, poster URLs, age restrictions, and UGC labels

## Requirements

- Python 3.6+
- requests library
- beautifulsoup4 library