# Agentic Workflow (WAT Framework)

Welcome to the **Agentic Workflow** project! This repository implements the **WAT (Workflows, Agents, Tools)** framework, a powerful architecture that separates artificial intelligence reasoning from deterministic code execution to build reliable, scalable AI systems.

## 🧠 The WAT Architecture

This project is built on three core layers:

1. **Workflows (`workflows/`)**: Markdown Standard Operating Procedures (SOPs). They act as instructions for the AI Agent, defining objectives, required inputs, edge cases, and which tools to use.
2. **Agents (The AI)**: The probabilistic decision-maker (like Claude). The Agent reads workflows, orchestrates the process, handles unexpected failures gracefully, and strings tools together to achieve the final goal.
3. **Tools (`tools/`)**: Deterministic Python scripts that do the actual execution (API calls, web scraping, writing to Google Sheets, file parsing). They are predictable, fast, and testable.

*Why this matters:* By keeping the AI out of direct script execution and focused solely on orchestration, the system's accuracy and reliability increase significantly.

## 📂 Project Structure

```text
.
├── .tmp/               # Disposable/temporary processing files (e.g., intermediate JSON or scraped HTML)
├── tools/              # Python scripts for execution (e.g., scrape_url.py, sheets_write.py)
├── workflows/          # Markdown SOPs defining tasks (e.g., extract_substack_articles.md)
├── CLAUDE.md           # Instructions for the AI Agent detailing how to operate in this repo
├── .env                # API keys and environment variables (ignored by git list)
├── .env.example        # Template for environment variables
└── README.md           # This file
```

*(Note: Files like `credentials.json` and `token.json` for Google Auth are gitignored for security).*

## 🚀 Getting Started

Follow these steps to set up the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/ASchwartzman/Agentic-Workflow.git
cd Agentic-Workflow
```

### 2. Set Up a Virtual Environment (Recommended)
It is highly recommended to use a Python virtual environment to manage dependencies.
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .\venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies
Install the required packages for the Python tools (e.g., web scraping, Google API, LLM SDKs).
```bash
# Example if using standard libraries required by tools:
pip install requests beautifulsoup4 google-api-python-client google-auth-httplib2 google-auth-oauthlib python-dotenv anthropic openai
```

### 4. Configuration & API Keys
Copy the example environment file:
```bash
cp .env.example .env
```
Open `.env` and fill in your actual API keys:
- `OPENAI_API_KEY=`
- `ANTHROPIC_API_KEY=`
- `GOOGLE_SHEETS_ID=`

**Google Authentication:**
If using the Google Sheets tools, secure your `credentials.json` from the Google Cloud Console and place it in the root folder. Running a Google Tool the first time will prompt login and generate a `token.json`.

## 🤖 How to Use

1. **Choose a Workflow**: Identify what you want the AI to do (e.g., `workflows/extract_substack_articles.md`).
2. **Prompt the Agent**: Ask your AI Agent (like a Claude desktop app, Cursor, or CLI) to execute the specific workflow.
   - *Example prompt:* "Please run the `extract_substack_articles.md` workflow for the URL https://example.substack.com"
3. **Agent Orchestration**: The AI will read the workflow, gather inputs, execute the appropriate scripts in `tools/`, and save intermediate files in `.tmp/`.
4. **Final Deliverables**: The AI will output final results to cloud services (like Google Sheets) or a final directory, exactly as established by the workflow.

## 🛠 Contributing & The Self-Improvement Loop

When extending the project or hitting an error, follow the **Self-Improvement Loop**:
1. Identify what broke or what's missing.
2. Build or fix the script in `tools/`.
3. Verify the script works reliably.
4. Update or document the behavior in the relevant `workflows/` Markdown file.

This ensures the agent learns and the system becomes more robust over time.
