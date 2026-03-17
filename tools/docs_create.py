"""
Create a Google Doc in Drive and optionally populate it with content.

Usage:
    python tools/docs_create.py --title "My Document"
    python tools/docs_create.py --title "My Document" --input .tmp/content.md
    python tools/docs_create.py --title "My Document" --content "Hello world"
    python tools/docs_create.py --title "My Document" --input .tmp/content.md --folder-id FOLDER_ID

Arguments:
    --title      Title of the new Google Doc
    --input      Path to a text/markdown file to use as body content
    --content    Inline string to use as body content
    --folder-id  Optional Drive folder ID to place the doc in (default: My Drive root)

Output:
    Prints the URL of the created document.
"""

import argparse
from pathlib import Path
from google_auth import get_docs_service, get_drive_service


def create_doc(title: str, content: str = "", folder_id: str = None) -> dict:
    docs = get_docs_service()
    drive = get_drive_service()

    # Create the document
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Move to folder if specified
    if folder_id:
        file = drive.files().get(fileId=doc_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents", []))
        drive.files().update(
            fileId=doc_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields="id, parents",
        ).execute()

    # Insert content if provided
    if content:
        docs.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": content,
                        }
                    }
                ]
            },
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return {"doc_id": doc_id, "url": url}


def main():
    parser = argparse.ArgumentParser(description="Create a Google Doc")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--input", help="Path to text/markdown file for body content")
    parser.add_argument("--content", help="Inline string for body content")
    parser.add_argument("--folder-id", help="Drive folder ID to place the doc in")
    args = parser.parse_args()

    content = ""
    if args.input:
        content = Path(args.input).read_text(encoding="utf-8")
    elif args.content:
        content = args.content

    result = create_doc(args.title, content, args.folder_id)
    print(f"Created: {result['url']}")


if __name__ == "__main__":
    main()
