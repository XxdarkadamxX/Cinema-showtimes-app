# Paris Cinema Club PDF Parser

This tool extracts movie showtime data from Paris Cinema Club PDF files and organizes it by date.

## Features

- Extracts movie showtimes from PDF files
- Organizes data by date (first block is the current date, following blocks are subsequent days)
- Parses movie titles, showtimes, directors, and categories
- Supports both Christine and Ecoles cinema locations
- Outputs structured JSON data
- Provides a summary display script

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- `requests>=2.31.0`
- `beautifulsoup4>=4.12.0`
- `PyPDF2>=3.0.0`
- `pdfplumber>=0.10.0`
- `python-dateutil>=2.8.0`

## Usage

### 1. Download PDF Files

First, download the current PDF files from the Paris Cinema Club website:

```bash
python paris_cinema_club_pdf_downloader.py
```

This will download the latest `semainier_christine.pdf` and `semainier_ecoles.pdf` files to the `Paris_Cinema_Club_pdf/` directory.

### 2. Extract Showtime Data

Run the PDF parser to extract and organize the showtime data:

```bash
python paris_cinema_club_pdf_parser.py
```

This will create a `paris_cinema_club_showtimes.json` file with the extracted data.

### 3. View Summary

Display a readable summary of the extracted data:

```bash
python show_showtimes_summary.py
```

## Output Format

The parser creates a JSON file with the following structure:

```json
{
  "metadata": {
    "source": "Paris Cinema Club PDFs",
    "fetched_at": "2025-08-01T04:04:16.390963",
    "pdf_files": ["semainier_christine.pdf", "semainier_ecoles.pdf"]
  },
  "dates": {
    "2025-07-30": {
      "date": "2025-07-30",
      "day_name": "Wednesday",
      "cinemas": {
        "Christine": {
          "name": "Christine",
          "films": [
            {
              "title": "Les Parapluies de Cherbourg",
              "showtime": "13h30",
              "duration": null,
              "director": null,
              "category": "Cannes Fever",
              "additional_info": "Les Parapluies de Cherbourg Cannes Fever"
            }
          ]
        },
        "Ecoles": {
          "name": "Ecoles",
          "films": [...]
        }
      }
    }
  }
}
```

## Data Structure

Each movie entry contains:

- **title**: Movie title
- **showtime**: Screening time (format: HHhMM)
- **duration**: Movie duration (if available)
- **director**: Director name (if identified)
- **category**: Program category (e.g., "Cannes Fever", "SORTIE NATIONALE", "Far West", "Summer of Love", "Toujours à l'affiche")
- **additional_info**: Original text from PDF

## Date Organization

The data is organized by date with:
- **First block**: Current date (when the code is run)
- **Following blocks**: Subsequent days in chronological order
- Each date contains showtimes for both Christine and Ecoles cinemas

## Example Output

```
Wednesday, July 30, 2025
------------------------------------------------------------

  Christine (10 films):
    13h30 - Les Parapluies de Cherbourg [Cannes Fever]
    14h00 - Citizen Kane Toujours à l'affiche
    15h15 - Stella Dallas [SORTIE NATIONALE]
    16h10 - Le Mépris [Summer of Love]
    17h10 - Drive [Cannes Fever]
    18h05 - Rushmore (dir. Wes Anderson)
    19h00 - Mademoiselle [Cannes Fever]
    19h50 - Blue Velvet (dir. David Lynch)
    21h45 - Le Silence des agneaux [Cannes Fever]
    22h00 - Nos années sauvages (dir. Wong Kar-wai)

  Ecoles (9 films):
    14h00 - Certains l'aiment chaud [Summer of Love]
    14h30 - Taxi Driver [Cannes Fever]
    ...
```

## Files

- `paris_cinema_club_pdf_downloader.py`: Downloads PDF files from the website
- `paris_cinema_club_pdf_parser.py`: Main parser that extracts showtime data
- `show_showtimes_summary.py`: Displays a readable summary of the data
- `test_parser.py`: Test script for the parser
- `paris_cinema_club_showtimes.json`: Output file with extracted data

## Notes

- The parser automatically detects French date formats and converts them to standard ISO format
- Movie titles are cleaned and normalized
- Directors are identified from a predefined list of known directors
- Categories are extracted from the PDF text based on known program categories
- The parser handles the specific format where each line contains two movies (one for each cinema hall) 