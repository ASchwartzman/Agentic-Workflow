# Workflow: Extração de Artigos Substack

## Objetivo
Ler URLs de artigos Substack de uma planilha Google Sheets, extrair o conteúdo de cada artigo com Firecrawl, limpar e estruturar o conteúdo com Gemini, e escrever os resultados de volta na planilha. Todo o conteúdo escrito é mantido no idioma original do artigo — sem tradução.

## Planilha Alvo
- **ID:** `15fZgS2sGT589wk1KHX4wWxo7gG2AD4plkn4-L2i9Qlo`
- **Aba:** Posts

## Mapa de Colunas (aba Posts)

| Coluna | Campo             | Papel                                        |
|--------|-------------------|----------------------------------------------|
| A      | Id                | Não modificar                                |
| B      | URL               | Entrada: URL do artigo                       |
| C      | Title             | Título do artigo (idioma original)           |
| D      | Description       | Descrição/subtítulo do artigo (idioma original) |
| E      | AI_summary        | Resumo de 5 linhas (idioma original)         |
| F      | original_content  | Markdown bruto retornado pelo Firecrawl      |
| G      | Extracted_content | Conteúdo limpo pelo Gemini (idioma original) |
| H      | Date              | Data de publicação no formato DD/MM/AAAA     |
| I      | Extracted         | "TRUE" quando linha processada com sucesso   |

## Pré-requisitos
- `FIRECRAWL_API_KEY` configurado em `.env`
- `GEMINI_API_KEY` configurado em `.env`
- `token.json` presente (autenticação Google — gerar com `python tools/google_auth.py`)
- `.venv` ativado

## Como Executar

```bash
source .venv/bin/activate
python tools/process_articles.py

# Com overrides opcionais:
python tools/process_articles.py --sheet-id <ID> --tab <NomeDaAba>
```

## Ferramentas Utilizadas

1. `tools/scrape_article.py` — Scraping com Firecrawl; retorna markdown bruto + metadados (`ogTitle`, `ogDescription`, `publishedTime`)
2. `tools/process_articles.py` — Orquestrador principal; lê a planilha, filtra linhas não processadas, executa todos os passos abaixo
3. `tools/llm_call.py` — Gemini `gemini-3-flash-preview` para limpeza de conteúdo e extração de metadados no idioma original do artigo
4. `tools/sheets_read.py` — Leitura de todas as linhas da planilha
5. `tools/sheets_write.py` — Escrita dos resultados (múltiplas chamadas por linha para não sobrescrever colunas intocadas)

## Ordem de Execução por Linha

Para cada linha não processada:
1. **Scraping** — Firecrawl extrai markdown + metadados da URL
2. **Extração LLM** — Gemini limpa o conteúdo e extrai título, descrição, data e resumo em PT-BR
3. **Escreve Title + Description** (colunas C:D)
4. **Escreve AI_summary** (coluna E)
5. **Escreve original_content + Extracted_content + Date** (colunas F:H)
6. **Escreve Extracted = TRUE** (coluna I) — **somente se todos os passos anteriores concluíram sem erro**

## Comportamento e Limitações Conhecidas

- **Limite de célula do Google Sheets:** 50.000 caracteres. Conteúdo é truncado em 49.000 com marcador `[TRUNCADO]`.
- **Ruído do Substack:** Páginas incluem navegação, botões de assinatura, posts relacionados e contagem de curtidas. O Gemini remove esse ruído e mantém apenas o corpo do artigo.
- **Metadados do Firecrawl:** Título e descrição vêm de `ogTitle`/`ogDescription`; data vem de `publishedTime`. Esses dados são passados como hints ao Gemini, que os confirma ou extrai do corpo do artigo se não estiverem disponíveis.
- **Formato de data:** DD/MM/AAAA.
- **Processamento resiliente:** Linhas são processadas e escritas individualmente. Uma falha em uma linha não afeta as demais.
- **Limite de tokens:** O markdown é truncado em 40.000 caracteres antes de enviar ao Gemini.
- **Colunas intocadas:** `AI_summary` (E) é escrita ou ignorada intencionalmente — nunca sobrescrita de forma acidental, pois as escritas são feitas em ranges `C:D`, `E` e `F:I`.

## Re-execução
Seguro executar a qualquer momento. Linhas com `Extracted=TRUE` são ignoradas automaticamente. Para reprocessar uma linha específica, apague manualmente o valor `TRUE` da célula `Extracted` dessa linha.

## Recuperação de Erros
Falhas são registradas no terminal como `ERRO: ...`. Causas comuns:

- **URL inválida ou inacessível:** Corrija a URL na planilha e re-execute.
- **Rate limit do Firecrawl:** Aguarde alguns minutos e re-execute (linhas já feitas são puladas).
- **Erro de autenticação Google:** Execute `python tools/google_auth.py` para renovar o token.
- **Modelo Gemini inválido:** Atualize a constante `MODEL` em `tools/process_articles.py`. Modelo atual: `gemini-3-flash-preview`. Para listar modelos disponíveis: `python -c "from google import genai; import os; from dotenv import load_dotenv; load_dotenv('.env'); [print(m.name) for m in genai.Client(api_key=os.getenv('GEMINI_API_KEY')).models.list()]"`
- **Firecrawl SDK v2+:** `scrape_article.py` usa `V1FirecrawlApp` (não `FirecrawlApp`). A classe `FirecrawlApp` na v2 é um alias para a nova API que não expõe `scrape_url`.
