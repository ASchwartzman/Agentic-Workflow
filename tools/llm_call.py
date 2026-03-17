"""
Send a prompt to Gemini and return the text response.

Usage:
    python tools/llm_call.py --prompt "Summarize this text" --input .tmp/content.md
    python tools/llm_call.py --prompt "Write a headline for this article" --input .tmp/content.md --output .tmp/result.txt
    python tools/llm_call.py --prompt "What is 2+2?"

Arguments:
    --prompt   The instruction/question to send to the model
    --input    Optional path to a file whose contents are appended to the prompt
    --output   Optional path to write the response (default: prints to stdout)
    --model    Model to use (default: gemini-2.5-flash)
"""

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).parent.parent / ".env")


def llm_call(prompt: str, model: str = "gemini-2.5-flash") -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text


def main():
    parser = argparse.ArgumentParser(description="Call Gemini with a prompt")
    parser.add_argument("--prompt", required=True, help="Instruction or question")
    parser.add_argument("--input", help="Path to file whose content is appended to the prompt")
    parser.add_argument("--output", help="Path to write the response")
    parser.add_argument("--model", default="gemini-2.5-flash", help="Gemini model ID")
    args = parser.parse_args()

    full_prompt = args.prompt
    if args.input:
        content = Path(args.input).read_text(encoding="utf-8")
        full_prompt = f"{args.prompt}\n\n---\n\n{content}"

    result = llm_call(full_prompt, args.model)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"Saved to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
