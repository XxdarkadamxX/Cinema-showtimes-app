#!/usr/bin/env python3
"""
Show Paris Cinema Club Showtimes Summary
Displays the extracted showtime data in a readable format
"""

import json
import os
from datetime import datetime

def load_showtimes_data(file_path: str = "paris_cinema_club_showtimes.json"):
    """Load the showtimes data from JSON file"""
    if not os.path.exists(file_path):
        print(f"Showtimes file not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading showtimes data: {e}")
        return None

def display_summary(data):
    """Display a summary of the showtimes data"""
    if not data:
        return
    
    print("=" * 80)
    print("PARIS CINEMA CLUB - SHOWTIMES SUMMARY")
    print("=" * 80)
    
    # Display metadata
    metadata = data.get('metadata', {})
    print(f"Source: {metadata.get('source', 'Unknown')}")
    print(f"Fetched at: {metadata.get('fetched_at', 'Unknown')}")
    print(f"PDF files: {', '.join(metadata.get('pdf_files', []))}")
    print()
    
    # Display dates and movies
    dates = data.get('dates', {})
    print(f"Total dates: {len(dates)}")
    
    total_movies = 0
    total_cinemas = 0
    
    for date_key, date_data in sorted(dates.items()):
        date_obj = datetime.strptime(date_key, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%A, %B %d, %Y')
        
        print(f"\n{formatted_date}")
        print("-" * 60)
        
        cinemas = date_data.get('cinemas', {})
        total_cinemas += len(cinemas)
        
        for cinema_name, cinema_data in cinemas.items():
            films = cinema_data.get('films', [])
            total_movies += len(films)
            
            print(f"\n  {cinema_name} ({len(films)} films):")
            
            for film in films:
                title = film.get('title', 'Unknown')
                showtime = film.get('showtime', 'Unknown')
                category = film.get('category', '')
                director = film.get('director', '')
                
                # Format the output
                film_info = f"    {showtime} - {title}"
                if category:
                    film_info += f" [{category}]"
                if director:
                    film_info += f" (dir. {director})"
                
                print(film_info)
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {total_movies} movies across {total_cinemas} cinema sessions")
    print("=" * 80)

def display_today_showtimes(data):
    """Display showtimes for today"""
    if not data:
        return
    
    today = datetime.now().strftime('%Y-%m-%d')
    dates = data.get('dates', {})
    
    if today in dates:
        print(f"\nTODAY'S SHOWTIMES ({today})")
        print("=" * 60)
        
        date_data = dates[today]
        cinemas = date_data.get('cinemas', {})
        
        for cinema_name, cinema_data in cinemas.items():
            films = cinema_data.get('films', [])
            
            if films:
                print(f"\n{cinema_name}:")
                for film in films:
                    title = film.get('title', 'Unknown')
                    showtime = film.get('showtime', 'Unknown')
                    category = film.get('category', '')
                    
                    film_info = f"  {showtime} - {title}"
                    if category:
                        film_info += f" [{category}]"
                    
                    print(film_info)
    else:
        print(f"\nNo showtimes found for today ({today})")

def main():
    """Main function"""
    # Load the data
    data = load_showtimes_data()
    
    if not data:
        print("No data to display. Please run the parser first.")
        return
    
    # Display summary
    display_summary(data)
    
    # Display today's showtimes
    display_today_showtimes(data)

if __name__ == "__main__":
    main() 