"""
Process unextracted Substack articles from Google Sheets.

Reads rows where Extracted != TRUE, scrapes each URL with Firecrawl,
cleans and extracts content with Gemini, and writes structured fields back.
All written content is kept in the original language of the article.

Usage:
    python tools/process_articles.py
    python tools/process_articles.py --sheet-id SHEET_ID --tab Posts

Arguments:
    --sheet-id  Google Sheets ID (default: target sheet)
    --tab       Sheet tab name (default: Posts)
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrape_article import scrape_article
from llm_call import llm_call
from sheets_read import read_sheet
from sheets_write import write_sheet

SHEET_ID = "15fZgS2sGT589wk1KHX4wWxo7gG2AD4plkn4-L2i9Qlo"
MODEL = "gemini-3-flash-preview"
CELL_LIMIT = 49000
MARKDOWN_LIMIT = 40000  # chars sent to Gemini (~10k tokens)

EXTRACTION_PROMPT = """Você está processando um artigo do Substack.

REGRA FUNDAMENTAL DE IDIOMA: Detecte o idioma do artigo e escreva TODO o conteúdo de saída nesse mesmo idioma. Não traduza nada. Se o artigo for em inglês, toda a saída deve ser em inglês. Se for em português, em português. E assim por diante.

PARTE 1 — LIMPAR CONTEÚDO:
Remova todo o ruído de UI do Substack (navegação, botões de inscrição, contagem de curtidas/comentários,
seções "Ready for more?", posts relacionados, seções de comentários, rodapés, avisos de assinatura).
Mantenha apenas: título do artigo (H1), subtítulo/lead, corpo do artigo, citações,
listas, imagens de conteúdo. Saída como markdown no idioma original do artigo.

PARTE 2 — EXTRAIR METADADOS:
Após o conteúdo limpo, produza exatamente este bloco JSON (sem mais nada depois):
```json
{{
  "title": "<título no idioma original — use o hint se for bom: {title_hint}>",
  "description": "<descrição no idioma original — use o hint se for bom: {description_hint}>",
  "date": "<DD/MM/AAAA — extraia do artigo ou reformate o hint: {date_hint}>",
  "ai_summary": "<resumo em exatamente 5 linhas do conteúdo do artigo, no idioma original>"
}}
```

Instruções para os campos JSON:
- "title": Use o hint se for um bom título. Caso contrário, extraia do artigo. Mantenha o idioma original.
- "description": Use o hint se for uma boa descrição. Caso contrário, extraia do artigo. Mantenha o idioma original.
- "date": Converta qualquer data encontrada para o formato DD/MM/AAAA. Se não encontrar, deixe vazio.
- "ai_summary": Exatamente 5 linhas separadas por \\n, resumindo os pontos principais do artigo. No idioma original.

ARTIGO MARKDOWN:
{markdown}"""


def truncate(text: str, max_chars: int = CELL_LIMIT) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    marker = "\n\n[TRUNCADO]"
    return text[: max_chars - len(marker)] + marker


def get_col_map(headers: list) -> dict:
    return {name.strip(): idx for idx, name in enumerate(headers)}


def parse_gemini_response(
    response: str, title_hint: str, description_hint: str, date_hint: str
) -> dict:
    """Split Gemini response into cleaned content and metadata JSON."""
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)

    extracted_content = response.strip()
    metadata = {}

    if json_match:
        extracted_content = response[: json_match.start()].strip()
        try:
            metadata = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    return {
        "extracted_content": extracted_content,
        "title": metadata.get("title") or title_hint or "",
        "description": metadata.get("description") or description_hint or "",
        "date": metadata.get("date") or date_hint or "",
        "ai_summary": metadata.get("ai_summary") or "",
    }


def process_row(
    sheet_id: str, tab: str, row_num: int, row_data: list, col_map: dict
) -> bool:
    """Process one row: scrape, extract, write back. Returns True on success."""
    url = row_data[col_map["URL"]].strip()

    try:
        # Step 1: Scrape with Firecrawl
        print(f"  Raspando {url}...")
        scraped = scrape_article(url)

        if scraped.get("error"):
            print(f"  Falha no scraping: {scraped['error']}")
            return False

        raw_markdown = scraped["markdown"]
        title_hint = scraped["title"] or ""
        description_hint = scraped["description"] or ""
        date_hint = scraped["published_time"] or ""

        # Step 2: LLM extraction and cleaning
        print(f"  Extraindo com Gemini...")
        prompt = EXTRACTION_PROMPT.format(
            title_hint=title_hint,
            description_hint=description_hint,
            date_hint=date_hint,
            markdown=raw_markdown[:MARKDOWN_LIMIT],
        )
        gemini_response = llm_call(prompt, model=MODEL)
        result = parse_gemini_response(
            gemini_response, title_hint, description_hint, date_hint
        )

        # Step 3: Write title and description (C:D)
        write_sheet(
            sheet_id,
            f"{tab}!C{row_num}:D{row_num}",
            [[truncate(result["title"], 1000), truncate(result["description"], 2000)]],
            mode="overwrite",
        )

        # Step 4: Write AI summary (E)
        write_sheet(
            sheet_id,
            f"{tab}!E{row_num}",
            [[truncate(result["ai_summary"], 2000)]],
            mode="overwrite",
        )

        # Step 5: Write content fields — without Extracted=TRUE yet (F:H)
        write_sheet(
            sheet_id,
            f"{tab}!F{row_num}:H{row_num}",
            [[
                truncate(raw_markdown),
                truncate(result["extracted_content"]),
                result["date"],
            ]],
            mode="overwrite",
        )

        # Step 6: Mark as done — only after everything succeeded (I)
        write_sheet(
            sheet_id,
            f"{tab}!I{row_num}",
            [["TRUE"]],
            mode="overwrite",
        )

        print(f"  Concluído: {result['title'][:60]}")
        return True

    except Exception as e:
        print(f"  ERRO: {e}")
        return False


def main(sheet_id: str, tab: str = "Posts"):
    print(f"Lendo planilha {sheet_id} aba '{tab}'...")
    rows = read_sheet(sheet_id, f"{tab}!A1:Z1000")

    if not rows:
        print("Planilha vazia ou ilegível.")
        return

    headers = rows[0]
    col_map = get_col_map(headers)

    required = {
        "URL",
        "Title",
        "Description",
        "original_content",
        "Extracted_content",
        "Date",
        "Extracted",
    }
    missing = required - set(col_map.keys())
    if missing:
        raise ValueError(f"Colunas ausentes na planilha: {missing}")

    extracted_col_idx = col_map["Extracted"]
    url_col_idx = col_map["URL"]

    processed = 0
    skipped = 0
    failed = 0

    for i, row in enumerate(rows[1:], start=2):
        padded = row + [""] * (len(headers) - len(row))

        extracted_val = padded[extracted_col_idx].strip().upper()
        if extracted_val == "TRUE":
            skipped += 1
            continue

        url = padded[url_col_idx].strip()
        if not url:
            print(f"Linha {i}: ignorada — sem URL")
            skipped += 1
            continue

        print(f"\nLinha {i}: {url}")
        success = process_row(sheet_id, tab, i, padded, col_map)

        if success:
            processed += 1
        else:
            failed += 1

    print(
        f"\nConcluído. Processados: {processed} | Ignorados (já feitos): {skipped} | Falhas: {failed}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Processar artigos Substack da planilha Google Sheets"
    )
    parser.add_argument("--sheet-id", default=SHEET_ID, help="Google Sheets ID")
    parser.add_argument("--tab", default="Posts", help="Nome da aba")
    args = parser.parse_args()
    main(args.sheet_id, args.tab)
