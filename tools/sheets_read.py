"""
Read data from a Google Sheet.

Usage:
    python tools/sheets_read.py --sheet-id SHEET_ID --range "Sheet1!A1:Z100"
    python tools/sheets_read.py --sheet-id SHEET_ID --range "Sheet1!A1:Z100" --output .tmp/data.json

Arguments:
    --sheet-id   The Google Sheets ID (from the URL: /spreadsheets/d/<ID>/)
    --range      A1 notation range (e.g. "Sheet1!A1:D50")
    --output     Optional path to write JSON output (default: prints to stdout)
"""

import argparse
import json
from google_auth import get_sheets_service


def read_sheet(sheet_id: str, range_: str) -> list[list]:
    service = get_sheets_service()
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheet_id, range=range_)
        .execute()
    )
    return result.get("values", [])


def main():
    parser = argparse.ArgumentParser(description="Read data from a Google Sheet")
    parser.add_argument("--sheet-id", required=True, help="Google Sheets ID")
    parser.add_argument("--range", required=True, help="A1 notation range")
    parser.add_argument("--output", help="Path to write JSON output")
    args = parser.parse_args()

    rows = read_sheet(args.sheet_id, args.range)

    output = json.dumps(rows, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Written {len(rows)} rows to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
