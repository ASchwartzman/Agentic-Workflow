"""
Write data to a Google Sheet.

Usage:
    python tools/sheets_write.py --sheet-id SHEET_ID --range "Sheet1!A1" --input .tmp/data.json
    python tools/sheets_write.py --sheet-id SHEET_ID --range "Sheet1!A1" --values '[["Name","Score"],["Alice",42]]'

Arguments:
    --sheet-id   The Google Sheets ID (from the URL: /spreadsheets/d/<ID>/)
    --range      Top-left cell to start writing (e.g. "Sheet1!A1")
    --input      Path to a JSON file containing a 2D array of values
    --values     Inline JSON string of a 2D array (alternative to --input)
    --mode       "overwrite" (default) clears the range first; "append" adds rows below existing data
"""

import argparse
import json
from google_auth import get_sheets_service


def write_sheet(sheet_id: str, range_: str, values: list[list], mode: str = "overwrite"):
    service = get_sheets_service()
    body = {"values": values}

    if mode == "append":
        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=sheet_id,
                range=range_,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        updated = result.get("updates", {}).get("updatedRows", 0)
    else:
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=sheet_id,
                range=range_,
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )
        updated = result.get("updatedRows", 0)

    return updated


def main():
    parser = argparse.ArgumentParser(description="Write data to a Google Sheet")
    parser.add_argument("--sheet-id", required=True)
    parser.add_argument("--range", required=True)
    parser.add_argument("--input", help="Path to JSON file with 2D array")
    parser.add_argument("--values", help="Inline JSON 2D array string")
    parser.add_argument("--mode", choices=["overwrite", "append"], default="overwrite")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            values = json.load(f)
    elif args.values:
        values = json.loads(args.values)
    else:
        parser.error("Provide either --input or --values")

    updated = write_sheet(args.sheet_id, args.range, values, args.mode)
    print(f"Updated {updated} rows in {args.range}")


if __name__ == "__main__":
    main()
