import requests
import json
import re
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
import time

class UGCShowtimesFetcher:
    """
    A class to fetch movie showtimes from UGC using film IDs
    """
    
    def __init__(self):
        self.base_url = "https://www.ugc.fr"
        self.showings_endpoint = "https://www.ugc.fr/showingsFilmAjaxAction!getShowingsByFilm.action"
        self.days_endpoint = "https://www.ugc.fr/showingsFilmAjaxAction!getDaysByFilm.action"
        
        # Headers to mimic a real browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def load_films_data(self, json_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load films data from the parsed JSON file
        
        Args:
            json_file_path: Path to the JSON file containing film data
            
        Returns:
            Dictionary containing film data or None if loading fails
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {data.get('total_films', 0)} films from {json_file_path}")
            return data
        except FileNotFoundError:
            print(f"JSON file not found: {json_file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            return None
        except Exception as e:
            print(f"Error loading films data: {e}")
            return None
    
    def get_available_dates(self, film_id: str, region_id: int = 1) -> List[str]:
        """
        Get available dates for a specific film
        
        Args:
            film_id: The film ID
            region_id: The region ID (default: 1 for Paris)
            
        Returns:
            List of available dates in YYYY-MM-DD format
        """
        try:
            # Use today's date as default
            today = date.today().strftime('%Y-%m-%d')
            
            params = {
                'reloadShowingsTopic': 'reloadShowings',
                'dayForm': 'dayFormDesktop',
                'filmId': film_id,
                'day': today,
                'regionId': region_id,
                'defaultRegionId': region_id
            }
            
            response = requests.get(
                self.days_endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse the HTML to extract available dates
            soup = BeautifulSoup(response.text, 'html.parser')
            dates = []
            
            # Look for date elements in div id attributes (based on actual UGC response structure)
            date_elements = soup.find_all('div', id=re.compile(r'nav_date_\d+_\d{4}-\d{2}-\d{2}'))
            
            for elem in date_elements:
                elem_id = elem.get('id', '')
                # Extract date from id attribute (format: nav_date_1_2025-07-31)
                date_match = re.search(r'nav_date_\d+_(\d{4}-\d{2}-\d{2})', elem_id)
                if date_match:
                    dates.append(date_match.group(1))
            
            # If no dates found in div ids, try alternative approach
            if not dates:
                # Look for date patterns in the text
                text_content = soup.get_text()
                date_pattern = r'\d{4}-\d{2}-\d{2}'
                dates = re.findall(date_pattern, text_content)
            
            # Remove duplicates and sort
            dates = sorted(list(set(dates)))
            
            return dates
            
        except Exception as e:
            print(f"Error getting dates for film {film_id}: {e}")
            return []
    
    def get_showtimes_for_date(self, film_id: str, date_str: str, region_id: int = 1) -> Dict[str, Any]:
        """
        Get showtimes for a specific film on a specific date
        
        Args:
            film_id: The film ID
            date_str: Date in YYYY-MM-DD format
            region_id: The region ID (default: 1 for Paris)
            
        Returns:
            Dictionary containing showtimes data with cinema information
        """
        try:
            params = {
                'filmId': film_id,
                'day': date_str,
                'regionId': region_id,
                'defaultRegionId': region_id,
                '__multiselect_versions': ''
            }
            
            response = requests.get(
                self.showings_endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            
            # Parse the HTML to extract showtimes
            soup = BeautifulSoup(response.text, 'html.parser')
            
            showtimes_data = {
                'film_id': film_id,
                'date': date_str,
                'cinemas': []
            }
            
            # Find cinema sections (based on actual UGC HTML structure)
            cinema_sections = soup.find_all('div', class_='component--cinema-list-item')
            
            if not cinema_sections:
                return showtimes_data
            
            for section in cinema_sections:
                # Find cinema name in the section
                cinema_name_elem = section.find('a', class_='color--dark-blue')
                if cinema_name_elem:
                    cinema_name = cinema_name_elem.get_text(strip=True)
                else:
                    # Fallback: look for cinema name in data attributes
                    cinema_name = "Unknown Cinema"
                
                cinema_data = {
                    'name': cinema_name,
                    'showtimes': []
                }
                
                # Extract showtimes from this cinema section
                # Look for li elements with button elements inside (showtime buttons)
                showtime_elements = section.find_all('li')
                
                for showtime_elem in showtime_elements:
                    # Look for the time in the screening-start div
                    time_div = showtime_elem.find('div', class_='screening-start')
                    if time_div:
                        time_text = time_div.get_text(strip=True)
                        # Extract time pattern (HH:MM)
                        time_match = re.search(r'(\d{2}:\d{2})', time_text)
                        if time_match:
                            cinema_data['showtimes'].append(time_match.group(1))
                
                showtimes_data['cinemas'].append(cinema_data)
            
            return showtimes_data
            
        except Exception as e:
            print(f"Error getting showtimes for film {film_id} on {date_str}: {e}")
            return {
                'film_id': film_id,
                'date': date_str,
                'cinemas': [],
                'error': str(e)
            }
    
    def fetch_all_film_dates(self, films_data: Dict[str, Any], max_films: int = 5) -> Dict[str, Any]:
        """
        Fetch available dates by cinema for all films in the data (efficient version)
        
        Args:
            films_data: Dictionary containing film data
            max_films: Maximum number of films to process
            
        Returns:
            Dictionary containing all film dates data with cinema breakdown
        """
        all_dates = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'total_films_processed': 0,
                'total_films_with_dates': 0,
                'region_id': 1,
                'note': 'Cinema data fetched only for first available date per film to reduce server load'
            },
            'films': {}
        }
        
        film_count = 0
        films_with_dates = 0
        
        # Extract all films from all sections
        all_films = []
        for section_id, section_data in films_data.get('sections', {}).items():
            for film in section_data.get('films', []):
                all_films.append(film)
        
        # Limit films if max_films is specified
        if max_films:
            all_films = all_films[:max_films]
        
        print(f"Processing {len(all_films)} films out of {films_data.get('total_films', 0)} total films")
        print(f"Note: Cinema data will be fetched only for the first available date per film to reduce server load")
        
        for film in all_films:
            film_id = film.get('film_id')
            film_title = film.get('title')
            
            if not film_id:
                print(f"Skipping film '{film_title}' - no film ID found")
                continue
            
            print(f"Processing film: {film_title} (ID: {film_id})")
            
            # Get available dates for this film
            available_dates = self.get_available_dates(film_id)
            
            if not available_dates:
                print(f"  No available dates found")
                film_data = {
                    'film_id': film_id,
                    'title': film_title,
                    'available_dates': [],
                    'date_count': 0,
                    'cinemas': [],
                    'cinema_count': 0
                }
                all_dates['films'][film_id] = film_data
                film_count += 1
                continue
            
            # Get cinema data only for the first available date (efficient approach)
            first_date = available_dates[0]
            print(f"  Found {len(available_dates)} available dates, fetching cinema data for first date ({first_date})...")
            
            showtimes_data = self.get_showtimes_for_date(film_id, first_date)
            cinemas = []
            
            for cinema in showtimes_data.get('cinemas', []):
                cinema_name = cinema.get('name', 'Unknown Cinema')
                showtime_count = len(cinema.get('showtimes', []))
                cinemas.append({
                    'name': cinema_name,
                    'showtime_count': showtime_count
                })
            
            film_data = {
                'film_id': film_id,
                'title': film_title,
                'available_dates': available_dates,
                'date_count': len(available_dates),
                'cinemas': cinemas,
                'cinema_count': len(cinemas),
                'sample_date': first_date
            }
            
            all_dates['films'][film_id] = film_data
            films_with_dates += 1
            
            print(f"  Found {len(available_dates)} dates across {len(cinemas)} cinemas")
            
            film_count += 1
            
            # Add a delay to be respectful to the server
            time.sleep(0.5)
        
        all_dates['metadata']['total_films_processed'] = film_count
        all_dates['metadata']['total_films_with_dates'] = films_with_dates
        
        return all_dates
    
    def save_dates_to_file(self, dates_data: Dict[str, Any], filename: str) -> bool:
        """
        Save film dates data to a JSON file
        
        Args:
            dates_data: The dates data to save
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(dates_data, f, indent=2, ensure_ascii=False)
            
            print(f"Film dates data saved to {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving film dates data: {e}")
            return False
    
    def print_dates_summary(self, dates_data: Dict[str, Any]) -> None:
        """
        Print a summary of the fetched film dates with cinema information
        
        Args:
            dates_data: The dates data
        """
        metadata = dates_data.get('metadata', {})
        films = dates_data.get('films', {})
        
        print(f"\n=== Film Dates by Cinema Summary (Efficient Version) ===")
        print(f"Films processed: {metadata.get('total_films_processed', 0)}")
        print(f"Films with available dates: {metadata.get('total_films_with_dates', 0)}")
        print(f"Region ID: {metadata.get('region_id', 1)}")
        print(f"Note: {metadata.get('note', 'Cinema data from first available date only')}")
        
        # Show films with the most dates first
        films_with_dates = [(film_id, film_data) for film_id, film_data in films.items() if film_data.get('available_dates')]
        films_with_dates.sort(key=lambda x: len(x[1].get('available_dates', [])), reverse=True)
        
        print(f"\nTop 10 films with most available dates:")
        for i, (film_id, film_data) in enumerate(films_with_dates[:10], 1):
            film_title = film_data.get('title', 'Unknown')
            dates = film_data.get('available_dates', [])
            cinema_count = film_data.get('cinema_count', 0)
            sample_date = film_data.get('sample_date', 'N/A')
            print(f"{i:2d}. {film_title} (ID: {film_id}): {len(dates)} dates, {cinema_count} cinemas")
            if dates:
                print(f"     Dates: {', '.join(dates[:5])}{'...' if len(dates) > 5 else ''}")
                cinemas = film_data.get('cinemas', [])
                if cinemas:
                    cinema_names = [c.get('name', 'Unknown') for c in cinemas]
                    print(f"     Cinemas (sample from {sample_date}): {', '.join(cinema_names[:3])}{'...' if len(cinema_names) > 3 else ''}")
        
        # Show detailed breakdown for first few films
        print(f"\nDetailed breakdown for first 3 films (cinema data from sample date):")
        for i, (film_id, film_data) in enumerate(films_with_dates[:3], 1):
            film_title = film_data.get('title', 'Unknown')
            cinemas = film_data.get('cinemas', [])
            sample_date = film_data.get('sample_date', 'N/A')
            print(f"\n{i}. {film_title} (sample date: {sample_date}):")
            print(f"   Total dates: {len(film_data.get('available_dates', []))}")
            print(f"   Cinemas showing: {len(cinemas)}")
            for cinema in cinemas[:3]:  # Show first 3 cinemas
                cinema_name = cinema.get('name', 'Unknown')
                showtime_count = cinema.get('showtime_count', 0)
                print(f"     - {cinema_name}: {showtime_count} showtimes")


def main():
    """
    Main function to demonstrate the usage of UGCShowtimesFetcher
    """
    print("=== UGC Film Dates Fetcher ===")
    
    # Create fetcher instance
    fetcher = UGCShowtimesFetcher()
    
    # Load films data from the parsed JSON file
    print("\n1. Loading films data...")
    films_data = fetcher.load_films_data('ugc_films_parsed.json')
    
    if not films_data:
        print("Failed to load films data. Please make sure ugc_films_parsed.json exists.")
        return
    
    # Fetch dates for all films
    print("\n2. Fetching available dates for all films...")
    dates_data = fetcher.fetch_all_film_dates(films_data)
    
    if dates_data['films']:
        # Save the dates data
        fetcher.save_dates_to_file(dates_data, 'ugc_film_dates.json')
        
        # Print summary
        fetcher.print_dates_summary(dates_data)
    else:
        print("No film dates data found")
    
    print("\n=== Film dates fetching completed ===")


if __name__ == "__main__":
    main() 