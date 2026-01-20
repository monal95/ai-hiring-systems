import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "judge029.p.rapidapi.com")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check if Judge0 is configured
JUDGE0_ENABLED = bool(RAPIDAPI_KEY and len(RAPIDAPI_KEY) > 10)

if JUDGE0_ENABLED:
    print(f"[Judge0] ✅ API configured with host: {RAPIDAPI_HOST}")
else:
    print("[Judge0] ⚠️ WARNING: RAPIDAPI_KEY not configured!")
    print("[Judge0] Code execution will use Groq AI evaluation.")

# Judge0 Language IDs
LANGUAGE_MAP = {
    'python': 71,      # Python (3.8.1)
    'python3': 71,
    'javascript': 63,  # JavaScript (Node.js 12.14.0)
    'java': 62,        # Java (OpenJDK 13.0.1)
    'cpp': 54,         # C++ (GCC 9.2.0)
    'c++': 54,
    'go': 60,          # Go (1.13.5)
    'rust': 73,        # Rust (1.40.0)
    'typescript': 74   # TypeScript (3.7.4)
}


def execute_code(source_code, language, stdin=None):
    """
    Execute code using Judge0 API via RapidAPI
    Falls back to Groq AI evaluation if API fails
    """
    # If Judge0 not configured, use Groq AI
    if not JUDGE0_ENABLED:
        return evaluate_with_groq_ai(source_code, language, stdin)
    
    url = f"https://{RAPIDAPI_HOST}/submissions"
    
    # Get language ID
    lang_id = LANGUAGE_MAP.get(language.lower(), 71)  # Default to Python
    
    # Send source code directly (not base64)
    payload = {
        "language_id": lang_id,
        "source_code": source_code,
        "stdin": stdin or ""
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }

    try:
        print(f"[Judge0] Submitting code to {RAPIDAPI_HOST}...")
        
        # Create submission with wait=true to get result immediately
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            params={"base64_encoded": "false", "wait": "true"},
            timeout=30
        )
        
        print(f"[Judge0] Response status: {response.status_code}")
        
        # Handle subscription/auth errors - fallback to Groq AI
        if response.status_code in [401, 403]:
            print("[Judge0] API subscription issue - falling back to Groq AI evaluation")
            return evaluate_with_groq_ai(source_code, language, stdin)
        
        # Handle rate limiting - fallback to Groq AI
        if response.status_code == 429:
            print("[Judge0] Rate limited - falling back to Groq AI evaluation")
            return evaluate_with_groq_ai(source_code, language, stdin)
        
        # Handle other errors
        if response.status_code not in [200, 201]:
            error_text = response.text[:500] if response.text else "No details"
            print(f"[Judge0] Error: {error_text} - falling back to Groq AI")
            return evaluate_with_groq_ai(source_code, language, stdin)
        
        data = response.json()
        print(f"[Judge0] Got response: {list(data.keys())}")
        
        # Extract result
        status = data.get("status", {})
        status_desc = status.get("description", "Unknown") if isinstance(status, dict) else str(status)
        
        return {
            "stdout": data.get("stdout") or "",
            "stderr": data.get("stderr") or "",
            "compile_output": data.get("compile_output") or "",
            "status": status_desc,
            "time": data.get("time"),
            "memory": data.get("memory")
        }
        
    except requests.exceptions.Timeout:
        print("[Judge0] Request timed out - falling back to Groq AI")
        return evaluate_with_groq_ai(source_code, language, stdin)
    except Exception as e:
        print(f"[Judge0] Exception: {e} - falling back to Groq AI")
        return evaluate_with_groq_ai(source_code, language, stdin)


def run_test_cases(source_code, language, test_cases):
    """
    Run code against multiple test cases with rate limit handling
    """
    results = []
    
    for i, test in enumerate(test_cases):
        print(f"[Judge0] Running test case {i+1}/{len(test_cases)}")
        
        stdin = test.get('input', '')
        # Convert dict/list input to string if necessary
        if isinstance(stdin, (dict, list)):
            import json
            stdin = json.dumps(stdin)
        
        # Add delay between test cases to avoid rate limiting
        if i > 0:
            time.sleep(1)
        
        res = execute_code(source_code, language, stdin)
        
        if "error" in res:
            results.append({
                "input": stdin,
                "passed": False,
                "error": res["error"]
            })
            continue
        
        stdout = res.get("stdout", "").strip()
        expected = str(test.get('expected_output', '')).strip()
        
        passed = stdout == expected
        
        results.append({
            "input": stdin,
            "expected": expected,
            "actual": stdout,
            "passed": passed,
            "status": res.get("status", "Unknown"),
            "stderr": res.get("stderr", ""),
            "compile_output": res.get("compile_output", ""),
            "ai_evaluated": res.get("ai_evaluated", False)
        })
    
    return results


def evaluate_with_groq_ai(source_code, language, stdin=None):
    """
    Use Groq AI to evaluate code execution when Judge0 is not available.
    Works for ANY programming language (Java, Python, C++, JavaScript, etc.)
    """
    print(f"[Groq-Eval] Evaluating {language} code with Groq AI...")
    
    if not GROQ_API_KEY:
        return {
            "stdout": "",
            "stderr": "Groq API key not configured",
            "compile_output": "",
            "status": "Error",
            "ai_evaluated": True
        }
    
    # Create prompt for Groq to evaluate code
    prompt = f"""You are a code execution engine. Execute this {language} code mentally and provide the EXACT output.

CODE:
```{language}
{source_code}
```

INPUT (if any):
{stdin if stdin else "No input provided"}

INSTRUCTIONS:
1. Analyze the code carefully
2. If it's a function definition (like twoSum), mentally execute it with the given input
3. Input format is typically: "[2, 7, 11, 15], 9" meaning args are ([2,7,11,15], 9)
4. Return ONLY the output that would be printed or returned
5. For functions that return a value, output that value
6. If there's a syntax/compilation error, output starts with "ERROR:"
7. If there's a runtime error, output starts with "RUNTIME ERROR:"

OUTPUT (just the result, nothing else):"""

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a precise code executor. Output ONLY the exact result of code execution. No explanations."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result['choices'][0]['message']['content'].strip()
            print(f"[Groq-Eval] AI Output: {output[:100]}...")
            
            # Check for errors in output
            if output.startswith("ERROR:"):
                return {
                    "stdout": "",
                    "stderr": "",
                    "compile_output": output.replace("ERROR:", "").strip(),
                    "status": "Compilation Error",
                    "ai_evaluated": True
                }
            elif output.startswith("RUNTIME ERROR:"):
                return {
                    "stdout": "",
                    "stderr": output.replace("RUNTIME ERROR:", "").strip(),
                    "compile_output": "",
                    "status": "Runtime Error",
                    "ai_evaluated": True
                }
            else:
                return {
                    "stdout": output,
                    "stderr": "",
                    "compile_output": "",
                    "status": "Accepted",
                    "time": "AI-evaluated",
                    "memory": "AI-evaluated",
                    "ai_evaluated": True
                }
        else:
            print(f"[Groq-Eval] API Error: {response.status_code}")
            return {
                "stdout": "",
                "stderr": f"AI evaluation failed: {response.status_code}",
                "compile_output": "",
                "status": "Error",
                "ai_evaluated": True
            }
            
    except Exception as e:
        print(f"[Groq-Eval] Exception: {e}")
        return {
            "stdout": "",
            "stderr": str(e),
            "compile_output": "",
            "status": "Error",
            "ai_evaluated": True
        }


def is_judge0_enabled():
    """Check if Judge0 API is properly configured"""
    return JUDGE0_ENABLED
