"""
Groq AI Configuration
Handles AI-powered features using Groq API (LLaMA3 / Mixtral)
"""

import os
import json
import requests
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Groq Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
DEFAULT_MODEL = 'llama-3.3-70b-versatile'  # Best available model


def call_groq(prompt: str, system_prompt: str = None, model: str = DEFAULT_MODEL, max_tokens: int = 1024, retries: int = 5) -> Optional[str]:
    """
    Call Groq API with a prompt and return the response with retry logic
    """
    import time
    
    if not GROQ_API_KEY:
        print('[Groq] Error: GROQ_API_KEY not set in environment variables')
        return None
    
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    for attempt in range(retries + 1):
        try:
            if attempt > 0:
                delay = (2 ** attempt) + (attempt * 2)
                print(f"[Groq] Retry attempt {attempt} after {delay}s delay...")
                time.sleep(delay)
                
            print(f"[Groq] Calling API with model: {model}")
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                result = data['choices'][0]['message']['content']
                print(f"[Groq] Success! Response length: {len(result)} chars")
                return result
            elif response.status_code == 429:
                print(f"[Groq] Rate limit hit (429).")
                # Switch to fallback model immediately on first 429
                if model != "llama-3.1-8b-instant":
                    print(f"[Groq] Emergency fallback to llama-3.1-8b-instant")
                    model = "llama-3.1-8b-instant"
                    payload["model"] = model
                continue
            else:
                print(f"[Groq] Error {response.status_code}: {response.text}")
                if attempt == retries:
                    return None
                
        except Exception as e:
            print(f"[Groq] Exception in call_groq: {e}")
            if attempt == retries:
                return None
    
    return None


def generate_job_description(job_title: str, department: str = "", location: str = "") -> dict:
    """Generate a complete job description using AI"""
    
    system_prompt = """You are an expert HR professional and job description writer. 
    Generate professional, engaging job descriptions that attract top talent.
    Always respond with valid JSON only, no markdown or extra text."""
    
    prompt = f"""Generate a complete job description for the following position:

Job Title: {job_title}
Department: {department if department else 'Not specified'}
Location: {location if location else 'Remote'}

Respond with ONLY a JSON object (no markdown, no code blocks) in this exact format:
{{
    "description": "A compelling 2-3 paragraph job description",
    "responsibilities": ["responsibility 1", "responsibility 2", "responsibility 3", "responsibility 4", "responsibility 5"],
    "must_have_skills": ["skill 1", "skill 2", "skill 3", "skill 4", "skill 5"],
    "nice_to_have_skills": ["skill 1", "skill 2", "skill 3"],
    "experience_required": "X+ years",
    "education": "Required education level",
    "benefits": ["benefit 1", "benefit 2", "benefit 3"]
}}"""

    response = call_groq(prompt, system_prompt, max_tokens=2048)
    
    if response:
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[Groq] JSON parse error: {e}")
            print(f"[Groq] Raw response: {response[:500]}")
    
    # Fallback response
    return {
        "description": f"We are looking for a talented {job_title} to join our team.",
        "responsibilities": [f"Core {job_title} responsibilities"],
        "must_have_skills": ["Communication", "Problem Solving", "Team Work"],
        "nice_to_have_skills": ["Leadership"],
        "experience_required": "2+ years",
        "education": "Bachelor's degree",
        "benefits": ["Competitive salary", "Health insurance", "Remote work"]
    }


def suggest_skills(job_title: str, current_skills: list = None) -> list:
    """Suggest relevant skills for a job title"""
    
    system_prompt = "You are an HR expert. Suggest relevant technical and soft skills for job positions. Respond with ONLY a JSON array of strings."
    
    current = f"\nAlready selected skills: {', '.join(current_skills)}" if current_skills else ""
    
    prompt = f"""Suggest 10 relevant skills for a {job_title} position.{current}

Respond with ONLY a JSON array of skill strings, no explanation:
["skill1", "skill2", "skill3", ...]"""

    response = call_groq(prompt, system_prompt, max_tokens=256)
    
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            return json.loads(cleaned.strip())
        except:
            pass
    
    # Fallback
    return ["Python", "JavaScript", "SQL", "Communication", "Problem Solving", 
            "Team Work", "Agile", "Git", "API Development", "Cloud Services"]


