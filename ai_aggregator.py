import asyncio
import os
import re
import sys
import itertools
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from mistralai import Mistral
from openai import OpenAI

# ------------------------------
# LOAD ENV
# ------------------------------

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

openrouter_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# ------------------------------
# SIMPLE QUERY DETECTOR
# ------------------------------

def is_simple_query(prompt: str) -> bool:
    prompt = prompt.lower().strip()

    if re.fullmatch(r"[\d\s\+\-\*/\.]+", prompt):
        return True

    if "today" in prompt and "date" in prompt:
        return True

    if len(prompt.split()) <= 3:
        return True

    return False


# ------------------------------
# SPINNER
# ------------------------------

async def spinner(stop_event: asyncio.Event):
    while not stop_event.is_set():
        for char in ["⏳ Thinking.", "⏳ Thinking..", "⏳ Thinking..."]:
            if stop_event.is_set():
                break
            sys.stdout.write("\r" + char)
            sys.stdout.flush()
            await asyncio.sleep(0.5)

    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()


# ------------------------------
# BLOCKING CALLS
# ------------------------------

def _call_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()


def _call_mistral(prompt):
    response = mistral_client.chat.complete(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

def _call_openrouter(prompt):
    try:
        response = openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return None  # Return None instead of error string
"""
def _call_openrouter(prompt):
    response = openrouter_client.chat.completions.create(
        model="meta-llama/llama-3.1-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
"""

# ------------------------------
# ASYNC WRAPPERS
# ------------------------------

async def call_groq(prompt):
    try:
        return await asyncio.to_thread(_call_groq, prompt)
    except Exception as e:
        return f"[Groq Error: {e}]"


async def call_mistral(prompt):
    try:
        return await asyncio.to_thread(_call_mistral, prompt)
    except Exception as e:
        return f"[Mistral Error: {e}]"


async def call_openrouter(prompt):
    try:
        return await asyncio.to_thread(_call_openrouter, prompt)
    except Exception as e:
        return f"[OpenRouter Error: {e}]"


# ------------------------------
# JUDGE (AI 4)
# ------------------------------

async def judge_answers(prompt, answers):
    combined_prompt = f"""
User Question:
{prompt}

AI 1:
{answers[0]}

AI 2:
{answers[1]}

AI 3:
{answers[2]}

Evaluate which answer is best and explain why.
Then provide a final improved summarized answer.
"""
    return await call_groq(combined_prompt)


# ------------------------------
# FULL MULTI-LLM PIPELINE
# ------------------------------
# ------------------------------
# FULL MULTI-LLM PIPELINE (RESILIENT)
# ------------------------------

async def run_full_pipeline(prompt):

    # Spinner for user feedback
    stop_event = asyncio.Event()
    spinner_task = asyncio.create_task(spinner(stop_event))

    try:
        # Run all 3 AIs concurrently
        results = await asyncio.gather(
            call_groq(prompt),
            call_mistral(prompt),
            call_openrouter(prompt),
        )
    finally:
        stop_event.set()
        await spinner_task

    # Filter out any failed responses (None or error strings)
    valid_results = [r for r in results if r and not r.startswith("[")]

    if not valid_results:
        print("\n❌ All AI responses failed. Please try again later.\n")
        return

    # Judge Phase only evaluates valid results
    stop_event = asyncio.Event()
    spinner_task = asyncio.create_task(spinner(stop_event))

    try:
        judge_result = await judge_answers(prompt, valid_results)
    finally:
        stop_event.set()
        await spinner_task

    print("\n--------------------------------------------\n")
    print(f"AI 1 (Groq):\n{results[0]}\n")
    print(f"AI 2 (Mistral):\n{results[1]}\n")
    print(f"AI 3 (OpenRouter):\n{results[2] if results[2] else '[Failed/Unavailable]'}\n")
    print(f"Conclusion by AI 4:\n{judge_result}\n")
"""
async def run_full_pipeline(prompt):

    stop_event = asyncio.Event()
    spinner_task = asyncio.create_task(spinner(stop_event))

    try:
        results = await asyncio.gather(
            call_groq(prompt),
            call_mistral(prompt),
            call_openrouter(prompt),
        )

    finally:
        stop_event.set()
        await spinner_task

    # Judge Phase
    stop_event = asyncio.Event()
    spinner_task = asyncio.create_task(spinner(stop_event))

    try:
        judge_result = await judge_answers(prompt, results)
    finally:
        stop_event.set()
        await spinner_task

    print("\n--------------------------------------------\n")
    print(f"AI 1 (Groq):\n{results[0]}\n")
    print(f"AI 2 (Mistral):\n{results[1]}\n")
    print(f"AI 3 (OpenRouter):\n{results[2]}\n")
    print(f"Conclusion by AI 4:\n{judge_result}\n")

"""
# ------------------------------
# FAST MODE
# ------------------------------

async def run_fast_mode(prompt):

    stop_event = asyncio.Event()
    spinner_task = asyncio.create_task(spinner(stop_event))

    try:
        result = await call_groq(prompt)
    finally:
        stop_event.set()
        await spinner_task

    print("\n--------------------------------------------\n")
    print(f"AI 4 (Fast Mode - Groq Only):\n{result}\n")


# ------------------------------
# INTERACTIVE LOOP
# ------------------------------

async def interactive_loop():
    print("\n🚀 AI Aggregator Agent Running")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_prompt = input("Enter your question: ").strip()

        if user_prompt.lower() in ["exit", "quit"]:
            print("\n👋 Exiting AI Aggregator Agent.")
            break

        if not user_prompt:
            print("⚠️ Please enter a valid question.\n")
            continue

        try:
            if is_simple_query(user_prompt):
                print("\n⚡ Simple query detected → Using AI 4 only\n")
                await run_fast_mode(user_prompt)
            else:
                print("\n🚀 Complex query detected → Running Full Multi-LLM Pipeline\n")
                await run_full_pipeline(user_prompt)

        except Exception as e:
            print(f"\n❌ Unexpected Error: {e}\n")


# ------------------------------
# ENTRY POINT
# ------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(interactive_loop())
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")