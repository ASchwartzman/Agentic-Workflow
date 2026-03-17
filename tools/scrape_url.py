"""
Scrape a single URL using Firecrawl and return clean markdown content.

Usage:
    python tools/scrape_url.py --url https://example.com
    python tools/scrape_url.py --url https://example.com --output .tmp/scraped.md

Arguments:
    --url     The URL to scrape
    --output  Optional path to write markdown output (default: prints to stdout)
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv(Path(__file__).parent.parent / ".env")


def scrape_url(url: str) -> str:
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY not set in .env")

    app = FirecrawlApp(api_key=api_key)
    result = app.scrape_url(url, formats=["markdown"])
    return result.markdown


def main():
    parser = argparse.ArgumentParser(description="Scrape a URL with Firecrawl")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--output", help="Path to write markdown output")
    args = parser.parse_args()

    content = scrape_url(args.url)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(content, encoding="utf-8")
        print(f"Saved to {args.output} ({len(content)} chars)")
    else:
        print(content)


if __name__ == "__main__":
    main()
