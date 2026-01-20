"""
Magical API Configuration
Handles resume parsing and skill matching via Magical AI API
Supports fallback to local processing if API is unavailable
"""

import os
import requests
import json
import re

# Magical API Configuration
MAGICAL_API_KEY = os.environ.get('MAGICAL_API_KEY', 'mag_d3eaf0b6fb7f909794ba772fcd80ea755466839')

# Try multiple API endpoints for flexibility
MAGICAL_API_ENDPOINTS = [
    'https://api.getmagical.com/v1',  # Primary endpoint
    'https://api.magical.dev/v1',     # Alternative endpoint
    'https://magical.ai/api/v1',      # Alternative endpoint
]

MAGICAL_API_BASE_URL = os.environ.get('MAGICAL_API_BASE_URL', MAGICAL_API_ENDPOINTS[0])


def call_magical_api(endpoint: str, payload: dict) -> dict:
    """
    Call Magical API for AI processing
    
    Args:
        endpoint: API endpoint (e.g., 'resume/parse', 'skills/extract')
        payload: Request payload
    
    Returns:
        API response as dictionary
    """
    try:
        headers = {
            'Authorization': f'Bearer {MAGICAL_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        url = f"{MAGICAL_API_BASE_URL}/{endpoint}"
        
        print(f"[Magical AI] Calling endpoint: {endpoint}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"[Magical AI] SUCCESS! Response received")
            return {
                'success': True,
                'data': result,
                'status_code': response.status_code
            }
        else:
            error_msg = response.text
            print(f"[Magical AI] ERROR: {response.status_code} - {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'status_code': response.status_code
            }
    
    except Exception as e:
        error_msg = str(e)
        print(f"[Magical AI] Exception: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }


def parse_resume_with_magical(resume_text: str) -> dict:
    """
    Parse resume using Magical AI API
    
    Args:
        resume_text: Plain text content of resume
    
    Returns:
        Parsed resume data
    """
    payload = {
        'text': resume_text,
        'extract_fields': [
            'name', 'email', 'phone', 'skills', 'experience',
            'education', 'location', 'title'
        ]
    }
    
    response = call_magical_api('resume/parse', payload)
    
    if response.get('success'):
        data = response.get('data', {})
        return {
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'skills': data.get('skills', []),
            'experience_years': data.get('experience', {}).get('years', 0),
            'education': data.get('education'),
            'current_title': data.get('title'),
            'location': data.get('location'),
            'raw_text': resume_text[:500]
        }
    else:
        return {
            'success': False,
            'error': response.get('error')
        }


def match_skills_with_magical(candidate_skills: list, job_requirements: dict) -> dict:
    """
    Match candidate skills with job requirements using Magical AI
    
    Args:
        candidate_skills: List of candidate skills
        job_requirements: Job requirements dict with 'must_have' and 'good_to_have'
    
    Returns:
        Match score and analysis
    """
    must_have = job_requirements.get('must_have', [])
    good_to_have = job_requirements.get('good_to_have', [])
    
    payload = {
        'candidate_skills': candidate_skills,
        'required_skills': must_have,
        'preferred_skills': good_to_have,
        'return_match_score': True,
        'return_missing_skills': True
    }
    
    response = call_magical_api('skills/match', payload)
    
    if response.get('success'):
        data = response.get('data', {})
        return {
            'success': True,
            'match_score': data.get('match_score', 0),
            'match_percentage': data.get('match_percentage', 0),
            'missing_skills': data.get('missing_skills', []),
            'matched_skills': data.get('matched_skills', []),
            'gap_analysis': data.get('gap_analysis', {})
        }
    else:
        # Fallback to simple calculation if API fails
        return calculate_match_score_fallback(candidate_skills, must_have)


def calculate_match_score_fallback(candidate_skills: list, required_skills: list) -> dict:
    """
    Fallback matching when API is unavailable
    """
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    required_skills_lower = [s.lower() for s in required_skills]
    
    matches = len(set(candidate_skills_lower) & set(required_skills_lower))
    total_required = len(required_skills_lower) if required_skills_lower else 1
    
    match_percentage = (matches / total_required) * 100 if total_required > 0 else 0
    missing = list(set(required_skills_lower) - set(candidate_skills_lower))
    
    return {
        'success': True,
        'match_score': round(match_percentage, 2),
        'match_percentage': round(match_percentage, 2),
        'missing_skills': missing,
        'matched_skills': list(set(candidate_skills_lower) & set(required_skills_lower)),
        'fallback': True
    }


def extract_skills_with_magical(text: str) -> dict:
    """
    Extract skills from any text using Magical AI
    
    Args:
        text: Text content to extract skills from
    
    Returns:
        Extracted skills list
    """
    payload = {
        'text': text,
        'return_proficiency': True,
        'return_categories': True
    }
    
    response = call_magical_api('skills/extract', payload)
    
    if response.get('success'):
        data = response.get('data', {})
        return {
            'skills': data.get('skills', []),
            'skill_categories': data.get('categories', {}),
            'proficiency_levels': data.get('proficiency', {})
        }
    else:
        return {
            'skills': [],
            'error': response.get('error')
        }
