"""
AI Evaluator Module - Enhanced Interview Answer Evaluation
Uses Groq AI to evaluate candidate responses with detailed scoring
"""

import os
import json
import requests
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Groq Configuration
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions'
DEFAULT_MODEL = 'llama-3.3-70b-versatile'


def call_groq(prompt: str, system_prompt: str = None, max_tokens: int = 1024) -> Optional[str]:
    """Call Groq API with a prompt and return the response"""
    if not GROQ_API_KEY:
        print('[AI Evaluator] Error: GROQ_API_KEY not set')
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
        "model": DEFAULT_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3  # Lower temperature for more consistent evaluation
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            print(f"[AI Evaluator] Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"[AI Evaluator] Exception: {e}")
        return None


def evaluate_single_answer(question: str, answer: str, question_type: str, 
                          candidate_skills: List[str] = None, job_title: str = None) -> Dict:
    """
    Evaluate a single interview answer using Groq AI
    
    Returns detailed scoring including:
    - Technical accuracy (for technical questions)
    - Clarity & communication
    - Depth of knowledge
    - Practical application
    - Overall score
    """
    
    skills_context = f"Candidate's skills: {', '.join(candidate_skills[:10])}" if candidate_skills else ""
    job_context = f"Position: {job_title}" if job_title else ""
    
    system_prompt = """You are an expert technical interviewer and HR professional evaluating interview responses.
    Provide fair, detailed, and constructive evaluations. Score objectively based on the quality of the answer.
    Always respond with valid JSON only, no markdown or extra text."""
    
    if question_type == 'technical':
        prompt = f"""Evaluate this TECHNICAL interview response:

Question: {question}
Candidate's Answer: {answer}
{skills_context}
{job_context}

Evaluate the answer on these criteria (each out of 100):
1. Technical Accuracy - Is the answer technically correct?
2. Depth of Knowledge - Does it show deep understanding?
3. Practical Application - Are there real-world examples?
4. Clarity - Is the explanation clear and well-organized?
5. Completeness - Does it fully address the question?

Respond with ONLY this JSON (no markdown):
{{
    "technical_accuracy": 0-100,
    "depth_of_knowledge": 0-100,
    "practical_application": 0-100,
    "clarity": 0-100,
    "completeness": 0-100,
    "overall_score": 0-100,
    "strengths": ["strength 1", "strength 2"],
    "areas_to_improve": ["improvement 1", "improvement 2"],
    "feedback": "2-3 sentence constructive feedback"
}}"""
    
    elif question_type == 'behavioral':
        prompt = f"""Evaluate this BEHAVIORAL interview response:

Question: {question}
Candidate's Answer: {answer}
{skills_context}
{job_context}

Evaluate using the STAR method (Situation, Task, Action, Result):
1. Situation Context - Did they set up the scenario well?
2. Task Clarity - Is the challenge/responsibility clear?
3. Action Description - Are specific actions detailed?
4. Result Impact - Are outcomes measurable/meaningful?
5. Communication - Is the story engaging and clear?

Respond with ONLY this JSON (no markdown):
{{
    "situation_context": 0-100,
    "task_clarity": 0-100,
    "action_description": 0-100,
    "result_impact": 0-100,
    "communication": 0-100,
    "overall_score": 0-100,
    "strengths": ["strength 1", "strength 2"],
    "areas_to_improve": ["improvement 1", "improvement 2"],
    "feedback": "2-3 sentence constructive feedback"
}}"""
    
    else:  # coding
        prompt = f"""Evaluate this CODING interview response:

Question: {question}
Candidate's Code/Answer: {answer}
{skills_context}

Evaluate the code on:
1. Correctness - Does it solve the problem?
2. Code Quality - Is it clean, readable, well-structured?
3. Efficiency - Is the time/space complexity optimal?
4. Edge Cases - Are edge cases handled?
5. Best Practices - Does it follow coding best practices?

Respond with ONLY this JSON (no markdown):
{{
    "correctness": 0-100,
    "code_quality": 0-100,
    "efficiency": 0-100,
    "edge_cases": 0-100,
    "best_practices": 0-100,
    "overall_score": 0-100,
    "strengths": ["strength 1", "strength 2"],
    "areas_to_improve": ["improvement 1", "improvement 2"],
    "feedback": "2-3 sentence constructive feedback",
    "suggested_improvements": "Brief code improvement suggestion"
}}"""
    
    response = call_groq(prompt, system_prompt, max_tokens=800)
    
    if response:
        try:
            # Clean response
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            result['evaluated_at'] = datetime.now().isoformat()
            result['question_type'] = question_type
            return result
        except json.JSONDecodeError as e:
            print(f"[AI Evaluator] JSON parse error: {e}")
    
    # Fallback scoring
    answer_length = len(answer) if answer else 0
    base_score = min(70, 30 + (answer_length // 10))
    
    return {
        "overall_score": base_score,
        "technical_accuracy": base_score if question_type == 'technical' else None,
        "communication": base_score,
        "strengths": ["Response provided"],
        "areas_to_improve": ["Could provide more detail"],
        "feedback": "Thank you for your response. Consider providing more specific examples.",
        "fallback": True,
        "evaluated_at": datetime.now().isoformat()
    }


def evaluate_all_responses(responses: List[Dict], candidate_skills: List[str] = None, 
                          job_title: str = None) -> Dict:
    """
    Evaluate all interview responses and provide comprehensive scoring
    
    Args:
        responses: List of {question, answer, type} dictionaries
        candidate_skills: List of candidate's skills from resume
        job_title: Job position being applied for
    
    Returns:
        Comprehensive evaluation with individual and aggregate scores
    """
    
    print(f"[AI Evaluator] Evaluating {len(responses)} responses...")
    
    evaluations = []
    technical_scores = []
    behavioral_scores = []
    coding_scores = []
    
    for i, response in enumerate(responses):
        question = response.get('question', '')
        answer = response.get('answer', '')
        q_type = response.get('type', 'technical')
        
        if not answer or len(answer.strip()) < 10:
            evaluation = {
                "overall_score": 0,
                "feedback": "No response provided",
                "strengths": [],
                "areas_to_improve": ["Response required"],
                "skipped": True
            }
        else:
            evaluation = evaluate_single_answer(
                question=question,
                answer=answer,
                question_type=q_type,
                candidate_skills=candidate_skills,
                job_title=job_title
            )
        
        evaluation['question_id'] = response.get('id', i + 1)
        evaluation['question'] = question[:100] + '...' if len(question) > 100 else question
        evaluations.append(evaluation)
        
        # Collect scores by type
        score = evaluation.get('overall_score', 0)
        if q_type == 'technical':
            technical_scores.append(score)
        elif q_type == 'behavioral':
            behavioral_scores.append(score)
        elif q_type == 'coding':
            coding_scores.append(score)
    
    # Calculate aggregate scores
    def safe_avg(scores):
        return round(sum(scores) / len(scores), 1) if scores else 0
    
    technical_avg = safe_avg(technical_scores)
    behavioral_avg = safe_avg(behavioral_scores)
    coding_avg = safe_avg(coding_scores)
    
    # Weighted overall score (Technical: 40%, Behavioral: 30%, Coding: 30%)
    weights = {
        'technical': 0.4,
        'behavioral': 0.3,
        'coding': 0.3
    }
    
    weighted_total = 0
    weight_sum = 0
    
    if technical_scores:
        weighted_total += technical_avg * weights['technical']
        weight_sum += weights['technical']
    if behavioral_scores:
        weighted_total += behavioral_avg * weights['behavioral']
        weight_sum += weights['behavioral']
    if coding_scores:
        weighted_total += coding_avg * weights['coding']
        weight_sum += weights['coding']
    
    overall_score = round(weighted_total / weight_sum, 1) if weight_sum > 0 else 0
    
    # Generate hiring recommendation
    if overall_score >= 80:
        recommendation = "Strong Hire"
        recommendation_detail = "Candidate demonstrated excellent skills across all areas. Highly recommended for the next round."
    elif overall_score >= 65:
        recommendation = "Hire"
        recommendation_detail = "Candidate shows good potential with solid fundamentals. Recommended to proceed."
    elif overall_score >= 50:
        recommendation = "Maybe"
        recommendation_detail = "Candidate has some strengths but also areas for improvement. Consider additional evaluation."
    else:
        recommendation = "No Hire"
        recommendation_detail = "Candidate's responses did not meet the required standards for this position."
    
    result = {
        "evaluations": evaluations,
        "summary": {
            "total_questions": len(responses),
            "technical_score": technical_avg,
            "behavioral_score": behavioral_avg,
            "coding_score": coding_avg,
            "overall_score": overall_score,
            "questions_by_type": {
                "technical": len(technical_scores),
                "behavioral": len(behavioral_scores),
                "coding": len(coding_scores)
            }
        },
        "recommendation": recommendation,
        "recommendation_detail": recommendation_detail,
        "evaluated_at": datetime.now().isoformat(),
        "scoring_method": "groq_ai_evaluation"
    }
    
    print(f"[AI Evaluator] ✅ Evaluation complete - Overall Score: {overall_score}% - Recommendation: {recommendation}")
    
    return result


def generate_skill_matched_questions(job_requirements: Dict, candidate_skills: List[str], 
                                    job_title: str, candidate_id: str = None) -> Dict:
    """
    Generate interview questions that specifically match candidate's skills with job requirements
    
    This ensures questions are:
    1. Relevant to the candidate's actual skills from resume
    2. Aligned with job requirements
    3. Progressive in difficulty
    4. Unique per candidate (using candidate_id for randomization)
    """
    
    must_have = job_requirements.get('must_have', [])[:7]
    nice_to_have = job_requirements.get('nice_to_have', [])[:3]
    
    # Find matching skills between candidate and job
    candidate_skills_lower = [s.lower().strip() for s in candidate_skills]
    must_have_lower = [s.lower().strip() for s in must_have]
    
    matched_skills = []
    for skill in candidate_skills:
        for req in must_have_lower:
            if skill.lower().strip() in req or req in skill.lower().strip():
                matched_skills.append(skill)
                break
    
    # If no matches, use candidate's top skills
    if not matched_skills:
        matched_skills = candidate_skills[:5]
    
    matched_str = ', '.join(matched_skills[:5])
    all_required = ', '.join(must_have)
    
    print(f"[AI Evaluator] Generating questions for matched skills: {matched_str}")
    
    system_prompt = f"""You are an expert technical interviewer creating personalized interview questions.
    The candidate has these skills: {matched_str}
    The job requires: {all_required}
    
    Generate questions that test the INTERSECTION of candidate skills and job requirements.
    Questions should be specific to the technologies the candidate knows.
    Always respond with valid JSON only."""
    
    prompt = f"""Generate interview questions for a {job_title} position.

CANDIDATE PROFILE:
- Skills from Resume: {', '.join(candidate_skills[:8])}
- Matched with Job Requirements: {matched_str}

JOB REQUIREMENTS:
- Must Have: {all_required}
- Nice to Have: {', '.join(nice_to_have)}

CRITICAL RULES:
1. Generate EXACTLY 15 TECHNICAL questions that test the candidate's listed skills
2. Each technical question MUST relate to one of these skills: {matched_str}
3. Generate EXACTLY 20 BEHAVIORAL questions
4. Generate EXACTLY 2 CODING challenges related to: {matched_str}
5. Vary difficulty: Easy (30%), Medium (40%), Hard (30%)
6. Make questions unique - use candidate_id "{candidate_id}" as seed

Return ONLY this JSON (no markdown):
{{
    "technical": [
        {{"id": "T1", "question": "...", "skill": "specific skill", "difficulty": "easy", "type": "technical", "expected_time_minutes": 2}},
        ... (15 questions total)
    ],
    "behavioral": [
        {{"id": "B1", "question": "...", "competency": "teamwork|leadership|problem_solving", "difficulty": "easy", "type": "behavioral"}},
        ... (20 questions total)
    ],
    "coding": [
        {{
            "id": "C1", 
            "title": "Problem related to {matched_skills[0] if matched_skills else 'programming'}", 
            "description": "...",
            "difficulty": "medium",
            "type": "coding",
            "language": "python",
            "test_cases": [{{"input": "...", "expected_output": "..."}}]
        }},
        {{
            "id": "C2", 
            "title": "Harder problem", 
            "description": "...",
            "difficulty": "hard",
            "type": "coding",
            "language": "python",
            "test_cases": [{{"input": "...", "expected_output": "..."}}]
        }}
    ],
    "matched_skills": {json.dumps(matched_skills[:5])},
    "job_title": "{job_title}"
}}"""
    
    response = call_groq(prompt, system_prompt, max_tokens=4000)
    
    if response:
        try:
            cleaned = response.strip()
            if cleaned.startswith('```'):
                cleaned = cleaned.split('\n', 1)[1]
            if cleaned.endswith('```'):
                cleaned = cleaned.rsplit('```', 1)[0]
            cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            result['generated_at'] = datetime.now().isoformat()
            result['candidate_id'] = candidate_id
            
            tech_count = len(result.get('technical', []))
            behav_count = len(result.get('behavioral', []))
            code_count = len(result.get('coding', []))
            
            print(f"[AI Evaluator] ✅ Generated {tech_count} technical, {behav_count} behavioral, {code_count} coding questions")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"[AI Evaluator] JSON parse error: {e}")
    
    # Return fallback
    return {
        "technical": [],
        "behavioral": [],
        "coding": [],
        "error": "Failed to generate questions",
        "fallback": True
    }


def generate_interview_summary_email(candidate_name: str, job_title: str, 
                                     evaluation: Dict) -> Dict:
    """
    Generate a professional email summarizing the interview results
    """
    
    overall_score = evaluation.get('summary', {}).get('overall_score', 0)
    recommendation = evaluation.get('recommendation', 'Pending')
    
    system_prompt = """You are a professional HR representative writing interview result emails.
    Write warm, professional, and encouraging emails regardless of outcome.
    Always respond with valid JSON only."""
    
    if overall_score >= 65:
        prompt = f"""Write a POSITIVE interview result email for:
- Candidate: {candidate_name}
- Position: {job_title}
- Score: {overall_score}%
- Outcome: Moving to next round

Include:
1. Congratulations on strong performance
2. Specific praise for their answers
3. Next steps in the process
4. Timeline expectations

Respond with JSON: {{"subject": "...", "html_body": "..."}}"""
    else:
        prompt = f"""Write a PROFESSIONAL rejection email for:
- Candidate: {candidate_name}
- Position: {job_title}
- Score: {overall_score}%

Include:
1. Thank them for participating
2. Acknowledge their effort positively
3. Mention keeping resume on file
4. Encourage future applications

Respond with JSON: {{"subject": "...", "html_body": "..."}}"""
    
    response = call_groq(prompt, system_prompt, max_tokens=600)
    
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
    if overall_score >= 65:
        return {
            "subject": f"Great News! Next Steps for {job_title} - GCC Hiring",
            "html_body": f"<p>Dear {candidate_name},</p><p>Congratulations! You've successfully completed the interview with a score of {overall_score}%.</p><p>We'll be in touch soon with next steps.</p>"
        }
    else:
        return {
            "subject": f"Thank You for Interviewing - {job_title} - GCC Hiring",
            "html_body": f"<p>Dear {candidate_name},</p><p>Thank you for completing the interview for {job_title}. We appreciate your time and effort.</p><p>We'll keep your resume on file for future opportunities.</p>"
        }
