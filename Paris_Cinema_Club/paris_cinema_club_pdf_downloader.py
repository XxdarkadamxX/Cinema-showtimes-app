import requests
import os
from urllib.parse import urlparse
import time
from bs4 import BeautifulSoup
import re

def get_pdf_urls_from_website():
    """
    Scrape the Paris Cinéma Club website to find current PDF URLs
    """
    url = "https://pariscinemaclub.com/programmation-et-horaires/"
    
    try:
        print("Scraping website for PDF links...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all PDF links
        pdf_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.endswith('.pdf'):
                pdf_links.append(href)
        
        # Filter for the specific PDFs we want (semainier files)
        semainier_pdfs = [link for link in pdf_links if 'semainier' in link.lower()]
        
        print(f"Found {len(semainier_pdfs)} semainier PDF files:")
        for pdf in semainier_pdfs:
            print(f"  - {pdf}")
        
        return semainier_pdfs
        
    except Exception as e:
        print(f"Error scraping website: {e}")
        return []

def download_pdf(url, filename):
    """
    Download a PDF file from the given URL with a specific filename
    """
    try:
        print(f"Downloading: {url}")
        print(f"Filename: {filename}")
        
        # Send request with headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Create directory if it doesn't exist
        os.makedirs('Paris_Cinema_Club_pdf', exist_ok=True)
        
        filepath = os.path.join('Paris_Cinema_Club_pdf', filename)
        
        # Download the file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"Successfully downloaded: {filepath}")
        return filepath
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error downloading {url}: {e}")
        return None

def main():
    """
    Download the PDF files from Paris Cinéma Club with dynamic URL detection
    """
    print("Starting dynamic download of Paris Cinéma Club PDF files...")
    print("=" * 60)
    
    # Get current PDF URLs from the website
    pdf_urls = get_pdf_urls_from_website()

    if not pdf_urls:
        print("No PDF files found on the website!")
        return
    
    downloaded_files = []
    
    # Download each PDF with specific names
    for i, url in enumerate(pdf_urls):
        if i == 0:
            filename = "semainier_christine.pdf"
        elif i == 1:
            filename = "semainier_ecoles.pdf"
        else:
            # For any additional PDFs, use a generic name
            filename = f"semainier_extra_{i+1}.pdf"
        
        filepath = download_pdf(url, filename)
        if filepath:
            downloaded_files.append(filepath)
        
        # Add a small delay between downloads
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Download Summary:")
    print(f"Successfully downloaded {len(downloaded_files)} files:")
    for filepath in downloaded_files:
        print(f"  - {filepath}")
    
    if downloaded_files:
        print(f"\nFiles saved in: {os.path.abspath('Paris_Cinema_Club_pdf')}")

if __name__ == "__main__":
    main() 