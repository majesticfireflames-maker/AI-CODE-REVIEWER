from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found. Create .env file")
    exit(1)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=GROQ_API_KEY)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Code Reviewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(245, 87, 108, 0.3);
        }
        .header h1 { font-size: 3rem; color: white; }
        .header p { color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h2 { color: #f5576c; margin-bottom: 15px; font-size: 1.2rem; }
        textarea {
            width: 100%;
            height: 400px;
            background: rgba(0,0,0,0.3);
            color: #e0e0e0;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            resize: vertical;
        }
        textarea:focus { outline: none; border-color: #f5576c; }
        select {
            width: 100%;
            padding: 12px;
            background: rgba(0,0,0,0.3);
            color: #e0e0e0;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            margin-bottom: 15px;
            font-size: 1rem;
        }
        select:focus { outline: none; border-color: #f5576c; }
        button {
            padding: 14px 40px;
            background: linear-gradient(135deg, #f093fb, #f5576c);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
            margin-top: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(245, 87, 108, 0.4);
        }
        button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .result-card {
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
            border: 1px solid rgba(255,255,255,0.05);
            max-height: 600px;
            overflow-y: auto;
        }
        .result-card h3 {
            color: #f5576c;
            margin-top: 15px;
            margin-bottom: 8px;
        }
        .result-card h3:first-child { margin-top: 0; }
        .result-card ul { padding-left: 20px; margin-bottom: 10px; }
        .result-card li { margin-bottom: 5px; color: #ccc; }
        .result-card pre {
            background: #0a0a0a;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 13px;
            color: #4CAF50;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #f5576c;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .loader-container {
            text-align: center;
            padding: 30px;
        }
        .loader-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            overflow: hidden;
            margin: 10px 0;
        }
        .loader-bar-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #f093fb, #f5576c);
            border-radius: 3px;
            animation: fillLoader 2s ease-in-out forwards;
        }
        @keyframes fillLoader {
            0% { width: 0%; }
            100% { width: 100%; }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            margin: 15px 0;
        }
        .stat-box {
            background: rgba(255,255,255,0.05);
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .stat-box .number { font-size: 1.5rem; font-weight: 700; color: #f5576c; }
        .stat-box .label { font-size: 0.8rem; color: #888; }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2rem; }
            .stats-grid { grid-template-columns: 1fr 1fr; }
        }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 10px; }
        ::-webkit-scrollbar-thumb { background: #f5576c; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Code Reviewer</h1>
            <p>Paste your code and get AI-powered feedback on bugs, performance, security, and more</p>
        </div>
        <div class="grid">
            <div class="card">
                <h2>Code Input</h2>
                <select id="language">
                    <option value="python">Python</option>
                    <option value="javascript">JavaScript</option>
                    <option value="java">Java</option>
                    <option value="cpp">C++</option>
                    <option value="csharp">C#</option>
                    <option value="go">Go</option>
                    <option value="rust">Rust</option>
                    <option value="typescript">TypeScript</option>
                    <option value="php">PHP</option>
                    <option value="ruby">Ruby</option>
                    <option value="swift">Swift</option>
                    <option value="sql">SQL</option>
                </select>
                <textarea id="codeInput" placeholder="Paste your code here...">def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    avg = total / len(numbers)
    return avg

numbers = [1, 2, 3, 4, 5]
result = calculate_average(numbers)
print("Average is: " + result)
</textarea>
                <button id="reviewBtn">Review Code</button>
            </div>
            <div class="card">
                <h2>Review Results</h2>
                <div id="result">
                    <div class="result-card" style="text-align:center;color:#888;padding:40px 20px;">
                        <div style="font-size:3rem;margin-bottom:10px;">&#128104;&#8205;&#128187;</div>
                        <p>Paste your code and click Review Code<br>to get AI-powered feedback</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
        const reviewBtn = document.getElementById('reviewBtn');
        const codeInput = document.getElementById('codeInput');
        const language = document.getElementById('language');
        const resultDiv = document.getElementById('result');

        reviewBtn.addEventListener('click', async function() {
            const code = codeInput.value.trim();
            const lang = language.value;

            if (!code) {
                alert('Please paste some code first');
                return;
            }

            reviewBtn.disabled = true;
            reviewBtn.innerHTML = '<div class="loading"></div> Analyzing...';

            // Show loader with progress
            resultDiv.innerHTML = `
                <div class="result-card">
                    <div class="loader-container">
                        <div class="loading"></div>
                        <p style="margin-top:10px;color:#888;">AI is analyzing your code...</p>
                        <div class="loader-bar"><div class="loader-bar-fill"></div></div>
                        <p style="font-size:0.8rem;color:#666;margin-top:5px;">This may take a few seconds</p>
                    </div>
                </div>
            `;

            try {
                const response = await fetch('/review', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code, language: lang })
                });

                const data = await response.json();

                if (data.error) {
                    resultDiv.innerHTML = '<div class="result-card"><p style="color:#ff6b6b;">Error: ' + data.error + '</p></div>';
                } else {
                    resultDiv.innerHTML = formatResults(data);
                }

            } catch (error) {
                resultDiv.innerHTML = '<div class="result-card"><p style="color:#ff6b6b;">Error: ' + error.message + '</p></div>';
            }

            reviewBtn.disabled = false;
            reviewBtn.innerHTML = 'Review Code';
        });

        function formatResults(data) {
            let html = '<div class="result-card">';

            // Extract stats from the analysis
            let bugCount = 0;
            let perfCount = 0;
            let secCount = 0;

            const sections = data.answer.split(/\\n(?=[A-Z])/);

            sections.forEach(function(section) {
                if (section.includes('Bugs')) {
                    bugCount = countItems(section);
                    html += '<h3>Bugs Found</h3><ul>' + formatList(section) + '</ul>';
                } else if (section.includes('Performance')) {
                    perfCount = countItems(section);
                    html += '<h3>Performance Improvements</h3><ul>' + formatList(section) + '</ul>';
                } else if (section.includes('Security')) {
                    secCount = countItems(section);
                    html += '<h3>Security Issues</h3><ul>' + formatList(section) + '</ul>';
                } else if (section.includes('Explanation')) {
                    html += '<h3>Code Explanation</h3><p>' + formatExplanation(section) + '</p>';
                } else if (section.includes('Suggestions')) {
                    html += '<h3>Improvement Suggestions</h3><ul>' + formatList(section) + '</ul>';
                } else if (section.includes('Improved')) {
                    html += '<h3>Improved Code</h3><pre>' + formatCode(section) + '</pre>';
                }
            });

            // Add stats at the top
            html = `
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="number">${bugCount}</div>
                        <div class="label">Bugs Found</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">${perfCount}</div>
                        <div class="label">Optimizations</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">${secCount}</div>
                        <div class="label">Security Issues</div>
                    </div>
                </div>
            ` + html;

            html += '</div>';
            return html;
        }

        function countItems(section) {
            const lines = section.split('\\n').filter(function(line) {
                return line.match(/^[-*•]|\\d\\./);
            });
            return lines.length || 1;
        }

        function formatList(section) {
            const lines = section.split('\\n').filter(function(line) {
                return line.match(/^[-*•]|\\d\\./);
            });
            if (lines.length === 0) {
                const content = section.replace(/^[^:]*:/, '').trim();
                return '<li>' + content + '</li>';
            }
            return lines.map(function(line) {
                const clean = line.replace(/^[-*•]\\s*|^\\d\\.\\s*/, '').trim();
                return '<li>' + clean + '</li>';
            }).join('');
        }

        function formatExplanation(section) {
            return section.replace(/^[^:]*:/, '').trim();
        }

        function formatCode(section) {
            const lines = section.split('\\n');
            const codeLines = lines.filter(function(line) {
                return !line.includes('Improved');
            });
            return codeLines.join('\\n').trim();
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.post("/review")
async def review(request: Request):
    try:
        data = await request.json()
        code = data.get("code", "")
        language = data.get("language", "python")

        if not code:
            return JSONResponse({"error": "No code provided"})

        prompt = f"""You are an expert code reviewer. Analyze the following {language} code and provide a detailed review in this exact format:

Bugs Found:
- List any bugs or errors

Performance Improvements:
- Suggest performance optimizations

Security Issues:
- Identify any security vulnerabilities

Code Explanation:
- Explain what the code does in plain English

Improvement Suggestions:
- Suggest improvements for code quality and readability

Improved Code:
- Write the improved version of the code

Code to review:
```{language}
{code}
```"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer. Be thorough, specific, and helpful. Always provide improved code."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        answer = completion.choices[0].message.content

        return JSONResponse({"answer": answer})

    except Exception as e:
        return JSONResponse({"error": str(e)})

if __name__ == "__main__":
    print("=" * 60)
    print("AI CODE REVIEWER")
    print("=" * 60)
    print("Open: http://localhost:8000")
    print("Paste code and get AI-powered review")
    print("Powered by Groq Llama 3.3 70B")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)