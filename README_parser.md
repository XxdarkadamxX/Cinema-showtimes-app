# UGC Films Parser

A Python script that uses BeautifulSoup to parse UGC films HTML content into structured JSON data.

## Features

- Fetches film data from UGC's API endpoint
- Parses HTML content into structured JSON data using BeautifulSoup
- Extracts comprehensive film information including:
  - Film titles and IDs
  - Genres and labels
  - Poster image URLs
  - Age restrictions
  - UGC labels/tags
  - Trailer availability
- Organizes films by sections (New Releases, Currently Showing, etc.)
- Can parse existing HTML files
- Provides detailed summaries and statistics

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
python ugc_films_parser.py
```

This will:
1. Fetch film data from the UGC API
2. Parse the HTML content into structured JSON
3. Save the result as `ugc_films_parsed.json`
4. Print a summary of the extracted data
5. Optionally parse any existing HTML files

### Programmatic Usage

```python
from ugc_films_parser import UGCFilmsParser

# Create parser instance
parser = UGCFilmsParser()

# Fetch and parse films data
films_data = parser.fetch_and_parse_films()

# Save to file
if films_data:
    parser.save_data_to_file(films_data, 'my_films_data.json')
    
    # Print summary
    parser.print_summary(films_data)

# Parse existing HTML file
existing_data = parser.parse_existing_html_file('ugc_films_data.html')
if existing_data:
    parser.save_data_to_file(existing_data, 'parsed_from_html.json')
```

## Output Structure

The parser generates structured JSON with the following format:

```json
{
  "sections": {
    "newReleased": {
      "title": "Nouveautés",
      "films": [
        {
          "title": "DRACULA",
          "film_id": "17055",
          "url": "film_dracula_17055.html",
          "genre": "Epouvante-horreur, Drame, Fantastique",
          "label": "",
          "poster_url": "https://www.ugc.fr/dynamique/films/55/17055/fr/poster/large/...",
          "age_restriction": "12+",
          "ugc_label": null,
          "has_trailer": true
        }
      ],
      "film_count": 8
    }
  },
  "total_films": 45,
  "metadata": {
    "source": "UGC Films API",
    "parsed_at": "2024-01-15T10:30:00.123456",
    "parser_version": "1.0"
  }
}
```

## Files Generated

- `ugc_films_parsed.json`: Freshly fetched and parsed film data
- `ugc_films_from_html.json`: Data parsed from existing HTML files (if available)

## API Endpoint

The parser uses the UGC API endpoint:
```
https://www.ugc.fr/filmsAjaxAction!getFilmsAndFilters.action
```

With parameters:
- `filter`: Filter string (empty by default)
- `page`: Page number (30010 by default)
- `cinemaId`: Cinema ID filter (empty by default)
- `reset`: Reset parameter (true by default)

## Extracted Data Fields

For each film, the parser extracts:

- **title**: Film title
- **film_id**: Unique film identifier
- **url**: Film page URL
- **genre**: Film genres/categories
- **label**: Film label information
- **poster_url**: URL to film poster image
- **age_restriction**: Age restriction (e.g., "12+", "16+")
- **ugc_label**: UGC-specific label (e.g., "UGC Aime", "Sélection UGC Family")
- **has_trailer**: Boolean indicating if trailer is available

## Notes

- Uses BeautifulSoup for robust HTML parsing
- Handles French characters and encoding properly
- Includes error handling for malformed HTML
- Provides detailed logging and progress information
- Can work with both live API data and saved HTML files

## Requirements

- Python 3.6+
- requests library
- beautifulsoup4 library

## Differences from ugc_films_fetcher.py

This parser is specifically designed for HTML parsing and provides:
- More detailed film information extraction
- Better error handling for HTML parsing
- Support for parsing existing HTML files
- Enhanced summary and statistics
- Additional metadata tracking 