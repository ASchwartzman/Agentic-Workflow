---
description: Extrair todos os artigos de um autor do Substack
---

# Workflow: Extração de Artigos de um Autor do Substack

## Objetivo
Receber o link da página de um escritor do Substack (ex: `https://substack.com/@compoundwithai`), criar uma planilha no Google Sheets com a estrutura padrão, mapear todos os links de artigos dessa página, preencher a planilha com os links faltantes e processar o conteúdo utilizando o fluxo de extração de artigos existente.

## Processo

### 1. Criar a Planilha no Google Sheets (se não existir)
O agente ou script deve criar uma nova planilha no Google Sheets para o autor analisado (ex: "Artigos Substack - [Nome do Autor]") e garantir que existe uma aba chamada `Posts` com as seguintes colunas de cabeçalho (linha 1):

| Coluna | Campo             | Papel                                        |
|--------|-------------------|----------------------------------------------|
| A      | Id                | Identificador único                          |
| B      | URL               | URL do artigo                                |
| C      | Title             | Título do artigo                             |
| D      | Description       | Descrição/subtítulo                          |
| E      | AI_summary        | Resumo gerado pela IA                        |
| F      | original_content  | Markdown bruto                               |
| G      | Extracted_content | Conteúdo limpo pela IA                       |
| H      | Date              | Data de publicação                           |
| I      | Extracted         | Status de processamento ("TRUE")             |

### 2. Identificar Links dos Artigos
- Ler a página do autor utilizando uma ferramenta de scraping (ex: Firecrawl).
- Mapear a lista contendo as URLs de todos os posts publicados por aquele escritor.
- Comparar os links extraídos com os que já existem na planilha (se a planilha já estiver populada de rodadas passadas).
- Adicionar novas linhas na planilha para os artigos que ainda não foram inseridos, preenchendo apenas a coluna `URL` (e opcionalmente `Id`).

### 3. Extrair e Processar o Conteúdo dos Artigos
Executar o workflow estabelecido em `workflows/extract_substack_articles.md` direcionado para a planilha recém configurada e populada. 

Para que este passo seja executado automaticamente, o script de processamento de artigos deve suportar a recepção do ID da planilha em que os novos links foram inseridos.

Para cada linha ainda não extraída (`Extracted` vazio):
1. Fazer o scrap da URL do novo artigo via Firecrawl.
2. Extrair metadados e limpar o conteúdo bruto via Google Gemini.
3. Atualizar a linha correspondente na planilha com as informações (Título, Resumo, Conteúdo, Data).
4. Marcar a coluna `Extracted` com `TRUE` ao concluir o sucesso. 

## Ferramentas e Implementação (Sugestão)
- **Criação de Planilha/Leitura de Linhas:** Dependerá da API Google Sheets (ex. `tools/sheets_write.py`, `tools/sheets_read.py` expandidos).
- **Mapeamento de Artigos:** Script Python que faz fetch em `https://substack.com/@author` e busca os links sob o domínio da página. Substack geralmente usa o layout de listas ou sitemaps que podem ser parseados por Beautiful Soup ou diretamente extraídos pelo Firecrawl (crawl/map features).
- **Pipeline de Extração:** Reutilizar o script `tools/process_articles.py` passando o novo `<sheet-id>`.

## Instrução de Uso
Sempre que o usuário fornecer o link da página do Substack de um autor, siga estes passos para inicializar a estrutura, mapear o que falta e colocar a extração em andamento.