def generate_rejection_email(candidate_name: str, job_title: str, skills: list = None) -> dict:
    """Generate a personalized rejection email using AI"""
    
    system_prompt = "You are a professional HR representative writing empathetic rejection emails."
    
    skills_text = f"The candidate has skills in: {', '.join(skills[:5])}" if skills else ""
    
    prompt = f"""Write a professional, empathetic rejection email for:
- Candidate Name: {candidate_name}
- Position Applied: {job_title}
{skills_text}

The email should:
1. Thank them for applying
2. Acknowledge their skills positively
3. Explain we're moving forward with other candidates
4. Encourage them to apply for future roles
5. Be warm but professional

Respond with ONLY JSON (no markdown):
{{"subject": "email subject", "body": "plain text body", "html_body": "HTML formatted body"}}"""

    response = call_groq(prompt, system_prompt)
    
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            return json.loads(cleaned.strip())
        except:
            pass
    
    # Fallback
    return {
        "subject": f"Update on Your Application for {job_title}",
        "body": f"Dear {candidate_name},\n\nThank you for your interest in the {job_title} position. After careful consideration, we have decided to move forward with other candidates.\n\nWe wish you the best in your career journey.\n\nBest regards,\nThe Hiring Team",
        "html_body": f"<p>Dear {candidate_name},</p><p>Thank you for your interest in the <strong>{job_title}</strong> position. After careful consideration, we have decided to move forward with other candidates.</p><p>We wish you the best in your career journey.</p><p>Best regards,<br>The Hiring Team</p>"
    }


def generate_application_confirmation_email(candidate_name: str, job_title: str) -> dict:
    """Generate application confirmation email"""
    
    system_prompt = "You are a friendly HR representative confirming job applications."
    
    prompt = f"""Write a warm application confirmation email for:
- Candidate: {candidate_name}
- Position: {job_title}

The email should confirm receipt of their application and explain next steps.

Respond with ONLY JSON (no markdown):
{{"subject": "email subject", "body": "plain text", "html_body": "HTML body"}}"""

    response = call_groq(prompt, system_prompt)
    
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            return json.loads(cleaned.strip())
        except:
            pass
    
    return {
        "subject": f"Application Received - {job_title}",
        "body": f"Dear {candidate_name},\n\nThank you for applying for the {job_title} position. We have received your application and will review it shortly.\n\nBest regards,\nThe Hiring Team",
        "html_body": f"<p>Dear {candidate_name},</p><p>Thank you for applying for the <strong>{job_title}</strong> position. We have received your application and will review it shortly.</p><p>Best regards,<br>The Hiring Team</p>"
    }


def generate_shortlisted_email(candidate_name: str, job_title: str, next_steps: str = "interview") -> dict:
    """Generate shortlisted/interview invitation email"""
    
    system_prompt = "You are an enthusiastic HR representative inviting candidates for interviews."
    
    prompt = f"""Write an exciting shortlist notification email for:
- Candidate: {candidate_name}  
- Position: {job_title}
- Next Step: {next_steps}

The email should congratulate them and explain the next steps.

Respond with ONLY JSON (no markdown):
{{"subject": "email subject", "body": "plain text", "html_body": "HTML body"}}"""

    response = call_groq(prompt, system_prompt)
    
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            return json.loads(cleaned.strip())
        except:
            pass
    
    return {
        "subject": f"Great News! You've Been Shortlisted - {job_title}",
        "body": f"Dear {candidate_name},\n\nCongratulations! We are pleased to inform you that you have been shortlisted for the {job_title} position.\n\nWe will contact you shortly to schedule the next steps.\n\nBest regards,\nThe Hiring Team",
        "html_body": f"<p>Dear {candidate_name},</p><p>Congratulations! We are pleased to inform you that you have been shortlisted for the <strong>{job_title}</strong> position.</p><p>We will contact you shortly to schedule the next steps.</p><p>Best regards,<br>The Hiring Team</p>"
    }


