"""
Scrape an article URL using Firecrawl and return structured metadata.

Returns raw markdown content plus metadata (title, description, published_time)
extracted from the Firecrawl response object.

Usage:
    python tools/scrape_article.py --url https://example.com
    python tools/scrape_article.py --url https://example.com --output .tmp/article.json

Arguments:
    --url     The URL to scrape
    --output  Optional path to write JSON output (default: prints to stdout)
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from firecrawl import V1FirecrawlApp as FirecrawlApp

load_dotenv(Path(__file__).parent.parent / ".env")


def scrape_article(url: str) -> dict:
    """
    Scrape a URL with Firecrawl and return structured article data.

    Returns:
        dict with keys: markdown, title, description, published_time, error
        On failure: error is set; other fields are None.
    """
    try:
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not set in .env")

        app = FirecrawlApp(api_key=api_key)
        result = app.scrape_url(url, formats=["markdown"])

        meta = result.metadata or {}

        title = meta.get("ogTitle") or meta.get("title") or None
        description = meta.get("ogDescription") or meta.get("description") or None
        published_time = (
            meta.get("publishedTime")
            or meta.get("article:published_time")
            or meta.get("dctermsCreated")
            or None
        )

        return {
            "markdown": result.markdown or "",
            "title": title,
            "description": description,
            "published_time": published_time,
            "error": None,
        }

    except Exception as e:
        return {
            "markdown": None,
            "title": None,
            "description": None,
            "published_time": None,
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(description="Scrape an article URL with Firecrawl")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument("--output", help="Path to write JSON output")
    args = parser.parse_args()

    result = scrape_article(args.url)
    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
