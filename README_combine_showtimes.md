# Showtime Data Combination Script

This script combines showtime data from multiple cinema sources into a single DataFrame and exports it to both JSON and CSV formats.

## Features

- **Multi-source support**: Combines data from Dulac Cinemas, Paris Cinema Club, and UGC
- **Unified format**: Standardizes different data structures into a consistent format
- **Multiple outputs**: Generates both JSON and CSV files for different use cases
- **Clean data**: Includes only essential columns: movie, cinema, showtime day, number of showings, and showtimes
- **Statistics**: Provides summary statistics and insights

## Output Format

The combined data includes the following columns:

- **movie**: Title of the film
- **cinema**: Name of the cinema
- **showtime_day**: Date of the showing (YYYY-MM-DD format)
- **nb_showings**: Number of showings for that movie on that day
- **showtimes**: List of specific showtimes (empty for UGC data)

## Usage

```bash
python combine_showtimes.py
```

## Output Files

1. **combined_showtimes.json**: Structured JSON with metadata and records
2. **combined_showtimes.csv**: Tabular format for easy analysis in Excel/spreadsheets

## Sample Output

The script provides a summary including:
- Total number of records
- Data sources used
- Cinemas included
- Date range covered
- Sample data preview
- Statistics by cinema and date

## Example Statistics

```
=== SUMMARY ===
Total records: 429
Cinemas: ['Christine', 'Ecoles', 'Escurial', 'L'Arlequin', 'Majestic Bastille', 'Majestic Passy', 'Reflet Medicis', 'UGC Ciné Cité Bercy', 'UGC Ciné Cité Les Halles', 'UGC Ciné Cité Maillot', 'UGC Ciné Cité Paris 19', 'UGC Danton', 'UGC Gobelins', 'UGC Lyon Bastille', 'UGC Montparnasse']
Date range: 2025-07-30 to 2025-08-05

=== STATISTICS ===
Movies per cinema:
cinema
Ecoles                      39
Christine                   37
Reflet Medicis              17
UGC Ciné Cité Paris 19       2
UGC Lyon Bastille            2
UGC Montparnasse             2
UGC Danton                   1
```

## Data Sources

### Dulac Cinemas
- **Format**: Structured JSON with dates, cinemas, and films
- **Features**: Multiple showtimes per film
- **Cinemas**: Majestic Bastille, L'Arlequin, Escurial, Majestic Passy, Reflet Medicis

### Paris Cinema Club
- **Format**: PDF-derived JSON with individual film entries
- **Features**: Single showtime per entry
- **Cinemas**: Christine, Ecoles

### UGC
- **Format**: JSON with film availability and showtime counts
- **Features**: Showtime counts per cinema, no specific showtimes
- **Cinemas**: Multiple UGC locations across Paris

## Extending the Script

To add new data sources:

1. Create a new parser function following the existing pattern
2. Add the file path and parser to the `json_files` list in `combine_all_showtimes()`
3. Ensure the parser returns records with the standard format

## Requirements

- Python 3.6+
- pandas
- json (built-in)
- datetime (built-in) 