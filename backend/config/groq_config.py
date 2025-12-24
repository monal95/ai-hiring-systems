"""
Groq AI Configuration
Handles AI-powered features using Groq API (LLaMA3 / Mixtral)
"""

import os
import json
import requests
from typing import Optional

# Groq Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
DEFAULT_MODEL = 'llama-3.3-70b-versatile'  # Fast and capable model


def call_groq(prompt: str, system_prompt: str = None, model: str = DEFAULT_MODEL, max_tokens: int = 1024) -> Optional[str]:
    """
    Call Groq API with a prompt and return the response
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt for context
        model: The model to use (default: llama-3.3-70b-versatile)
        max_tokens: Maximum tokens in response
    
    Returns:
        The AI response text or None if error
    """
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
    
    try:
        print(f"[Groq] Calling API with model: {model}")
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            result = data['choices'][0]['message']['content']
            print(f"[Groq] Success! Response length: {len(result)} chars")
            return result
        else:
            print(f"[Groq] Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"[Groq] Exception: {e}")
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

    response = call_groq(prompt, system_prompt)
    
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
        "html_body": f"<p>Dear {candidate_name},</p><p>🎉 <strong>Congratulations!</strong> We are pleased to inform you that you have been shortlisted for the <strong>{job_title}</strong> position.</p><p>We will contact you shortly to schedule the next steps.</p><p>Best regards,<br>The Hiring Team</p>"
    }


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
    
    # Fallback
    return f"""🚀 We're Hiring: {title}!

📍 {location}

{description[:150]}...

🔑 Skills: {', '.join(skills[:3])}

👉 Apply: {application_url}

#Hiring #NowHiring #{title.replace(' ', '')} #JobOpening"""
