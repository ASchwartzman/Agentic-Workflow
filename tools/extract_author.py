"""
Extract author articles from Substack and create a Google Sheet.

Usage:
    python tools/extract_author.py --url https://substack.com/@compoundwithai
"""

import argparse
import xml.etree.ElementTree as ET
import urllib.request
from google_auth import get_sheets_service

def get_article_urls(author_handle: str) -> list[str]:
    # Use the publication's sitemap. Substack redirects author.substack.com to their custom domain if any.
    sitemap_url = f"https://{author_handle}.substack.com/sitemap.xml"
    req = urllib.request.Request(sitemap_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        xml_data = response.read()
    except Exception as e:
        print(f"Error fetching sitemap for {author_handle}: {e}")
        return []

    root = ET.fromstring(xml_data)
    
    # Substack sitemaps use namespaces
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = []
    
    for url in root.findall('ns:url', namespaces):
        loc = url.find('ns:loc', namespaces)
        if loc is not None and loc.text:
            link = loc.text
            # Only keep article links, exclude /archive, /about, etc.
            if '/p/' in link:
                urls.append(link)
                
    return urls

def create_and_populate_sheet(author_name: str, urls: list[str]) -> str:
    service = get_sheets_service()
    
    sheet_title = f"Artigos Substack - {author_name}"
    spreadsheet = {
        'properties': {
            'title': sheet_title
        },
        'sheets': [
            {
                'properties': {
                    'title': 'Posts'
                }
            }
        ]
    }
    
    spreadsheet = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    sheet_id = spreadsheet.get('spreadsheetId')
    print(f"Created Google Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}/")
    
    # Populate the headers
    headers = ["Id", "URL", "Title", "Description", "AI_summary", "original_content", "Extracted_content", "Date", "Extracted"]
    
    # Values array with header + urls
    values = [headers]
    for url in urls:
        # Id can be empty, URL is second column
        values.append(["", url])
        
    body = {
        'values': values
    }
    
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="Posts!A1",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    print(f"Updated {result.get('updatedRows')} rows in the new sheet.")
    return sheet_id

def main():
    parser = argparse.ArgumentParser(description="Extract Substack author articles and create Google Sheet")
    parser.add_argument("--url", required=True, help="Substack author URL (e.g. https://substack.com/@compoundwithai)")
    args = parser.parse_args()
    
    # Extract author handle from URL
    url = args.url.rstrip('/')
    author_handle = url.split('@')[-1]
    
    print(f"Extracting articles for author: {author_handle}...")
    urls = get_article_urls(author_handle)
    
    if not urls:
        print("No articles found or error occurred.")
        return
        
    print(f"Found {len(urls)} articles.")
    
    print(f"Creating Google Sheet for {author_handle}...")
    sheet_id = create_and_populate_sheet(author_handle, urls)
    
    print(f"\nNext steps:")
    print(f"  source .venv/bin/activate")
    print(f"  python tools/process_articles.py --sheet-id {sheet_id}")

if __name__ == "__main__":
    main()
