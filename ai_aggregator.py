import asyncio
import os
from dotenv import load_dotenv
from groq import Groq
from mistralai import Mistral
from openai import OpenAI

load_dotenv()

# Load API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Clients
groq_client = Groq(api_key=GROQ_API_KEY)
mistral_client = Mistral(api_key=MISTRAL_API_KEY)

openrouter_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# ------------------------------
# ASYNC CALLS
# ------------------------------

async def call_groq(prompt):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

async def call_mistral(prompt):
    try:
        response = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

async def call_openrouter(prompt):
    try:
        response = openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ------------------------------
# JUDGE (AI 4)
# ------------------------------

async def judge_answers(prompt, answers):
    try:
        combined_prompt = f"""
User Question:
{prompt}

Here are three AI answers:

AI 1:
{answers[0]}

AI 2:
{answers[1]}

AI 3:
{answers[2]}

Evaluate which answer is best and explain why.
Then provide a final improved summarized answer.
"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": combined_prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Judge Error: {str(e)}"

# ------------------------------
# MAIN AGGREGATOR
# ------------------------------

async def run_agent(prompt):
    tasks = [
        call_groq(prompt),
        call_mistral(prompt),
        call_openrouter(prompt),
    ]

    results = await asyncio.gather(*tasks)

    # Judge only successful responses
    judge_result = await judge_answers(prompt, results)

    print("\n--------------------------------------------\n")

    print(f"AI 1 llama-3.3-70b-versatile: {results[0]}\n")
    print(f"AI 2 mistral-small-latest: {results[1]}\n")
    print(f"AI 3 meta-llama/llama-3.1-8b-instruct:free: {results[2]}\n")
    print(f"Conclusion by AI 4: {judge_result}\n")

if __name__ == "__main__":
    user_prompt = input("Enter your question: ")
    asyncio.run(run_agent(user_prompt))