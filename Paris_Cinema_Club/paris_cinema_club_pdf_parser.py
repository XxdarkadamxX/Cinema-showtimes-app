#!/usr/bin/env python3
"""
Paris Cinema Club PDF Parser
Extracts movie showtime data from PDF files and organizes by date
"""

import os
import json
import re
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import pdfplumber
from typing import Dict, List, Any, Optional

class ParisCinemaClubPDFParser:
    def __init__(self, pdf_dir: str = "Paris_Cinema_Club_pdf"):
        """
        Initialize the PDF parser
        
        Args:
            pdf_dir: Directory containing the PDF files
        """
        self.pdf_dir = pdf_dir
        self.output_file = "paris_cinema_club_showtimes.json"
        
        # Common French month names and their English equivalents
        self.month_mapping = {
            'janvier': 'January', 'février': 'February', 'mars': 'March',
            'avril': 'April', 'mai': 'May', 'juin': 'June',
            'juillet': 'July', 'août': 'August', 'septembre': 'September',
            'octobre': 'October', 'novembre': 'November', 'décembre': 'December'
        }
        
        # Common French day names
        self.day_mapping = {
            'lundi': 'Monday', 'mardi': 'Tuesday', 'mercredi': 'Wednesday',
            'jeudi': 'Thursday', 'vendredi': 'Friday', 'samedi': 'Saturday', 'dimanche': 'Sunday'
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text_content = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"
            return text_content
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def parse_date_range_from_header(self, text: str) -> Optional[tuple]:
        """
        Parse date range from the header (e.g., "HORAIRES DU 30 JUILLET AU 5 AOÛT")
        
        Args:
            text: Text containing the header
            
        Returns:
            Tuple of (start_date, end_date) or None
        """
        # Look for the header pattern
        header_pattern = r'HORAIRES DU (\d{1,2})\s+([A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]+)\s+AU\s+(\d{1,2})\s+([A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]+)'
        match = re.search(header_pattern, text, re.IGNORECASE)
        
        if match:
            try:
                start_day = int(match.group(1))
                start_month = match.group(2).lower()
                end_day = int(match.group(3))
                end_month = match.group(4).lower()
                
                # Convert French month names to English
                if start_month in self.month_mapping:
                    start_month_en = self.month_mapping[start_month]
                else:
                    return None
                    
                if end_month in self.month_mapping:
                    end_month_en = self.month_mapping[end_month]
                else:
                    return None
                
                # Assume current year
                current_year = datetime.now().year
                
                # Handle December to January transition (end date in next year)
                if start_month_en == 'December' and end_month_en == 'January':
                    start_date = datetime(current_year, list(self.month_mapping.values()).index(start_month_en) + 1, start_day)
                    end_date = datetime(current_year + 1, list(self.month_mapping.values()).index(end_month_en) + 1, end_day)
                else:
                    # Both dates in same year
                    start_date = datetime(current_year, list(self.month_mapping.values()).index(start_month_en) + 1, start_day)
                    end_date = datetime(current_year, list(self.month_mapping.values()).index(end_month_en) + 1, end_day)
                
                return (start_date, end_date)
                
            except (ValueError, IndexError):
                return None
        
        return None

    def parse_daily_schedule(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse the daily schedule from the PDF text
        
        Args:
            text: Text content from PDF
            
        Returns:
            Dictionary with dates as keys and movie lists as values
        """
        daily_schedules = {}
        
        # Split text into lines
        lines = text.split('\n')
        
        current_date = None
        current_movies = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for day headers (e.g., "MERCREDI 30", "JEUDI 31")
            day_pattern = r'^([A-ZÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]+)\s+(\d{1,2})$'
            day_match = re.match(day_pattern, line)
            
            if day_match:
                # Save previous day's movies
                if current_date and current_movies:
                    daily_schedules[current_date] = current_movies
                
                # Start new day
                day_name = day_match.group(1).lower()
                day_number = int(day_match.group(2))
                
                # Convert French day name to English
                if day_name in self.day_mapping:
                    day_name_en = self.day_mapping[day_name]
                else:
                    day_name_en = day_name
                
                current_date = f"{day_name_en} {day_number}"
                current_movies = []
                continue
            
            # Look for movie entries with two movies per line
            # Pattern: time : movie1 category time : movie2 category
            # Each line contains two movies (one for each cinema hall)
            movie_pattern = r'(\d{1,2}h\d{2})\s*:\s*(.+?)(?:\s+(\d{1,2}h\d{2})\s*:\s*(.+))?$'
            movie_match = re.match(movie_pattern, line)
            
            if movie_match and current_date:
                # First movie
                showtime1 = movie_match.group(1)
                movie1_info = movie_match.group(2).strip()
                
                # Second movie (if exists)
                showtime2 = movie_match.group(3)
                movie2_info = movie_match.group(4).strip() if movie_match.group(4) else ""
                
                # Parse first movie
                if movie1_info:
                    movie1 = self.parse_movie_info(movie1_info, showtime1)
                    if movie1:
                        current_movies.append(movie1)
                
                # Parse second movie
                if movie2_info and showtime2:
                    movie2 = self.parse_movie_info(movie2_info, showtime2)
                    if movie2:
                        current_movies.append(movie2)
        
        # Add the last day's movies
        if current_date and current_movies:
            daily_schedules[current_date] = current_movies
        
        return daily_schedules

    def parse_movie_info(self, movie_text: str, showtime: str) -> Optional[Dict[str, Any]]:
        """
        Parse individual movie information from text
        
        Args:
            movie_text: Text containing movie information
            showtime: Showtime for the movie
            
        Returns:
            Dictionary with movie information or None
        """
        if not movie_text or len(movie_text.strip()) < 3:
            return None
        
        # Extract title, director, and category
        title = movie_text.strip()
        director = None
        category = None
        duration = None
        
        # Known categories
        categories = ["Cannes Fever", "SORTIE NATIONALE", "Far West", "Summer of Love", "Toujours à l'affiche"]
        
        # Known directors
        known_directors = ["Wes Anderson", "David Lynch", "Stanley Kubrick", "Wong Kar-wai"]
        
        # Extract category
        for cat in categories:
            if cat in title:
                category = cat
                title = title.replace(cat, "").strip()
                break
        
        # Extract director
        for director_name in known_directors:
            if director_name in title:
                director = director_name
                title = title.replace(director_name, "").strip()
                break
        
        # Look for duration (e.g., "(35mm)", "1h30")
        duration_match = re.search(r'\((\d+mm)\)|(\d+h\d{2})', title)
        if duration_match:
            duration = duration_match.group(0)
            title = title.replace(duration, "").strip()
        
        # Clean up title
        title = re.sub(r'\s+', ' ', title).strip()
        title = title.strip('.,:;')
        
        # Skip if title is too short
        if len(title) < 3:
            return None
        
        return {
            'title': title,
            'showtime': showtime,
            'duration': duration,
            'director': director,
            'category': category,
            'additional_info': movie_text.strip()
        }

    def organize_by_date(self, christine_text: str, ecoles_text: str) -> Dict[str, Any]:
        """
        Organize showtime data by date
        
        Args:
            christine_text: Text from Christine cinema PDF
            ecoles_text: Text from Ecoles cinema PDF
            
        Returns:
            Organized data by date
        """
        # Parse date range from headers
        christine_dates = self.parse_date_range_from_header(christine_text)
        ecoles_dates = self.parse_date_range_from_header(ecoles_text)
        
        # Use the first date range found, or default to current week
        if christine_dates:
            start_date, end_date = christine_dates
        elif ecoles_dates:
            start_date, end_date = ecoles_dates
        else:
            # Default to current week
            start_date = datetime.now()
            end_date = start_date + timedelta(days=6)
        
        # Parse daily schedules
        christine_schedule = self.parse_daily_schedule(christine_text)
        ecoles_schedule = self.parse_daily_schedule(ecoles_text)
        
        # Create date structure for the week
        dates_data = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            day_name = current_date.strftime('%A')
            
            # Find corresponding day in schedules
            christine_movies = []
            ecoles_movies = []
            
            # Look for movies in Christine schedule
            for day_key, movies in christine_schedule.items():
                if day_name.lower() in day_key.lower() or str(current_date.day) in day_key:
                    christine_movies = movies
                    break
            
            # Look for movies in Ecoles schedule
            for day_key, movies in ecoles_schedule.items():
                if day_name.lower() in day_key.lower() or str(current_date.day) in day_key:
                    ecoles_movies = movies
                    break
            
            dates_data[date_key] = {
                'date': date_key,
                'day_name': day_name,
                'cinemas': {
                    'Christine': {
                        'name': 'Christine',
                        'films': christine_movies
                    },
                    'Ecoles': {
                        'name': 'Ecoles',
                        'films': ecoles_movies
                    }
                }
            }
            
            current_date += timedelta(days=1)
        
        return dates_data

    def run(self):
        """
        Main method to run the PDF parser
        """
        print("Starting Paris Cinema Club PDF Parser...")
        
        # Check if PDF directory exists
        if not os.path.exists(self.pdf_dir):
            print(f"PDF directory {self.pdf_dir} not found!")
            return
        
        # Define PDF file paths
        christine_pdf = os.path.join(self.pdf_dir, "semainier_christine.pdf")
        ecoles_pdf = os.path.join(self.pdf_dir, "semainier_ecoles.pdf")
        
        # Check if PDF files exist
        if not os.path.exists(christine_pdf):
            print(f"Christine PDF not found: {christine_pdf}")
            return
        
        if not os.path.exists(ecoles_pdf):
            print(f"Ecoles PDF not found: {ecoles_pdf}")
            return
        
        print("Extracting text from PDFs...")
        
        # Extract text from both PDFs
        christine_text = self.extract_text_from_pdf(christine_pdf)
        ecoles_text = self.extract_text_from_pdf(ecoles_pdf)
        
        if not christine_text and not ecoles_text:
            print("No text could be extracted from PDFs!")
            return
        
        print("Parsing and organizing data...")
        
        # Organize data by date
        dates_data = self.organize_by_date(christine_text, ecoles_text)
        
        # Create output structure
        output_data = {
            'metadata': {
                'source': 'Paris Cinema Club PDFs',
                'fetched_at': datetime.now().isoformat(),
                'pdf_files': ['semainier_christine.pdf', 'semainier_ecoles.pdf']
            },
            'dates': dates_data
        }
        
        # Save to JSON file
        print(f"Saving data to {self.output_file}...")
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print("Parsing completed successfully!")
        
        # Print summary
        total_cinemas = sum(len(date_data['cinemas']) for date_data in dates_data.values())
        total_movies = sum(
            sum(len(cinema['films']) for cinema in date_data['cinemas'].values())
            for date_data in dates_data.values()
        )
        
        print(f"\nSummary:")
        print(f"  Dates processed: {len(dates_data)}")
        print(f"  Total cinemas: {total_cinemas}")
        print(f"  Total movies: {total_movies}")
        print(f"  Output file: {self.output_file}")

if __name__ == "__main__":
    parser = ParisCinemaClubPDFParser()
    parser.run() 