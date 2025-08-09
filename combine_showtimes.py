#!/usr/bin/env python3
"""
Script to combine all showtime JSON files into a single DataFrame.
Combines data from Dulac, Paris Cinema Club, and other cinema showtime files.
"""

import json
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and return JSON data from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def parse_dulac_showtimes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Dulac showtimes data into flat list of records."""
    records = []
    
    if 'dates' not in data:
        return records
    
    for date_str, date_data in data['dates'].items():
        if 'cinemas' not in date_data:
            continue
            
        for cinema in date_data['cinemas']:
            cinema_name = cinema.get('name', 'Unknown')
            
            for film in cinema.get('films', []):
                film_title = film.get('title', 'Unknown')
                showtimes = film.get('showtimes', [])
                showtime_count = film.get('showtime_count', len(showtimes))
                
                records.append({
                    'movie': film_title,
                    'cinema': cinema_name,
                    'showtime_day': date_str,
                    'nb_showings': showtime_count,
                    'showtimes': showtimes
                })
    
    return records

def parse_paris_cinema_club_showtimes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Paris Cinema Club showtimes data into flat list of records."""
    records = []
    
    if 'dates' not in data:
        return records
    
    for date_str, date_data in data['dates'].items():
        if 'cinemas' not in date_data:
            continue
            
        for cinema_name, cinema_data in date_data['cinemas'].items():
            for film in cinema_data.get('films', []):
                film_title = film.get('title', 'Unknown')
                showtime = film.get('showtime', '')
                
                # Each film entry represents one showing
                records.append({
                    'movie': film_title,
                    'cinema': cinema_name,
                    'showtime_day': date_str,
                    'nb_showings': 1,
                    'showtimes': [showtime] if showtime else []
                })
    
    return records

def parse_ugc_showtimes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse UGC showtimes data into flat list of records."""
    records = []
    
    if 'films' not in data:
        return records
    
    for film_id, film_data in data['films'].items():
        film_title = film_data.get('title', 'Unknown')
        available_dates = film_data.get('available_dates', [])
        cinemas = film_data.get('cinemas', [])
        
        for cinema in cinemas:
            cinema_name = cinema.get('name', 'Unknown')
            showtime_count = cinema.get('showtime_count', 0)
            
            # Create one record per date for this film/cinema combination
            for date_str in available_dates:
                records.append({
                    'movie': film_title,
                    'cinema': cinema_name,
                    'showtime_day': date_str,
                    'nb_showings': showtime_count,
                    'showtimes': []  # UGC doesn't provide specific showtimes, just counts
                })
    
    return records

def combine_all_showtimes() -> pd.DataFrame:
    """Combine all showtime data from different sources into a single DataFrame."""
    all_records = []
    
    # Define the JSON files to process
    json_files = [
        ('Dulac/dulac_showtimes.json', parse_dulac_showtimes),
        ('Paris_Cinema_Club/paris_cinema_club_showtimes.json', parse_paris_cinema_club_showtimes),
        ('UGC/ugc_film_dates.json', parse_ugc_showtimes),
    ]
    
    for file_path, parser_func in json_files:
        if os.path.exists(file_path):
            print(f"Processing {file_path}...")
            data = load_json_file(file_path)
            if data:
                records = parser_func(data)
                all_records.extend(records)
                print(f"  Found {len(records)} records")
        else:
            print(f"File not found: {file_path}")
    
    if not all_records:
        print("No showtime data found!")
        return pd.DataFrame()
    
    # Create DataFrame
    df = pd.DataFrame(all_records)
    
    # Convert showtime_day to datetime for better sorting
    df['showtime_day'] = pd.to_datetime(df['showtime_day'], errors='coerce')
    
    # Sort by date, cinema, and movie
    df = df.sort_values(['showtime_day', 'cinema', 'movie'])
    
    return df

def save_combined_data(df: pd.DataFrame, output_file: str = 'combined_showtimes.json'):
    """Save combined data to JSON file."""
    # Convert back to string format for JSON serialization
    df_copy = df.copy()
    df_copy['showtime_day'] = df_copy['showtime_day'].dt.strftime('%Y-%m-%d')
    
    # Convert DataFrame to records for JSON
    records = df_copy.to_dict('records')
    
    output_data = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'total_records': len(records),
            'cinemas': df_copy['cinema'].unique().tolist(),
            'date_range': {
                'start': df_copy['showtime_day'].min(),
                'end': df_copy['showtime_day'].max()
            }
        },
        'records': records
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Combined data saved to {output_file}")

def main():
    """Main function to combine and display showtime data."""
    print("Combining showtime data from all sources...")
    
    # Combine all showtimes
    df = combine_all_showtimes()
    
    if df.empty:
        print("No data to process!")
        return
    
    # Display summary
    print(f"\n=== SUMMARY ===")
    print(f"Total records: {len(df)}")
    print(f"Cinemas: {df['cinema'].unique()}")
    print(f"Date range: {df['showtime_day'].min()} to {df['showtime_day'].max()}")
    
    # Display sample data
    print(f"\n=== SAMPLE DATA ===")
    print(df.head(10).to_string(index=False))
    
    # Save to JSON
    save_combined_data(df)
    
    # Save to CSV for easy viewing
    csv_file = 'combined_showtimes.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"Data also saved to {csv_file}")
    
    # Display some statistics
    print(f"\n=== STATISTICS ===")
    print(f"Movies per cinema:")
    print(df.groupby('cinema')['movie'].nunique().sort_values(ascending=False))
    
    print(f"\nShowings per day:")
    print(df.groupby('showtime_day')['nb_showings'].sum().sort_values(ascending=False).head(10))

if __name__ == "__main__":
    main() 