def clean_json_response(response: str) -> str:
    """Robustly clean JSON response from AI model"""
    if not response:
        return ""
    
    cleaned = response.strip()
    
    # Remove markdown code blocks if present
    if "```json" in cleaned:
        cleaned = cleaned.split("```json", 1)[1]
        if "```" in cleaned:
            cleaned = cleaned.rsplit("```", 1)[0]
    elif "```" in cleaned:
        cleaned = cleaned.split("```", 1)[1]
        if "```" in cleaned:
            cleaned = cleaned.rsplit("```", 1)[0]
            
    return cleaned.strip()


def generate_interview_questions(job_requirements: dict, candidate_skills: list, candidate_id: str = None, job_id: str = None, job_title: str = "Software Engineer") -> dict:
    """Generate AI-powered interview questions with competitive programming coding challenges"""
    
    must_have_skills = job_requirements.get('must_have', [])[:7]
    nice_to_have_skills = job_requirements.get('nice_to_have', [])[:3]
    
    candidate_skills_lower = [s.lower().strip() for s in candidate_skills] if candidate_skills else []
    must_have_lower = [s.lower().strip() for s in must_have_skills]
    
    matched_skills = []
    
    for job_skill in must_have_skills:
        skill_matched = False
        for cand_skill in candidate_skills:
            if (job_skill.lower().strip() in cand_skill.lower() or 
                cand_skill.lower() in job_skill.lower().strip() or
                any(word in cand_skill.lower() for word in job_skill.lower().split())):
                matched_skills.append(cand_skill)
                skill_matched = True
                break
    
    matched_skills = list(dict.fromkeys(matched_skills))[:5]
    if not matched_skills:
        matched_skills = candidate_skills[:5] if candidate_skills else must_have_skills[:5]
    
    matched_str = ', '.join(matched_skills) if matched_skills else "general programming"
    all_required_str = ', '.join(must_have_skills) if must_have_skills else "general programming"
    
    print(f"[Groq] COMPETITIVE PROGRAMMING CHALLENGE GENERATION:")
    print(f"[Groq]   - Candidate skills: {candidate_skills[:8] if candidate_skills else 'None'}")
    print(f"[Groq]   - Job requires: {must_have_skills}")
    print(f"[Groq]   - MATCHED skills: {matched_skills}")
    print(f"[Groq]   - Generating interview with competitive programming challenges")

    # Generate FULL INTERVIEW in ONE call to avoid rate limits (429)
    system_prompt = (
        "You are an expert competitive programming interviewer. Generate 15 Technical + 20 "
        "Behavioral + 2 Coding challenges (NOT job-specific, pure competitive programming problems)."
    )

    prompt = f"""Generate a COMPLETE interview for a {job_title} candidate with COMPETITIVE PROGRAMMING focus.

For CODING CHALLENGES (2 total) - IMPORTANT: These must be COMPETITIVE PROGRAMMING questions, NOT job-specific:

1. EASY/MEDIUM Challenge (Choose from these categories):
    - Array/String manipulation problems
    - Hash Map/Set problems
    - Math and simulation problems
    - Gaming/simulation logic problems
    - Basic DSA (sorted arrays, searching, sorting)
    Examples: "Two Sum", "Longest Substring Without Repeating", "Remove Duplicates", "Majority Element"
    MUST include (no placeholders): title, description, constraints, AT LEAST 2 examples (input/output + explanation), AT LEAST 2 test_cases with input AND expected_output, hints

2. HARD Challenge (Choose from these):
    - Dynamic Programming problems
    - Complex graph/tree problems
    - Advanced DSA
    Examples: "Longest Increasing Subsequence", "Edit Distance", "Coin Change", "Wildcard Matching"
    MUST include (no placeholders): title, description, constraints, AT LEAST 2 examples (input/output + explanation), AT LEAST 2 test_cases with input AND expected_output, hints

For Technical (15) and Behavioral (20), generate relevant to: {matched_str}

You must return a single JSON object with EXACTLY 3 keys:
1. "technical": 15 questions (5 Easy, 5 Medium, 5 Hard)
2. "behavioral": 20 questions (8 Easy, 7 Medium, 5 Hard)
3. "coding": 2 challenges (1 Easy/Medium from Array/String/Math/DSA/Gaming, 1 Hard Dynamic Programming)

Return ONLY this JSON (no markdown):
{{
    "technical": [{"id": "T1", "question": "...", "skill": "...", "difficulty": "Easy/Medium/Hard", "type": "technical"}, ...],
    "behavioral": [{"id": "B1", "question": "...", "competency": "...", "difficulty": "Easy/Medium/Hard", "type": "behavioral"}, ...],
    "coding": [
        {
            "id": "CODE1",
            "title": "Easy/Medium Competitive Programming Problem",
            "description": "Clear problem statement (Arrays, Strings, Math, DSA, or Gaming logic)",
            "difficulty": "Easy",
            "language": "python",
            "constraints": ["constraint 1", "constraint 2"],
            "examples": [
                {"input": "example input 1", "output": "expected output 1", "explanation": "why this output"},
                {"input": "example input 2", "output": "expected output 2", "explanation": "why this output"}
            ],
            "test_cases": [
                {"input": "test input 1", "expected_output": "expected output 1"},
                {"input": "test input 2", "expected_output": "expected output 2"}
            ],
            "hints": ["hint 1", "hint 2"],
            "type": "coding"
        },
        {
            "id": "CODE2",
            "title": "Hard Dynamic Programming Problem",
            "description": "Complex problem statement",
            "difficulty": "Hard",
            "language": "python",
            "constraints": ["constraint 1", "constraint 2"],
            "examples": [
                {"input": "example input 1", "output": "expected output 1", "explanation": "why this output"},
                {"input": "example input 2", "output": "expected output 2", "explanation": "why this output"}
            ],
            "test_cases": [
                {"input": "test input 1", "expected_output": "expected output 1"},
                {"input": "test input 2", "expected_output": "expected output 2"}
            ],
            "hints": ["hint 1", "hint 2"],
            "type": "coding"
        }
    ]
}}"""

    response = call_groq(prompt, system_prompt, max_tokens=8192)
    
    technical_questions = []
    behavioral_questions = []
    coding_questions = []
    error_msg = None
    
    if response:
        try:
            cleaned = clean_json_response(response)
            data = json.loads(cleaned)
            technical_questions = data.get('technical', [])
            behavioral_questions = data.get('behavioral', [])
            coding_questions = data.get('coding', [])
            print(f"[Groq] Success! Generated {len(technical_questions)} tech, {len(behavioral_questions)} behavioral, {len(coding_questions)} coding questions")
        except Exception as e:
            error_msg = f"JSON parse error: {str(e)}"
            print(f"[Groq] {error_msg}")
    else:
        error_msg = "Groq API timeout or empty response"
    
    all_qs = technical_questions + behavioral_questions + coding_questions
    
    result = {
        'technical': technical_questions,
        'behavioral': behavioral_questions,
        'coding': coding_questions,
        'total_questions': len(all_qs),
        'matched_skills': matched_skills,
        'job_requirements': must_have_skills,
        'generated_at': datetime.now().isoformat(),
        'candidate_id': candidate_id,
        'job_id': job_id
    }
    
    if error_msg or len(all_qs) == 0:
        result['error'] = error_msg or "No questions generated"
    
    return result


def generate_linkedin_post(job_data: dict) -> str:
    """Generate an engaging LinkedIn job post"""
    
    system_prompt = "You are a social media expert creating engaging LinkedIn job posts."
    
    title = job_data.get('title', 'Position')
    location = job_data.get('location', 'Remote')
    description = job_data.get('description', '')[:200]
    skills = job_data.get('requirements', {}).get('must_have', [])[:5]
    application_url = job_data.get('application_url', '')
    
    prompt = f"""Create an engaging LinkedIn job post for:
- Title: {title}
- Location: {location}
- Description: {description}
- Key Skills: {', '.join(skills)}
- Application URL: {application_url}

Make it professional but engaging with emojis. Include relevant hashtags.
Keep it under 500 characters.
Return ONLY the post text, no JSON."""

    response = call_groq(prompt, system_prompt, max_tokens=300)
    
    if response:
        return response.strip()
    
    return f"🚀 We're Hiring: {title}! Apply here: {application_url}"
