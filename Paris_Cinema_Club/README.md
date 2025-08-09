# Paris Cinema Club PDF Parser

This script extracts movie showings data from PDF files and creates a JSON file similar to the Dulac showtimes format.

## Features

- Extracts movie data from PDF files using both `tabula-py` and `pdfplumber`
- Parses movie titles, showtimes, durations, and genres
- Creates structured JSON output matching the Dulac showtimes format
- Handles multiple cinemas (Cinéma Christine and Cinéma des Écoles)

## Requirements

Install the required dependencies:

```bash
pip install -r ../requirements.txt
```

Required packages:
- `pdfplumber>=0.10.0` - For text extraction from PDFs
- `tabula-py>=2.8.0` - For table extraction from PDFs
- `pandas>=2.0.0` - For data manipulation
- `requests>=2.31.0` - For HTTP requests
- `beautifulsoup4>=4.12.0` - For HTML parsing

## Usage

### Basic Usage

```python
from paris_cinema_club_pdf_parser import ParisCinemaClubPDFParser

# Create parser instance
parser = ParisCinemaClubPDFParser()

# Run the parser
parser.run()
```

### Command Line

```bash
cd Paris_Cinema_Club
python paris_cinema_club_pdf_parser.py
```

### Test the Parser

```bash
cd Paris_Cinema_Club
python test_parser.py
```

## Input Files

The parser expects the following PDF files in the `Paris_Cinema_Club_pdf/` directory:

- `semainier_christine.pdf` - Showtimes for Cinéma Christine
- `semainier_ecoles.pdf` - Showtimes for Cinéma des Écoles

## Output Format

The script generates a JSON file (`paris_cinema_club_showtimes.json`) with the following structure:

```json
{
  "metadata": {
    "fetched_at": "2025-01-27T10:30:00.000000",
    "source": "Paris Cinema Club",
    "base_url": "https://pariscinemaclub.com",
    "date_range": "Next 7 days from today"
  },
  "dates": {
    "2025-01-27": {
      "date": "2025-01-27",
      "cinemas": [
        {
          "name": "Cinéma Christine",
          "cinema_id": "pcc_1",
          "films": [
            {
              "title": "MOVIE TITLE",
              "kind": "Drame",
              "duration": "(1 H 47 MIN)",
              "showtimes": ["14:30", "20:15"],
              "showtime_count": 2
            }
          ]
        }
      ]
    }
  }
}
```

## Methodology

The parser uses a dual approach similar to the `extract_pdf.ipynb` methodology:

1. **Table Extraction**: Uses `tabula-py` to extract structured tables from PDFs
2. **Text Extraction**: Uses `pdfplumber` to extract raw text and parse it with regex patterns
3. **Data Merging**: Combines results from both methods and removes duplicates
4. **Date Organization**: Organizes movies by date and cinema

## Data Extraction Patterns

The parser looks for:

- **Movie Titles**: Text in ALL CAPS format
- **Showtimes**: Time patterns like "14:30", "20:15"
- **Durations**: Patterns like "(1 H 47 MIN)", "(2 H 30 MIN)"
- **Genres**: French movie genres like "Drame", "Comédie", "Thriller", etc.

## Limitations

- Currently uses placeholder dates (next 7 days from today) as actual dates are not easily extractable from the PDFs
- Movie-genre matching is based on regex patterns and may not capture all genres
- Duration extraction depends on consistent formatting in the PDFs

## Troubleshooting

### Common Issues

1. **PDF files not found**: Ensure PDF files are in the correct directory
2. **Import errors**: Install all required dependencies
3. **Empty output**: Check if PDF files contain extractable text/tables

### Debug Mode

To see more detailed output, modify the parser to add debug prints:

```python
parser = ParisCinemaClubPDFParser()
# Add debug prints in the parsing methods
parser.run()
```

## Future Improvements

- Extract actual dates from PDF content
- Improve genre detection accuracy
- Add support for more cinema locations
- Implement date-specific movie scheduling
- Add validation for extracted data 