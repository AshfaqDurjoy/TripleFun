<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Aggregator Agent - Multi LLM Orchestration</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f4f6f8;
            color: #333;
        }
        h1, h2, h3 {
            color: #1f2937;
        }
        code {
            background-color: #e5e7eb;
            padding: 4px 6px;
            border-radius: 4px;
        }
        pre {
            background-color: #111827;
            color: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
        .section {
            margin-bottom: 40px;
        }
        .highlight {
            background-color: #dbeafe;
            padding: 10px;
            border-left: 5px solid #2563eb;
        }
    </style>
</head>
<body>

<h1>AI Aggregator Agent</h1>

<p>
This project implements a <strong>Multi-LLM Orchestration System</strong> using asynchronous Python.
The agent queries three different AI providers simultaneously and then uses a fourth AI to evaluate and synthesize their answers.
</p>

<div class="section">
<h2>Architecture Overview</h2>

<p>The AI Agent uses the following stack:</p>

<ul>
    <li><strong>AI 1:</strong> Groq API → llama-3.3-70b-versatile</li>
    <li><strong>AI 2:</strong> Mistral API → mistral-small-latest</li>
    <li><strong>AI 3:</strong> OpenRouter API → meta-llama/llama-3.1-8b-instruct:free</li>
    <li><strong>AI 4 (Judge):</strong> Groq API → llama-3.3-70b-versatile</li>
</ul>

<p>Execution Flow:</p>

<pre>
User Prompt
     │
 ┌───┼─────────────┐
 │   │             │
Groq  Mistral   OpenRouter
 │   │             │
 └───┼─────────────┘
     │
Groq (Judge Model)
     │
Final Conclusion
</pre>

<p>
All three AI models are called <strong>asynchronously</strong> using Python's <code>asyncio</code> library.
This ensures the user does not wait for each model sequentially.
</p>
</div>

<div class="section">
<h2>Key Features</h2>

<ul>
    <li>Parallel AI querying using asyncio</li>
    <li>Fail-safe fallback mechanism</li>
    <li>Free-tier compatible APIs</li>
    <li>Secure API key management using .env file</li>
    <li>Final synthesized evaluation by a judge AI</li>
</ul>

<div class="highlight">
If one AI fails, the system still displays the remaining responses and produces a final judgment.
</div>
</div>

<div class="section">
<h2>Step 1 — Obtain Free API Keys</h2>

<h3>1. Groq</h3>
<ol>
    <li>Go to https://console.groq.com</li>
    <li>Create a free account</li>
    <li>Generate an API key</li>
</ol>

<h3>2. Mistral</h3>
<ol>
    <li>Go to https://console.mistral.ai</li>
    <li>Create a free account</li>
    <li>Generate an API key</li>
</ol>

<h3>3. OpenRouter</h3>
<ol>
    <li>Go to https://openrouter.ai</li>
    <li>Create a free account</li>
    <li>Generate an API key</li>
</ol>
</div>

<div class="section">
<h2>Step 2 — Install Dependencies</h2>

<p>Run this command in your project directory:</p>

<pre>pip install groq mistralai openai python-dotenv</pre>

</div>

<div class="section">
<h2>Step 3 — Create .env File</h2>

<p>Create a file named <code>.env</code> in the same directory as your Python script.</p>

<pre>
GROQ_API_KEY=your_groq_key_here
MISTRAL_API_KEY=your_mistral_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
</pre>

<p>Important Rules:</p>
<ul>
    <li>No quotes around keys</li>
    <li>No spaces around "="</li>
    <li>File must be named exactly ".env"</li>
</ul>
</div>

<div class="section">
<h2>Step 4 — Project Structure</h2>

<pre>
project-folder/
│
├── ai_aggregator.py
├── .env
└── README.html
</pre>

</div>

<div class="section">
<h2>Step 5 — Run the AI Agent</h2>

<p>Execute the script using:</p>

<pre>python ai_aggregator.py</pre>

<p>You will be prompted to enter a question:</p>

<pre>Enter your question: What is quantum computing?</pre>

<p>The output will appear in this format:</p>

<pre>
AI 1 llama-3.3-70b-versatile: [Answer]

AI 2 mistral-small-latest: [Answer]

AI 3 meta-llama/llama-3.1-8b-instruct:free: [Answer]

Conclusion by AI 4: [Evaluation and Final Summary]
</pre>

</div>

<div class="section">
<h2>Error Handling</h2>

<p>
If one API fails (network issue, quota limit, invalid key), the agent:
</p>

<ul>
    <li>Displays an error message for that model</li>
    <li>Continues processing other models</li>
    <li>Still produces a final conclusion using available answers</li>
</ul>

</div>

<div class="section">
<h2>How the Judge AI Works</h2>

<p>
The Judge AI receives:
</p>

<ul>
    <li>The original user prompt</li>
    <li>All three AI responses</li>
</ul>

<p>
It then:
</p>

<ol>
    <li>Compares factual accuracy</li>
    <li>Evaluates clarity and completeness</li>
    <li>Identifies the strongest response</li>
    <li>Produces an improved final summary</li>
</ol>

<p>
This creates a meta-reasoning layer, improving reliability and response quality.
</p>

</div>

<div class="section">
<h2>Technical Notes</h2>

<ul>
    <li>Uses asyncio.gather() for parallel execution</li>
    <li>Uses OpenRouter via OpenAI-compatible client</li>
    <li>Secure environment variable loading with python-dotenv</li>
    <li>Production-ready structure for scaling</li>
</ul>

</div>

<div class="section">
<h2>Future Improvements</h2>

<ul>
    <li>Streaming responses</li>
    <li>Token usage tracking</li>
    <li>Response scoring system</li>
    <li>FastAPI integration</li>
    <li>Docker containerization</li>
</ul>

</div>

<hr>

<p>
Developed as a demonstration of Multi-LLM Orchestration and AI Ensemble Evaluation.
</p>

</body>
</html>