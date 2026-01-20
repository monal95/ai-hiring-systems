from flask import Flask, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import random
import secrets
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()
from models.resume_parser import ResumeParser
from models.skill_matcher import SkillMatcher
from models.interview_system import (
    interview_generator,
    coding_evaluator,
    interview_session_manager
)
from models.adaptive_interview import adaptive_interview_manager
from models.enhanced_interview import enhanced_interview_manager
from models.ai_recommendations import (
    candidate_scorer, salary_recommender, 
    interview_panel_recommender, assessment_recommender
)
from config.api_integrations import integration_manager
from config.email_config import (
    send_email,
    send_rejection_email as sendgrid_rejection_email,
    send_interview_invitation,
    send_offer_letter,
    send_application_confirmation,
    send_auto_rejection_email,
    send_hr_interview_invitation,
    send_interview_rejection_email
)
from config.groq_config import (
    generate_job_description,
    suggest_skills,
    generate_rejection_email as groq_rejection_email,
    generate_application_confirmation_email,
    generate_shortlisted_email,
    generate_linkedin_post
)
from config.magical_config import extract_skills_with_magical
from config.ai_evaluator import (
    evaluate_single_answer,
    evaluate_all_responses,
    generate_skill_matched_questions,
    generate_interview_summary_email
)
from routes.linkedin_auth import linkedin_bp
from routes.linkedin_share import linkedin_share_bp
from config.devtunnel_config import DevTunnelConfig, get_cors_config
import traceback
import re

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))

# Configure CORS for both local and ngrok/tunnel access
# Use wildcard "*" to allow all origins (simpler for ngrok which changes URLs)
CORS(app, 
     origins="*",
     supports_credentials=True,
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'ngrok-skip-browser-warning'])

# Auto-rejection threshold
AUTO_REJECT_THRESHOLD = 50  # Candidates scoring below 50% are auto-rejected

# Register LinkedIn blueprints
app.register_blueprint(linkedin_bp)
app.register_blueprint(linkedin_share_bp)

# Initialize AI models
print("[APP] Initializing Resume Parser with Magical AI...")
parser = ResumeParser()
print("[APP] Initializing Skill Matcher with Magical AI...")
matcher = SkillMatcher()
print("[APP] Initializing AI Interview System...")

# Mock databases (in real app, use PostgreSQL)
CANDIDATES_FILE = 'data/candidates.json'
JOBS_FILE = 'data/jobs.json'

# Mock Interviewers Database
MOCK_INTERVIEWERS = [
    {
        'id': 'INT001',
        'name': 'Priya Sharma',
        'email': 'priya.sharma@gcc.com',
        'role': 'Senior Software Engineer',
        'expertise': ['Python', 'Django', 'Flask', 'REST APIs', 'PostgreSQL', 'AWS'],
        'experience_years': 8,
        'available': True,
        'rating': 4.8
    },
    {
        'id': 'INT002',
        'name': 'Rahul Verma',
        'email': 'rahul.verma@gcc.com',
        'role': 'Tech Lead',
        'expertise': ['Java', 'Spring Boot', 'Microservices', 'Kubernetes', 'Docker', 'MongoDB'],
        'experience_years': 10,
        'available': True,
        'rating': 4.9
    },
    {
        'id': 'INT003',
        'name': 'Ananya Patel',
        'email': 'ananya.patel@gcc.com',
        'role': 'Full Stack Developer',
        'expertise': ['React', 'Node.js', 'TypeScript', 'JavaScript', 'MongoDB', 'GraphQL'],
        'experience_years': 6,
        'available': True,
        'rating': 4.7
    },
    {
        'id': 'INT004',
        'name': 'Vikram Singh',
        'email': 'vikram.singh@gcc.com',
        'role': 'DevOps Engineer',
        'expertise': ['AWS', 'Azure', 'CI/CD', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins'],
        'experience_years': 7,
        'available': True,
        'rating': 4.6
    },
    {
        'id': 'INT005',
        'name': 'Sneha Reddy',
        'email': 'sneha.reddy@gcc.com',
        'role': 'Data Scientist',
        'expertise': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'SQL', 'Data Analysis'],
        'experience_years': 5,
        'available': True,
        'rating': 4.8
    },
    {
        'id': 'INT006',
        'name': 'Arjun Nair',
        'email': 'arjun.nair@gcc.com',
        'role': 'Backend Developer',
        'expertise': ['Python', 'Go', 'gRPC', 'Redis', 'Kafka', 'PostgreSQL'],
        'experience_years': 6,
        'available': True,
        'rating': 4.5
    },
    {
        'id': 'INT007',
        'name': 'Meera Iyer',
        'email': 'meera.iyer@gcc.com',
        'role': 'Frontend Developer',
        'expertise': ['React', 'Vue.js', 'Angular', 'CSS', 'Tailwind', 'JavaScript'],
        'experience_years': 5,
        'available': True,
        'rating': 4.7
    },
    {
        'id': 'INT008',
        'name': 'Karthik Menon',
        'email': 'karthik.menon@gcc.com',
        'role': 'Mobile Developer',
        'expertise': ['React Native', 'Flutter', 'iOS', 'Android', 'Swift', 'Kotlin'],
        'experience_years': 6,
        'available': True,
        'rating': 4.6
    }
]

def match_interviewer(candidate_skills: list, job_title: str) -> dict:
    """Match the best interviewer based on candidate skills and job title"""
    best_match = None
    best_score = 0
    
    candidate_skills_lower = [s.lower() for s in candidate_skills]
    job_title_lower = job_title.lower()
    
    for interviewer in MOCK_INTERVIEWERS:
        if not interviewer['available']:
            continue
            
        expertise_lower = [e.lower() for e in interviewer['expertise']]
        
        # Calculate skill match score
        matching_skills = sum(1 for skill in candidate_skills_lower 
                            if any(skill in exp or exp in skill for exp in expertise_lower))
        
        # Bonus for role matching
        role_bonus = 0
        if 'python' in job_title_lower and 'python' in str(expertise_lower):
            role_bonus = 2
        if 'react' in job_title_lower and 'react' in str(expertise_lower):
            role_bonus = 2
        if 'java' in job_title_lower and 'java' in str(expertise_lower):
            role_bonus = 2
        if 'data' in job_title_lower and 'data' in interviewer['role'].lower():
            role_bonus = 3
        if 'devops' in job_title_lower and 'devops' in interviewer['role'].lower():
            role_bonus = 3
            
        total_score = matching_skills + role_bonus + (interviewer['rating'] * 0.5)
        
        if total_score > best_score:
            best_score = total_score
            best_match = interviewer
    
    return best_match or MOCK_INTERVIEWERS[0]  # Default to first interviewer

# Ensure data directory exists
os.makedirs('data/resumes', exist_ok=True)

print("[APP] GCC Hiring System initialized")
print("[APP] Resume Parsing: Magical AI")
print("[APP] Skill Matching: Magical AI")
print("[APP] Interview System: AI-Powered")

# Load or initialize data
def load_json(filepath, default=[]):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Handle both list and dict formats
            if isinstance(data, dict):
                # Extract list from candidates.json or jobs.json structure
                if 'candidates' in data:
                    return data['candidates']
                elif 'jobs' in data:
                    return data['jobs']
            return data if isinstance(data, list) else default
    return default

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        # Wrap in appropriate object key
        if 'candidates' in filepath:
            json.dump({'candidates': data}, f, indent=2)
        elif 'jobs' in filepath:
            json.dump({'jobs': data}, f, indent=2)
        else:
            json.dump(data, f, indent=2)

def generate_job_post(job_data):
    """Generate AI job posting message for platforms"""
    title = job_data.get('title', 'Position')
    location = job_data.get('location', 'Remote')
    description = job_data.get('description', 'Great opportunity')
    must_have = job_data.get('requirements', {}).get('must_have', [])
    nice_to_have = job_data.get('requirements', {}).get('good_to_have', [])
    openings = job_data.get('openings', 5)
    
    message = f"""
🚀 Now Hiring: {title}

📍 Location: {location}
🎯 Openings: {openings}

{description}

✅ Must-Have Skills:
"""
    
    for skill in must_have[:5]:
        message += f"  • {skill}\n"
    
    if nice_to_have:
        message += "\n💡 Nice-to-Have Skills:\n"
        for skill in nice_to_have[:3]:
            message += f"  • {skill}\n"
    
    message += "\n🔗 Apply Now via the link below!\n"
    message += "#Hiring #JobOpening #Careers"
    
    return message

candidates = load_json(CANDIDATES_FILE, default=[])
jobs = load_json(JOBS_FILE, default=[])

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    # Calculate stats
    total_jobs = len(jobs)
    total_applications = len(candidates)
    
    # Count by priority
    high_priority = sum(1 for c in candidates if c.get('priority') == 'High')
    medium_priority = sum(1 for c in candidates if c.get('priority') == 'Medium')
    low_priority = sum(1 for c in candidates if c.get('priority') == 'Low')
    
    # Get recent applications (last 5)
    recent_apps = sorted(
        candidates, 
        key=lambda x: x.get('applied_at', ''),
        reverse=True
    )[:5]
    
    stats = {
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'recent_applications': [
            {
                'id': app['id'],
                'name': app['name'],
                'skills': app['skills'][:3] if app.get('skills') else [],
                'match_score': app.get('match_score', 0),
                'priority': app.get('priority', 'Medium'),
                'status': app.get('status', 'Applied')
            }
            for app in recent_apps
        ]
    }
    
    return jsonify(stats), 200


# ======================== GROQ AI ENDPOINTS ========================

@app.route('/api/ai/generate-job-description', methods=['POST'])
def ai_generate_job_description():
    """Generate job description using Groq AI"""
    data = request.json
    job_title = data.get('job_title', '')
    department = data.get('department', '')
    location = data.get('location', '')
    
    if not job_title:
        return jsonify({'error': 'Job title is required'}), 400
    
    result = generate_job_description(job_title, department, location)
    return jsonify(result), 200


@app.route('/api/ai/suggest-skills', methods=['POST'])
def ai_suggest_skills():
    """Suggest skills for a job title using Groq AI"""
    data = request.json
    job_title = data.get('job_title', '')
    current_skills = data.get('current_skills', [])
    
    if not job_title:
        return jsonify({'error': 'Job title is required'}), 400
    
    skills = suggest_skills(job_title, current_skills)
    return jsonify({'skills': skills}), 200


@app.route('/api/ai/generate-linkedin-post', methods=['POST'])
def ai_generate_linkedin_post():
    """Generate LinkedIn post using Groq AI"""
    job_data = request.json
    post_content = generate_linkedin_post(job_data)
    return jsonify({'post_content': post_content}), 200


@app.route('/api/jobs', methods=['GET', 'POST'])
def handle_jobs():
    """Create and list jobs"""
    if request.method == 'POST':
        job_data = request.json
        job_data['id'] = f"JOB{len(jobs) + 1}"
        job_data['created_at'] = datetime.now().isoformat()
        job_data['status'] = 'active'
        job_data['applications'] = 0
        job_data['openings'] = job_data.get('openings', 5)  # Number of positions to fill
        job_data['hired_count'] = 0  # Track hired candidates
        
        # Initialize multi-platform publishing data
        platforms = job_data.get('selected_platforms', [
            'company_portal', 'linkedin', 'indeed', 'naukri', 'internal_referral'
        ])
        
        # Generate AI job description for posting
        ai_job_message = generate_job_post(job_data)
        job_data['ai_generated_message'] = ai_job_message
        
        job_data['platforms'] = {}
        for platform in platforms:
            # Auto-post to all platforms
            post_result = integration_manager.post_job_to_platform(platform, {
                'title': job_data.get('title'),
                'description': ai_job_message,
                'location': job_data.get('location'),
                'requirements': job_data.get('requirements', {}),
                'job_id': job_data['id']
            })
            
            job_data['platforms'][platform] = {
                'status': 'published',
                'published_at': datetime.now().isoformat(),
                'views': 0,
                'clicks': 0,
                'applications': 0,
                'ignored': 0,
                'url': f"https://{platform}.com/jobs/{job_data['id']}",
                'post_id': post_result.get('post_id', f'{platform}_{job_data["id"]}')
            }
        
        jobs.append(job_data)
        save_json(JOBS_FILE, jobs)
        
        return jsonify(job_data), 201
    
    return jsonify(jobs), 200

@app.route('/api/jobs/<job_id>', methods=['GET', 'DELETE', 'PUT'])
def get_job(job_id):
    """Get specific job details, remove job, or update job status"""
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if request.method == 'DELETE':
        # Remove job from all platforms
        platforms = job.get('platforms', {})
        
        for platform, details in platforms.items():
            post_id = details.get('post_id')
            integration_manager.delete_job_post(platform, post_id)
        
        # Remove from database
        jobs.remove(job)
        save_json(JOBS_FILE, jobs)
        
        return jsonify({
            'success': True,
            'message': 'Job removed from dashboard and all platforms',
            'removed_from_platforms': list(platforms.keys())
        }), 200
    
    if request.method == 'PUT':
        # Update job status (e.g., mark as filled)
        update_data = request.json
        if 'hired_count' in update_data:
            job['hired_count'] = update_data['hired_count']
        if 'status' in update_data:
            job['status'] = update_data['status']
        
        # Check if job slots are filled
        if job['hired_count'] >= job.get('openings', 5):
            job['status'] = 'filled'
        
        save_json(JOBS_FILE, jobs)
        return jsonify(job), 200
    
    return jsonify(job), 200

@app.route('/api/jobs/<job_id>/analytics', methods=['GET'])
def get_job_analytics(job_id):
    """Get job platform analytics"""
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Calculate platform stats
    platforms = job.get('platforms', {})
    total_views = sum(p.get('views', 0) for p in platforms.values())
    total_applications = sum(p.get('applications', 0) for p in platforms.values())
    total_ignored = sum(p.get('ignored', 0) for p in platforms.values())
    
    analytics = {
        'job_id': job_id,
        'job_title': job.get('title'),
        'created_at': job.get('created_at'),
        'platforms': platforms,
        'summary': {
            'total_views': total_views,
            'total_applications': total_applications,
            'total_ignored': total_ignored,
            'conversion_rate': round((total_applications / total_views * 100) if total_views > 0 else 0, 2)
        }
    }
    
    return jsonify(analytics), 200

@app.route('/api/jobs/<job_id>/platform-stats', methods=['POST'])
def update_platform_stats(job_id):
    """Update platform statistics (views, clicks, applications, ignored)"""
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    data = request.get_json()
    platform = data.get('platform')
    stat_type = data.get('type')  # 'view', 'click', 'application', 'ignored'
    
    if platform not in job.get('platforms', {}):
        return jsonify({'error': 'Platform not found'}), 404
    
    # Update the stat
    if stat_type == 'view':
        job['platforms'][platform]['views'] += 1
    elif stat_type == 'click':
        job['platforms'][platform]['clicks'] += 1
    elif stat_type == 'application':
        job['platforms'][platform]['applications'] += 1
    elif stat_type == 'ignored':
        job['platforms'][platform]['ignored'] += 1
    
    # Save updated data
    save_json(JOBS_FILE, jobs)
    
    return jsonify({'success': True, 'platform': platform, 'stat_type': stat_type}), 200

@app.route('/api/apply', methods=['GET', 'POST'])
def apply_job():
    """Get all candidates or apply to a job with resume"""
    if request.method == 'GET':
        return jsonify(candidates), 200
    
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume uploaded'}), 400
    
    resume = request.files['resume']
    job_id = request.form.get('job_id')
    
    # Save resume
    resume_filename = f"{datetime.now().timestamp()}_{resume.filename}"
    resume_path = os.path.join('data/resumes', resume_filename)
    resume.save(resume_path)
    
    # Parse resume
    parsed_data = parser.parse_resume(resume_path)
    
    if not parsed_data:
        return jsonify({'error': 'Failed to parse resume'}), 400
    
    # Find job and calculate match
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    match_score = matcher.calculate_match_score(
        parsed_data['skills'], 
        job.get('requirements', {})
    )
    
    missing_skills = matcher.get_missing_skills(
        parsed_data['skills'],
        job.get('requirements', {})
    )
    
    category = matcher.categorize_candidate(match_score)
    
    # Create candidate record
    candidate = {
        'id': f"CAND{len(candidates) + 1}",
        'job_id': job_id,
        'name': parsed_data['name'] or request.form.get('name', 'Unknown'),
        'email': parsed_data['email'] or request.form.get('email'),
        'phone': parsed_data['phone'] or request.form.get('phone'),
        'skills': parsed_data['skills'],
        'experience_years': parsed_data['experience_years'],
        'match_score': match_score,
        'missing_skills': missing_skills,
        'priority': category['priority'],
        'recommended_action': category['action'],
        'status': 'Applied',
        'applied_at': datetime.now().isoformat(),
        'resume_path': resume_path
    }
    
    candidates.append(candidate)
    save_json(CANDIDATES_FILE, candidates)
    
    # Update job application count
    job['applications'] = job.get('applications', 0) + 1
    save_json(JOBS_FILE, jobs)
    
    # Send immediate "Thank you for registering" confirmation email
    confirmation_result = send_application_confirmation(
        candidate_name=candidate['name'],
        candidate_email=candidate['email'],
        job_title=job.get('title', 'the position')
    )
    
    print(f"[Application] {candidate['name']} applied for {job.get('title')} - Thank you email sent: {confirmation_result.get('success')}")
    
    # Check if ATS score is below 50% - send automatic rejection email
    rejection_sent = False
    if match_score < 50:
        rejection_result = send_auto_rejection_email(
            candidate_name=candidate['name'],
            candidate_email=candidate['email'],
            job_title=job.get('title', 'the position'),
            match_score=match_score
        )
        rejection_sent = rejection_result.get('success', False)
        
        # Update candidate status to Rejected
        candidate['status'] = 'Rejected'
        candidate['rejection_reason'] = f'ATS score below threshold ({match_score}%)'
        save_json(CANDIDATES_FILE, candidates)
        
        print(f"[Auto-Rejection] {candidate['name']} rejected (ATS Score: {match_score}%) - Rejection email sent: {rejection_sent}")
    
    return jsonify({
        'message': 'Application submitted successfully',
        'candidate': candidate,
        'email_sent': confirmation_result.get('success', False),
        'auto_rejected': match_score < 50,
        'rejection_email_sent': rejection_sent
    }), 201

@app.route('/api/applications/public', methods=['POST'])
def public_apply():
    """Public application endpoint for job application form"""
    
    # Get form data
    job_id = request.form.get('jobId')
    full_name = request.form.get('fullName')
    email = request.form.get('email')
    phone = request.form.get('phone')
    current_location = request.form.get('currentLocation')
    total_experience = request.form.get('totalExperience')
    expected_salary = request.form.get('expectedSalary')
    notice_period = request.form.get('noticePeriod')
    current_employer = request.form.get('currentEmployer', '')
    current_designation = request.form.get('currentDesignation', '')
    work_experience = request.form.get('workExperience', '')
    education = request.form.get('education', '')
    linkedin_profile = request.form.get('linkedinProfile', '')
    key_skills = request.form.get('keySkills', '')
    
    # Find job
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Handle resume upload
    resume_path = None
    parsed_skills = []
    
    if 'resume' in request.files:
        resume = request.files['resume']
        if resume.filename:
            resume_filename = f"{datetime.now().timestamp()}_{resume.filename}"
            resume_path = os.path.join('data/resumes', resume_filename)
            resume.save(resume_path)
            
            # Parse resume for skills
            try:
                parsed_data = parser.parse_resume(resume_path)
                if parsed_data and parsed_data.get('skills'):
                    parsed_skills = parsed_data['skills']
            except:
                pass
    
    # Combine parsed skills with manually entered skills
    manual_skills = [s.strip() for s in key_skills.split(',') if s.strip()]
    all_skills = list(set(parsed_skills + manual_skills))
    
    # Calculate match score
    match_score = matcher.calculate_match_score(
        all_skills, 
        job.get('requirements', {})
    ) if all_skills else 50
    
    missing_skills = matcher.get_missing_skills(
        all_skills,
        job.get('requirements', {})
    ) if all_skills else []
    
    category = matcher.categorize_candidate(match_score)
    
    # Create candidate record
    candidate = {
        'id': f"CAND{len(candidates) + 1}",
        'job_id': job_id,
        'name': full_name,
        'email': email,
        'phone': phone,
        'current_location': current_location,
        'total_experience': total_experience,
        'expected_salary': expected_salary,
        'notice_period': notice_period,
        'current_employer': current_employer,
        'current_designation': current_designation,
        'work_experience': work_experience,
        'education': education,
        'linkedin_profile': linkedin_profile,
        'skills': all_skills,
        'experience_years': int(''.join(filter(str.isdigit, total_experience.split()[0]))) if total_experience else 0,
        'match_score': match_score,
        'missing_skills': missing_skills,
        'priority': category['priority'],
        'recommended_action': category['action'],
        'status': 'Applied',
        'applied_at': datetime.now().isoformat(),
        'resume_path': resume_path,
        'source': 'public_application_form'
    }
    
    candidates.append(candidate)
    save_json(CANDIDATES_FILE, candidates)
    
    # Update job application count
    job['applications'] = job.get('applications', 0) + 1
    save_json(JOBS_FILE, jobs)
    
    # Send immediate "Thank you for registering" confirmation email
    confirmation_result = send_application_confirmation(
        candidate_name=full_name,
        candidate_email=email,
        job_title=job.get('title', 'the position')
    )
    
    print(f"[Application] {full_name} applied for {job.get('title')} - Thank you email sent: {confirmation_result.get('success')}")
    
    # Check if ATS score is below 50% - send automatic rejection email
    rejection_sent = False
    interview_generated = False
    interview_link = None
    email_result = {'success': False}
    
    if match_score < 50:
        # AUTO-REJECTION for candidates scoring below 50%
        print(f"\n[Auto-Rejection] Candidate {full_name} scored {match_score}% - Below threshold")
        
        rejection_result = send_auto_rejection_email(
            candidate_name=full_name,
            candidate_email=email,
            job_title=job.get('title', 'the position'),
            match_score=match_score
        )
        rejection_sent = rejection_result.get('success', False)
        
        # Update candidate status to Rejected
        candidate['status'] = 'Rejected'
        candidate['rejection_reason'] = f'ATS score below threshold ({match_score}%)'
        save_json(CANDIDATES_FILE, candidates)
        
        print(f"[Auto-Rejection] {full_name} rejected (ATS Score: {match_score}%) - Rejection email sent: {rejection_sent}")
    
    else:
        # ELIGIBLE FOR INTERVIEW - Score >= 50%
        print(f"\n{'='*60}")
        print(f"[Interview Generation] ✅ ELIGIBLE CANDIDATE DETECTED")
        print(f"[Interview Generation] Name: {full_name}")
        print(f"[Interview Generation] Email: {email}")
        print(f"[Interview Generation] Score: {match_score}%")
        print(f"{'='*60}")
        
        try:
            # Step 1: Generate interview questions using Groq AI
            print(f"[Interview Generation] Step 1: Generating interview questions with AI...")
            print(f"[Interview Generation] Job requirements: {job.get('requirements', {})}")
            print(f"[Interview Generation] Candidate skills: {candidate.get('skills', [])}")
            
            interview_questions = interview_generator.generate_interview_questions(
                job.get('requirements', {}),
                candidate.get('skills', []),
                candidate_id=candidate['id'],
                job_id=job_id,
                job_title=job.get('title')
            )
            
            # Check if AI generation succeeded
            has_questions = (
                len(interview_questions.get('technical', [])) > 0 or
                len(interview_questions.get('behavioral', [])) > 0 or
                len(interview_questions.get('coding', [])) > 0
            )
            
            if not has_questions or 'error' in interview_questions:
                print(f"[Interview Generation] ⚠️ AI generation failed, using fallback questions")
                # Use fallback questions
                interview_questions = _generate_fallback_interview_questions(job.get('title', 'Software Engineer'))
            
            print(f"[Interview Generation] Questions ready:")
            print(f"  - Technical: {len(interview_questions.get('technical', []))} questions")
            print(f"  - Behavioral: {len(interview_questions.get('behavioral', []))} questions")
            print(f"  - Coding: {len(interview_questions.get('coding', []))} questions")
            
            # Step 2: Create interview session with the questions
            print(f"[Interview Generation] Step 2: Creating interview session...")
            session_info = interview_session_manager.create_interview_session(
                candidate_id=candidate['id'],
                candidate_name=full_name,
                job_id=job_id,
                interview_questions=interview_questions
            )
            
            interview_link = session_info['interview_link']
            print(f"[Interview Generation] ✅ Session created: {session_info['session_id']}")
            print(f"[Interview Generation] Interview link: {interview_link}")
            
            # Step 3: Update candidate record
            candidate['interview_round_1'] = {
                'status': 'generated',
                'session_id': session_info['session_id'],
                'interview_link': interview_link,
                'generated_at': datetime.now().isoformat(),
                'expires_at': session_info['expires_at'],
                'duration_minutes': session_info.get('interview_duration_minutes', 45),
                'questions_count': {
                    'technical': len(interview_questions.get('technical', [])),
                    'behavioral': len(interview_questions.get('behavioral', [])),
                    'coding': len(interview_questions.get('coding', []))
                }
            }
            candidate['status'] = 'Interview Pending'
            save_json(CANDIDATES_FILE, candidates)
            
            # Step 4: Send interview email with link
            print(f"[Interview Email] Step 4: Sending interview invitation to {email}...")
            
            tech_count = len(interview_questions.get('technical', []))
            behavioral_count = len(interview_questions.get('behavioral', []))
            coding_count = len(interview_questions.get('coding', []))
            duration = session_info.get('interview_duration_minutes', 45)
            expires_at = session_info.get('expires_at', '')[:10] if session_info.get('expires_at') else '7 days'
            
            email_result = send_email(
                to_email=email,
                subject=f"🎯 Your Interview is Ready - {job.get('title')} at GCC",
                html_content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f5f5f5; }}
                        .email-container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                        .header p {{ margin: 0; opacity: 0.9; font-size: 16px; }}
                        .content {{ padding: 35px 30px; }}
                        .score-badge {{ display: inline-block; background: linear-gradient(135deg, #10b981, #34d399); color: white; padding: 10px 24px; border-radius: 25px; font-weight: 700; font-size: 18px; margin: 15px 0; }}
                        .round-card {{ background: #f8fafc; border-radius: 10px; padding: 20px; margin: 15px 0; border-left: 4px solid #667eea; }}
                        .round-title {{ font-weight: 700; color: #667eea; font-size: 16px; margin-bottom: 8px; }}
                        .round-info {{ color: #64748b; font-size: 14px; }}
                        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; padding: 16px 40px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 16px; margin: 25px 0; transition: transform 0.2s; }}
                        .cta-button:hover {{ transform: translateY(-2px); }}
                        .info-box {{ background: #fef3c7; border: 1px solid #fbbf24; border-radius: 8px; padding: 15px; margin: 20px 0; }}
                        .info-box strong {{ color: #b45309; }}
                        .footer {{ background: #f8fafc; padding: 25px 30px; text-align: center; color: #64748b; font-size: 13px; border-top: 1px solid #e2e8f0; }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="header">
                            <h1>🎯 Your Interview is Ready!</h1>
                            <p>Next Step in Your Journey with GCC</p>
                        </div>
                        <div class="content">
                            <p>Dear <strong>{full_name}</strong>,</p>
                            
                            <p>Congratulations! 🎉 Your resume has been evaluated by our AI-powered system, and we're thrilled to invite you to the next stage of our hiring process for the <strong>{job.get('title')}</strong> position!</p>
                            
                            <div style="text-align: center;">
                                <span class="score-badge">✅ ATS Score: {match_score}%</span>
                            </div>
                            
                            <h3 style="color: #1e293b; margin-top: 30px;">📋 Your Interview Includes:</h3>
                            
                            <div class="round-card">
                                <div class="round-title">🔧 Round 1: Technical Assessment</div>
                                <div class="round-info">{tech_count} technical questions about your skills and experience</div>
                            </div>
                            
                            <div class="round-card">
                                <div class="round-title">💻 Round 2: Coding Challenge</div>
                                <div class="round-info">{coding_count} coding problem(s) with real-time evaluation</div>
                            </div>
                            
                            <div class="round-card">
                                <div class="round-title">🗣️ Round 3: Behavioral Assessment</div>
                                <div class="round-info">{behavioral_count} behavioral questions to understand your approach</div>
                            </div>
                            
                            <div class="info-box">
                                <strong>⏱️ Estimated Duration:</strong> {duration} minutes<br>
                                <strong>📅 Valid Until:</strong> {expires_at}<br>
                                <strong>💡 Tip:</strong> Ensure a stable internet connection and quiet environment
                            </div>
                            
                            <div style="text-align: center;">
                                <a href="{interview_link}" class="cta-button">Start Your Interview Now →</a>
                            </div>
                            
                            <p style="color: #64748b; font-size: 14px; margin-top: 25px;">
                                <strong>Can't click the button?</strong> Copy and paste this link in your browser:<br>
                                <span style="color: #667eea; word-break: break-all;">{interview_link}</span>
                            </p>
                        </div>
                        <div class="footer">
                            <p>Best of luck! We're excited to learn more about you.</p>
                            <p>© GCC Hiring System | AI-Powered Recruitment</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            )
            
            interview_generated = email_result.get('success', False)
            
            if interview_generated:
                print(f"[Interview Email] ✅ SUCCESS - Interview email sent to {full_name}")
                print(f"[Interview Email] Email status: {email_result}")
            else:
                print(f"[Interview Email] ❌ FAILED - Could not send email to {full_name}")
                print(f"[Interview Email] Error: {email_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"[Interview Error] ❌ EXCEPTION during interview generation:")
            print(f"[Interview Error] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            interview_generated = False
            interview_link = None
            
            # Still mark candidate as eligible even if email fails
            candidate['status'] = 'Eligible for Interview'
            candidate['interview_error'] = str(e)
            save_json(CANDIDATES_FILE, candidates)
    
    print(f"\n{'='*60}")
    print(f"[Application Complete] {full_name}")
    print(f"  - Score: {match_score}%")
    print(f"  - Status: {'Rejected' if match_score < 50 else 'Interview Pending'}")
    print(f"  - Interview Email Sent: {interview_generated}")
    print(f"  - Interview Link: {interview_link}")
    print(f"{'='*60}\n")
    
    return jsonify({
        'message': 'Application submitted successfully',
        'candidate_id': candidate['id'],
        'email_sent': confirmation_result.get('success', False),
        'auto_rejected': match_score < 50,
        'rejection_email_sent': rejection_sent,
        'interview_generated': interview_generated,
        'interview_link': interview_link
    }), 201


def _generate_fallback_interview_questions(job_title: str) -> dict:
    """Generate fallback interview questions when AI generation fails"""
    return {
        'technical': [
            {'id': 'T1', 'question': f'Tell us about your experience relevant to the {job_title} role.', 'difficulty': 'easy', 'type': 'technical', 'skill': 'experience'},
            {'id': 'T2', 'question': 'Describe a complex technical problem you solved and your approach.', 'difficulty': 'medium', 'type': 'technical', 'skill': 'problem_solving'},
            {'id': 'T3', 'question': 'What technologies and tools are you most proficient with?', 'difficulty': 'easy', 'type': 'technical', 'skill': 'tools'},
            {'id': 'T4', 'question': 'How do you approach debugging and troubleshooting issues?', 'difficulty': 'medium', 'type': 'technical', 'skill': 'debugging'},
            {'id': 'T5', 'question': 'Explain a system or application you have designed or architected.', 'difficulty': 'hard', 'type': 'technical', 'skill': 'architecture'},
            {'id': 'T6', 'question': 'How do you ensure code quality in your projects?', 'difficulty': 'medium', 'type': 'technical', 'skill': 'quality'},
            {'id': 'T7', 'question': 'Describe your experience with version control and CI/CD.', 'difficulty': 'easy', 'type': 'technical', 'skill': 'devops'},
            {'id': 'T8', 'question': 'How do you handle performance optimization?', 'difficulty': 'medium', 'type': 'technical', 'skill': 'performance'},
            {'id': 'T9', 'question': 'What is your approach to learning new technologies?', 'difficulty': 'easy', 'type': 'technical', 'skill': 'learning'},
            {'id': 'T10', 'question': 'Describe your experience with database design and management.', 'difficulty': 'medium', 'type': 'technical', 'skill': 'database'},
            {'id': 'T11', 'question': 'How do you approach API design and integration?', 'difficulty': 'medium', 'type': 'technical', 'skill': 'api'},
            {'id': 'T12', 'question': 'Explain your experience with testing and test automation.', 'difficulty': 'medium', 'type': 'technical', 'skill': 'testing'},
            {'id': 'T13', 'question': 'How do you handle security considerations in your code?', 'difficulty': 'hard', 'type': 'technical', 'skill': 'security'},
            {'id': 'T14', 'question': 'Describe a time you had to scale an application.', 'difficulty': 'hard', 'type': 'technical', 'skill': 'scalability'},
            {'id': 'T15', 'question': 'What best practices do you follow in software development?', 'difficulty': 'medium', 'type': 'technical', 'skill': 'best_practices'},
        ],
        'behavioral': [
            {'id': 'B1', 'question': 'Tell us about a time you worked effectively in a team.', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'teamwork'},
            {'id': 'B2', 'question': 'Describe a situation where you had to meet a tight deadline.', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'time_management'},
            {'id': 'B3', 'question': 'How do you handle constructive criticism?', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'feedback'},
            {'id': 'B4', 'question': 'Tell us about a project failure and what you learned.', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'resilience'},
            {'id': 'B5', 'question': 'How do you prioritize tasks when everything seems urgent?', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'prioritization'},
            {'id': 'B6', 'question': 'Describe a time you took initiative without being asked.', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'initiative'},
            {'id': 'B7', 'question': 'How do you handle conflicts with colleagues?', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'conflict_resolution'},
            {'id': 'B8', 'question': 'Tell us about a time you mentored or helped a team member.', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'leadership'},
            {'id': 'B9', 'question': 'How do you stay motivated during repetitive tasks?', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'motivation'},
            {'id': 'B10', 'question': 'Describe a situation where you had to adapt to change quickly.', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'adaptability'},
            {'id': 'B11', 'question': 'How do you communicate complex ideas to non-technical stakeholders?', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'communication'},
            {'id': 'B12', 'question': 'Tell us about your greatest professional achievement.', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'achievement'},
            {'id': 'B13', 'question': 'How do you handle working with difficult team members?', 'difficulty': 'hard', 'type': 'behavioral', 'competency': 'interpersonal'},
            {'id': 'B14', 'question': 'Describe a time you had to make a difficult decision.', 'difficulty': 'hard', 'type': 'behavioral', 'competency': 'decision_making'},
            {'id': 'B15', 'question': 'How do you balance quality with speed?', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'balance'},
            {'id': 'B16', 'question': 'Tell us about a time you went above and beyond for a project.', 'difficulty': 'medium', 'type': 'behavioral', 'competency': 'dedication'},
            {'id': 'B17', 'question': 'How do you handle uncertainty and ambiguity in projects?', 'difficulty': 'hard', 'type': 'behavioral', 'competency': 'uncertainty'},
            {'id': 'B18', 'question': 'Describe your approach to work-life balance.', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'balance'},
            {'id': 'B19', 'question': 'Tell us about a time you disagreed with a decision but still supported it.', 'difficulty': 'hard', 'type': 'behavioral', 'competency': 'professionalism'},
            {'id': 'B20', 'question': 'Where do you see yourself in 5 years?', 'difficulty': 'easy', 'type': 'behavioral', 'competency': 'vision'},
        ],
        'coding': [
            {
                'id': 'CODE1',
                'title': 'Two Sum',
                'description': 'Given an array of integers nums and an integer target, return indices of the two numbers that add up to target. You may assume each input has exactly one solution.',
                'difficulty': 'medium',
                'type': 'coding',
                'language': 'python',
                'constraints': ['2 <= nums.length <= 10^4', '-10^9 <= nums[i] <= 10^9', 'Only one valid answer exists'],
                'examples': [
                    {'input': 'nums = [2, 7, 11, 15], target = 9', 'output': '[0, 1]', 'explanation': 'nums[0] + nums[1] = 2 + 7 = 9'},
                    {'input': 'nums = [3, 2, 4], target = 6', 'output': '[1, 2]', 'explanation': 'nums[1] + nums[2] = 2 + 4 = 6'}
                ],
                'test_cases': [
                    {'input': '[2, 7, 11, 15], 9', 'expected_output': '[0, 1]'},
                    {'input': '[3, 2, 4], 6', 'expected_output': '[1, 2]'},
                    {'input': '[3, 3], 6', 'expected_output': '[0, 1]'}
                ],
                'hints': ['Use a hash map to store seen values', 'For each element, check if target - element exists']
            },
            {
                'id': 'CODE2',
                'title': 'Longest Increasing Subsequence',
                'description': 'Given an integer array nums, return the length of the longest strictly increasing subsequence.',
                'difficulty': 'hard',
                'type': 'coding',
                'language': 'python',
                'constraints': ['1 <= nums.length <= 2500', '-10^4 <= nums[i] <= 10^4'],
                'examples': [
                    {'input': 'nums = [10, 9, 2, 5, 3, 7, 101, 18]', 'output': '4', 'explanation': 'The LIS is [2, 3, 7, 101], length = 4'},
                    {'input': 'nums = [0, 1, 0, 3, 2, 3]', 'output': '4', 'explanation': 'The LIS is [0, 1, 2, 3], length = 4'}
                ],
                'test_cases': [
                    {'input': '[10, 9, 2, 5, 3, 7, 101, 18]', 'expected_output': '4'},
                    {'input': '[0, 1, 0, 3, 2, 3]', 'expected_output': '4'},
                    {'input': '[7, 7, 7, 7, 7]', 'expected_output': '1'}
                ],
                'hints': ['Dynamic programming approach works in O(n^2)', 'Binary search can optimize to O(n log n)']
            }
        ],
        'total_questions': 37,
        'generated_at': datetime.now().isoformat(),
        'fallback': True
    }


@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates with optional filtering"""
    job_id = request.args.get('job_id')
    
    if job_id:
        filtered = [c for c in candidates if c['job_id'] == job_id]
        return jsonify(filtered), 200
    
    return jsonify(candidates), 200

@app.route('/api/candidates/<candidate_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_candidate(candidate_id):
    """Get, update, or delete candidate details"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    if request.method == 'PUT':
        updates = request.json
        candidate.update(updates)
        save_json(CANDIDATES_FILE, candidates)
        return jsonify(candidate), 200
    
    if request.method == 'DELETE':
        # Get rejection reason from request
        data = request.json or {}
        reason = data.get('reason', 'After careful consideration')
        should_send_email = data.get('send_email', True)
        
        # Get job title for email
        job = next((j for j in jobs if j['id'] == candidate.get('job_id')), None)
        job_title = job.get('title', 'the position') if job else 'the position'
        
        email_result = {'success': False, 'message': 'Email not sent'}
        
        if should_send_email:
            # Send real rejection email via SendGrid
            email_result = sendgrid_rejection_email(
                candidate_name=candidate.get('name', 'Candidate'),
                candidate_email=candidate.get('email', ''),
                job_title=job_title,
                skills=candidate.get('skills', [])
            )
        
        # Remove candidate from list
        candidates.remove(candidate)
        save_json(CANDIDATES_FILE, candidates)
        
        return jsonify({
            'success': True,
            'message': 'Candidate removed successfully',
            'email_sent': email_result.get('success', False),
            'email_result': email_result,
            'candidate_name': candidate.get('name'),
            'candidate_email': candidate.get('email')
        }), 200
    
    return jsonify(candidate), 200


def generate_rejection_email(candidate: dict, reason: str) -> dict:
    """Generate an AI-powered professional rejection email"""
    name = candidate.get('name', 'Candidate')
    email = candidate.get('email', '')
    job_applied = candidate.get('job_id', 'the position')
    skills = candidate.get('skills', [])
    
    # Get job title if available
    job = next((j for j in jobs if j['id'] == job_applied), None)
    job_title = job.get('title', 'the position') if job else 'the position'
    
    subject = f"Update on Your Application for {job_title}"
    
    body = f"""Dear {name},

Thank you for taking the time to apply for the {job_title} position and for your interest in joining our team.

{reason}, we have decided to move forward with other candidates whose qualifications more closely match our current requirements for this role.

We were impressed by your background{' in ' + ', '.join(skills[:3]) if skills else ''}, and we encourage you to apply for future openings that match your skill set.

We truly appreciate the effort you put into your application and wish you the very best in your career journey.

If you have any questions, please don't hesitate to reach out.

Warm regards,

The Hiring Team
GCC Hiring System

---
This is an automated email sent via GCC Hiring System.
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: #ffffff; padding: 30px; border: 1px solid #e5e7eb; }}
        .footer {{ background: #f9fafb; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; border-radius: 0 0 8px 8px; }}
        .highlight {{ color: #4f46e5; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">Application Update</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{name}</strong>,</p>
            
            <p>Thank you for taking the time to apply for the <span class="highlight">{job_title}</span> position and for your interest in joining our team.</p>
            
            <p>{reason}, we have decided to move forward with other candidates whose qualifications more closely match our current requirements for this role.</p>
            
            <p>We were impressed by your background{' in <strong>' + ', '.join(skills[:3]) + '</strong>' if skills else ''}, and we encourage you to apply for future openings that match your skill set.</p>
            
            <p>We truly appreciate the effort you put into your application and wish you the very best in your career journey.</p>
            
            <p>If you have any questions, please don't hesitate to reach out.</p>
            
            <p>Warm regards,<br><strong>The Hiring Team</strong></p>
        </div>
        <div class="footer">
            <p>This is an automated email sent via GCC Hiring System</p>
            <p>© 2024 GCC Hiring System. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return {
        'to': email,
        'subject': subject,
        'body': body,
        'html_body': html_body,
        'sent_at': datetime.now().isoformat(),
        'type': 'rejection'
    }


@app.route('/api/candidates/<candidate_id>/send-rejection', methods=['POST'])
def send_rejection_email_endpoint(candidate_id):
    """Send rejection email to candidate without removing them"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    # Get job title for email
    job = next((j for j in jobs if j['id'] == candidate.get('job_id')), None)
    job_title = job.get('title', 'the position') if job else 'the position'
    
    # Send real rejection email via SendGrid
    email_result = sendgrid_rejection_email(
        candidate_name=candidate.get('name', 'Candidate'),
        candidate_email=candidate.get('email', ''),
        job_title=job_title,
        skills=candidate.get('skills', [])
    )
    
    # Update candidate status
    candidate['status'] = 'Rejected'
    candidate['rejection_email_sent'] = email_result.get('success', False)
    candidate['rejection_date'] = datetime.now().isoformat()
    save_json(CANDIDATES_FILE, candidates)
    
    return jsonify({
        'success': email_result.get('success', False),
        'message': email_result.get('message', 'Email sent'),
        'email_result': email_result
    }), 200


# ======================== PHASE 1: CANDIDATE SCREENING ========================

@app.route('/api/candidates/<candidate_id>/score', methods=['GET'])
def get_candidate_score(candidate_id):
    """Get AI-generated candidate score with auto-rejection for low scores"""
    job_id = request.args.get('job_id', 'JOB1')
    
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    # Get job for context
    job = next((j for j in jobs if j['id'] == job_id), jobs[0] if jobs else {})
    job_title = job.get('title', 'the position') if job else 'the position'
    
    # Use AI scorer
    score = candidate_scorer.score_candidate(candidate, job)
    
    # Update candidate
    candidate['score'] = score['overall_score']
    candidate['category'] = score['category']
    candidate['skill_gaps'] = score.get('skill_gaps', [])
    candidate['scored_at'] = datetime.now().isoformat()
    
    email_result = None
    auto_rejected = False
    
    # AUTO-REJECTION: If score is below threshold, automatically reject and send email
    if score['overall_score'] < AUTO_REJECT_THRESHOLD:
        auto_rejected = True
        candidate['status'] = 'Auto-Rejected'
        candidate['rejection_reason'] = f"Score {score['overall_score']}% below threshold ({AUTO_REJECT_THRESHOLD}%)"
        candidate['rejection_date'] = datetime.now().isoformat()
        
        # Generate AI rejection email
        email_content = groq_rejection_email(
            candidate_name=candidate.get('name', 'Candidate'),
            job_title=job_title,
            skills=candidate.get('skills', [])
        )
        
        # Send rejection email via SendGrid
        email_result = send_email(
            to_email=candidate.get('email', ''),
            subject=email_content.get('subject', f"Update on Your Application"),
            html_content=email_content.get('html_body', email_content.get('body', ''))
        )
        
        candidate['rejection_email_sent'] = email_result.get('success', False)
        
        print(f"[Auto-Reject] Candidate {candidate['name']} scored {score['overall_score']}% - REJECTED")
    
    # If score is good (>= 60%), send shortlist email
    elif score['overall_score'] >= 40:
        candidate['status'] = 'Shortlisted'
        
        # Generate AI shortlist email
        email_content = generate_shortlisted_email(
            candidate_name=candidate.get('name', 'Candidate'),
            job_title=job_title
        )
        
        # Send shortlist email
        email_result = send_email(
            to_email=candidate.get('email', ''),
            subject=email_content.get('subject', f"Great News! You've Been Shortlisted"),
            html_content=email_content.get('html_body', email_content.get('body', ''))
        )
        
        print(f"[Shortlist] Candidate {candidate['name']} scored {score['overall_score']}% - SHORTLISTED")
    
    save_json(CANDIDATES_FILE, candidates)
    
    return jsonify({
        **score,
        'auto_rejected': auto_rejected,
        'email_sent': email_result.get('success', False) if email_result else False,
        'status': candidate.get('status', 'Scored')
    }), 200

@app.route('/api/jobs/<job_id>/salary-recommendation', methods=['GET'])
def get_salary_recommendation(job_id):
    """Get salary recommendation for job"""
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    location = job.get('location', 'Remote')
    experience = 5
    
    recommendation = salary_recommender.get_salary_recommendation(
        job.get('title'),
        location,
        experience
    )
    
    return jsonify(recommendation), 200

@app.route('/api/jobs/<job_id>/interview-panel', methods=['GET'])
def get_interview_panel_recommendation(job_id):
    """Get AI-recommended interview panel"""
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    job_requirements = job.get('requirements', {})
    panel_recommendation = interview_panel_recommender.recommend_panel(job_requirements)
    
    return jsonify(panel_recommendation), 200


@app.route('/api/jobs/<job_id>/assessment-recommendation', methods=['GET'])
def get_assessment_recommendation(job_id):
    """Get AI-recommended assessment for job"""
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    recommendation = assessment_recommender.recommend_assessment(job.get('title', 'General'))
    return jsonify(recommendation), 200


@app.route('/api/candidates/<candidate_id>/screening-summary', methods=['GET'])
def get_screening_summary(candidate_id):
    """Get comprehensive screening summary"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    return jsonify({
        'candidate_id': candidate_id,
        'name': candidate.get('name'),
        'score': candidate.get('score', 0),
        'category': candidate.get('category', 'Not Screened'),
        'hire_probability': candidate.get('hire_probability', 0),
        'skills': candidate.get('skills', []),
        'skill_gaps': candidate.get('skill_gaps', []),
        'recommendation': candidate.get('recommendation', 'Pending'),
        'screened_at': candidate.get('screened_at', datetime.now().isoformat())
    }), 200

# ======================== PHASE 2: ASSESSMENT & INTERVIEW ========================

@app.route('/api/candidates/<candidate_id>/assessment', methods=['POST'])
def assign_assessment(candidate_id):
    """Assign assessment to candidate"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    job_id = request.json.get('job_id')
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Get assessment recommendation
    assessment_rec = assessment_recommender.recommend_assessment(job.get('title'))
    
    # Send assessment
    result = integration_manager.send_assessment(
        assessment_rec['recommended_assessment'],
        {
            'candidate_email': candidate.get('email'),
            'candidate_name': candidate.get('name')
        }
    )
    
    # Save assessment record
    candidate['assessment'] = {
        'job_id': job_id,
        'type': assessment_rec['recommended_assessment'],
        'platform': assessment_rec['details']['platform'],
        'assigned_at': datetime.now().isoformat(),
        'status': 'pending',
        'assessment_id': result.get('assessment_id')
    }
    save_json(CANDIDATES_FILE, candidates)
    
    # Send email
    email_template = f"""
    <h2>Assessment Ready!</h2>
    <p>Hi {candidate.get('name')},</p>
    <p>Your assessment for <strong>{job.get('title')}</strong> is ready.</p>
    <p>Type: {assessment_rec['details']['type']}</p>
    <p>Duration: {assessment_rec['details']['duration_minutes']} minutes</p>
    <p><a href="{result.get('invite_link')}">Start Assessment</a></p>
    <p>Complete by: {datetime.now() + timedelta(days=7)}</p>
    """
    integration_manager.send_notification(candidate, 'assessment_ready', email_template)
    
    return jsonify({
        'success': True,
        'assessment_id': result.get('assessment_id'),
        'assessment_type': assessment_rec['recommended_assessment'],
        'invite_link': result.get('invite_link'),
        'expires_in_days': result.get('expires_in_days', 7)
    }), 200

@app.route('/api/candidates/<candidate_id>/assessment/score', methods=['GET'])
def get_assessment_score(candidate_id):
    """Get assessment score"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    assessment = candidate.get('assessment', {})
    assessment_id = assessment.get('assessment_id')
    
    if not assessment_id:
        return jsonify({'error': 'No assessment found'}), 404
    
    # Get score from platform
    if assessment.get('platform') == 'HackerRank':
        score_data = integration_manager.hackerrank.get_assessment_score(assessment_id)
    elif assessment.get('platform') == 'Codility':
        score_data = integration_manager.codility.get_assessment_score(assessment_id)
    else:
        score_data = {'success': False, 'error': 'Unknown platform'}
    
    if score_data.get('success'):
        candidate['assessment']['score'] = score_data.get('score')
        candidate['assessment']['status'] = 'completed'
        candidate['assessment']['submitted_at'] = score_data.get('submitted_at')
        save_json(CANDIDATES_FILE, candidates)
        
        # Auto-schedule interview if score > 70
        if score_data.get('score', 0) >= 70:
            candidate['assessment']['next_step'] = 'Interview Scheduled'
    
    return jsonify(score_data), 200


@app.route('/api/interviewers', methods=['GET'])
def get_interviewers():
    """Get list of all available interviewers"""
    return jsonify(MOCK_INTERVIEWERS), 200


@app.route('/api/interviewers/match/<candidate_id>', methods=['GET'])
def get_matched_interviewer(candidate_id):
    """Get best matched interviewer for a candidate based on skills"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    job_id = candidate.get('job_id')
    job = next((j for j in jobs if j['id'] == job_id), None)
    job_title = job.get('title', 'Software Engineer') if job else 'Software Engineer'
    
    candidate_skills = candidate.get('skills', [])
    matched_interviewer = match_interviewer(candidate_skills, job_title)
    
    # Calculate matching skills
    matched_skills = []
    if matched_interviewer:
        for skill in candidate_skills:
            for exp in matched_interviewer.get('expertise', []):
                if skill.lower() in exp.lower() or exp.lower() in skill.lower():
                    matched_skills.append(skill)
                    break
    
    return jsonify({
        'interviewer': matched_interviewer,
        'matching_skills': list(set(matched_skills)),
        'match_reason': f"Best match based on {len(matched_skills)} overlapping skills"
    }), 200


@app.route('/api/candidates/<candidate_id>/assign-interviewer', methods=['POST'])
def assign_interviewer_to_candidate(candidate_id):
    """Assign an interviewer to a candidate and send notification email"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    data = request.json or {}
    interviewer_id = data.get('interviewer_id')
    scheduled_date = data.get('scheduled_date')
    scheduled_time = data.get('scheduled_time')
    
    # Get interviewer (either specified or auto-matched)
    if interviewer_id:
        interviewer = next((i for i in MOCK_INTERVIEWERS if i['id'] == interviewer_id), None)
    else:
        job_id = candidate.get('job_id')
        job = next((j for j in jobs if j['id'] == job_id), None)
        job_title = job.get('title', 'Software Engineer') if job else 'Software Engineer'
        interviewer = match_interviewer(candidate.get('skills', []), job_title)
    
    if not interviewer:
        return jsonify({'error': 'No interviewer available'}), 404
    
    # Get job details
    job_id = candidate.get('job_id')
    job = next((j for j in jobs if j['id'] == job_id), None)
    job_title = job.get('title', 'the position') if job else 'the position'
    
    # Update candidate with assigned interviewer
    candidate['assigned_interviewer'] = {
        'interviewer_id': interviewer['id'],
        'interviewer_name': interviewer['name'],
        'interviewer_email': interviewer['email'],
        'interviewer_role': interviewer['role'],
        'interviewer_expertise': interviewer['expertise'],
        'scheduled_date': scheduled_date,
        'scheduled_time': scheduled_time,
        'assigned_at': datetime.now().isoformat()
    }
    save_json(CANDIDATES_FILE, candidates)
    
    # Send email notification to candidate
    subject = f"🗓️ Interview Scheduled - {job_title} | GCC"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
            .header h1 {{ margin: 0 0 10px 0; font-size: 26px; }}
            .content {{ padding: 35px 30px; }}
            .interviewer-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin: 20px 0; }}
            .interviewer-name {{ font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 5px; }}
            .interviewer-role {{ color: #64748b; font-size: 14px; margin-bottom: 15px; }}
            .expertise-tag {{ display: inline-block; background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 15px; font-size: 12px; margin: 2px; }}
            .schedule-box {{ background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; padding: 15px; margin: 20px 0; }}
            .footer {{ background: #f9fafb; padding: 25px; text-align: center; color: #6b7280; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗓️ Interview Scheduled!</h1>
                <p>Your interview has been confirmed</p>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate.get('name')}</strong>,</p>
                
                <p>Great news! Your interview for the <strong>{job_title}</strong> position has been scheduled.</p>
                
                <div class="interviewer-card">
                    <div class="interviewer-name">👤 {interviewer['name']}</div>
                    <div class="interviewer-role">{interviewer['role']} • {interviewer['experience_years']} years experience</div>
                    <div style="margin-top: 10px;">
                        <strong style="font-size: 12px; color: #64748b;">EXPERTISE:</strong><br>
                        {''.join([f'<span class="expertise-tag">{skill}</span>' for skill in interviewer['expertise'][:5]])}
                    </div>
                </div>
                
                <div class="schedule-box">
                    <strong>📅 Interview Schedule</strong><br>
                    <p style="margin: 10px 0 0 0;">
                        <strong>Date:</strong> {scheduled_date or 'To be confirmed'}<br>
                        <strong>Time:</strong> {scheduled_time or 'To be confirmed'}<br>
                        <strong>Mode:</strong> Video Call / In-Person (details will follow)
                    </p>
                </div>
                
                <p>Please be prepared and ensure you have a stable internet connection if it's a video call.</p>
                
                <p>Best of luck!</p>
                
                <p style="margin-top: 30px;">
                    Warm regards,<br>
                    <strong style="color: #667eea;">The Recruitment Team</strong><br>
                    GCC Hiring System
                </p>
            </div>
            <div class="footer">
                <p>© 2025 GCC Hiring System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    email_result = send_email(
        to_email=candidate.get('email'),
        subject=subject,
        html_content=html_content
    )
    
    return jsonify({
        'success': True,
        'interviewer': interviewer,
        'candidate_id': candidate_id,
        'email_sent': email_result.get('success', False),
        'message': f"Interviewer {interviewer['name']} assigned to {candidate.get('name')}"
    }), 200


@app.route('/api/candidates/<candidate_id>/interview/schedule', methods=['POST'])
def schedule_interview(candidate_id):
    """Schedule interview with smart calendar integration"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    job_id = request.json.get('job_id')
    job = next((j for j in jobs if j['id'] == job_id), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Get interview panel
    panel_recommendation = interview_panel_recommender.recommend_panel(job.get('requirements', {}))
    
    # Get available slots
    calendar_provider = request.json.get('calendar_provider', 'google')
    calendar_api = integration_manager.google_calendar if calendar_provider == 'google' else integration_manager.outlook
    
    available_slots = calendar_api.get_free_slots('hiring@company.com', 60)
    
    # Create event
    event_data = {
        'title': f"Interview - {job.get('title')}",
        'description': f"Interview round for {job.get('title')} position",
        'start_time': available_slots[0]['start'] if available_slots else None,
        'end_time': available_slots[0]['end'] if available_slots else None,
        'attendees': [
            candidate.get('email'),
            'hiring@company.com'
        ] + [p.get('email', 'interviewer@company.com') for p in panel_recommendation.get('recommended_panel', [])]
    }
    
    result = calendar_api.create_event(event_data)
    
    # Save interview record
    candidate['interview'] = {
        'job_id': job_id,
        'status': 'scheduled',
        'scheduled_at': datetime.now().isoformat(),
        'interview_time': available_slots[0]['start'] if available_slots else None,
        'interview_panel': panel_recommendation['recommended_panel'],
        'event_id': result.get('event_id'),
        'zoom_link': 'https://zoom.us/j/xyz123'
    }
    save_json(CANDIDATES_FILE, candidates)
    
    # Send interview invite email
    email_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 14px 32px; border-radius: 6px; text-decoration: none; margin-top: 20px; font-weight: bold; }}
            .button:hover {{ opacity: 0.9; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 13px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
            .details-box {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #667eea; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📅 Interview Scheduled!</h1>
                <p>Next Step in Your Journey with GCC</p>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate.get('name')}</strong>,</p>
                
                <p>Great news! 🎉 Your interview has been scheduled for the <strong>{job.get('title')}</strong> position.</p>
                
                <div class="details-box">
                    <strong>Interview Details:</strong><br>
                    <div style="margin-top: 10px;">
                        <div><strong>Date & Time:</strong> {available_slots[0]['start'] if available_slots else 'TBD'}</div>
                        <div><strong>Duration:</strong> 60 minutes</div>
                        <div><strong>Format:</strong> Virtual (Zoom/Video Call)</div>
                    </div>
                </div>
                
                <div class="details-box">
                    <strong>Interview Panel:</strong><br>
                    <div style="margin-top: 10px;">
    """
    
    # Add interviewer details
    if panel_recommendation.get('recommended_panel'):
        for idx, interviewer in enumerate(panel_recommendation.get('recommended_panel', [])[:3], 1):
            email_template += f"<div>Round {idx}: {interviewer.get('name', 'TBD')} - {interviewer.get('expertise', 'Interviewer')}</div>\n"
    
    email_template += f"""
                    </div>
                </div>
                
                <p style="color: #6b7280; font-size: 14px; margin: 20px 0;">
                    <strong>Important:</strong> Please confirm your availability by clicking the button below.
                    If you need to reschedule, please reply to this email as soon as possible.
                </p>
                
                <div style="text-align: center;">
                    <a href="https://zoom.us/j/xyz123" class="button">Join Interview →</a>
                </div>
                
                <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">
                    If you have any questions about the interview, please feel free to reach out to our team.
                </p>
                
                <div class="footer">
                    <p>We look forward to meeting you!</p>
                    <p>© GCC Hiring System</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Send email using the main send_email function
    email_result = send_email(
        to_email=candidate.get('email'),
        subject=f"Interview Scheduled - {job.get('title')} - GCC Hiring",
        html_content=email_template
    )
    
    print(f"[Interview Schedule] Interview email sent to {candidate.get('name')}: {email_result.get('success', False)}")
    if not email_result.get('success'):
        print(f"[Interview Schedule] Email error: {email_result.get('error', 'Unknown error')}")
    
    return jsonify({
        'success': True,
        'interview_scheduled': True,
        'scheduled_time': available_slots[0]['start'] if available_slots else None,
        'interview_panel': panel_recommendation['recommended_panel'],
        'zoom_link': 'https://zoom.us/j/xyz123',
        'available_slots': available_slots[:3]
    }), 200

@app.route('/api/interview/<interview_token>/resend-email', methods=['POST'])
def resend_interview_email(interview_token):
    """Resend interview invitation email with updated interview link"""
    try:
        print(f"[Resend Interview Email] Processing request for token: {interview_token}")
        
        # Get interview session
        session = interview_session_manager.get_interview_session(interview_token)
        if not session:
            print(f"[Resend Interview Email] Session not found for token: {interview_token}")
            return jsonify({'error': 'Interview session not found'}), 404
        
        # Get candidate details
        candidate_id = session.get('candidate_id')
        candidate_name = session.get('candidate_name')
        job_id = session.get('job_id')
        
        candidates_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'candidates.json')
        with open(candidates_file, 'r') as f:
            candidates_data = json.load(f).get('candidates', [])
            candidate = next((c for c in candidates_data if c.get('id') == candidate_id), None)
        
        if not candidate:
            print(f"[Resend Interview Email] Candidate not found: {candidate_id}")
            return jsonify({'error': 'Candidate not found'}), 404
        
        # Get job details
        jobs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'jobs.json')
        with open(jobs_file, 'r') as f:
            jobs_data = json.load(f).get('jobs', [])
            job = next((j for j in jobs_data if j.get('id') == job_id), None)
        
        if not job:
            print(f"[Resend Interview Email] Job not found: {job_id}")
            return jsonify({'error': 'Job not found'}), 404
        
        email = candidate.get('email')
        job_title = job.get('title', 'Software Engineer')
        
        # Get frontend URL from environment
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        interview_link = f"{frontend_url}/interview/{interview_token}"
        
        # Create email content
        expires_at = session.get('expires_at', '')[:10] if session.get('expires_at') else '7 days'
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f5f5f5; }}
                .email-container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
                .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                .content {{ padding: 35px 30px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea, #764ba2); color: white !important; padding: 16px 40px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 16px; margin: 25px 0; transition: transform 0.2s; }}
                .cta-button:hover {{ transform: scale(1.05); }}
                .footer {{ background: #f8fafc; padding: 20px 30px; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🎯 Your Interview Link</h1>
                    <p>Ready to take the next step?</p>
                </div>
                <div class="content">
                    <p>Hi {candidate_name},</p>
                    <p>We're excited to move forward with your interview for the <strong>{job_title}</strong> position at GCC!</p>
                    <p>Click the button below to start your interview:</p>
                    <center>
                        <a href="{interview_link}" class="cta-button">Start Interview</a>
                    </center>
                    <p><strong>⏰ Important:</strong> This interview link expires on <strong>{expires_at}</strong></p>
                    <p>If you have any questions or need to reschedule, please don't hesitate to reach out to us.</p>
                    <p>Best of luck with your interview! 🚀</p>
                    <p>Warm regards,<br>The GCC Hiring Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2024 GCC Hiring System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        print(f"[Resend Interview Email] Sending email to {email} with interview link: {interview_link}")
        email_result = send_email(
            to_email=email,
            subject=f"🎯 Your Interview Link - {job_title} at GCC",
            html_content=html_content
        )
        
        print(f"[Resend Interview Email] Email result: {email_result}")
        
        if email_result.get('success'):
            print(f"[Resend Interview Email] ✅ SUCCESS - Interview email resent to {candidate_name}")
            return jsonify({
                'success': True,
                'message': f'Interview email resent to {email}',
                'interview_link': interview_link
            }), 200
        else:
            print(f"[Resend Interview Email] ❌ FAILED - {email_result.get('error', 'Unknown error')}")
            return jsonify({
                'success': False,
                'error': email_result.get('error', 'Failed to send email'),
                'message': email_result.get('message', 'Failed to send interview email')
            }), 500
            
    except Exception as e:
        print(f"[Resend Interview Email] Exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while resending the interview email'
        }), 500

@app.route('/api/candidates/<candidate_id>/interview/feedback', methods=['POST'])
def submit_interview_feedback(candidate_id):
    """Submit interview feedback from interviewer"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    feedback_data = request.json
    
    # Store feedback
    if 'interview_feedback' not in candidate:
        candidate['interview_feedback'] = []
    
    feedback_record = {
        'interviewer': feedback_data.get('interviewer'),
        'round': feedback_data.get('round'),
        'technical_score': feedback_data.get('technical_score'),
        'soft_skills_score': feedback_data.get('soft_skills_score'),
        'overall_recommendation': feedback_data.get('recommendation'),
        'comments': feedback_data.get('comments'),
        'submitted_at': datetime.now().isoformat()
    }
    
    candidate['interview_feedback'].append(feedback_record)
    save_json(CANDIDATES_FILE, candidates)
    
    # Calculate overall score after all feedbacks collected
    if len(candidate.get('interview_feedback', [])) >= 3:
        scores = [f.get('technical_score', 0) + f.get('soft_skills_score', 0) for f in candidate['interview_feedback']]
        avg_score = sum(scores) / len(scores)
        candidate['interview_score'] = round(avg_score / 2, 2)  # Out of 100
        candidate['interview_status'] = 'completed'
        
        # Auto-trigger offer if score > 75
        if candidate['interview_score'] > 75:
            candidate['recommendation'] = 'Proceed to Offer'
        
        save_json(CANDIDATES_FILE, candidates)
    
    return jsonify({
        'success': True,
        'feedback_recorded': True,
        'interview_score': candidate.get('interview_score', 'Pending')
    }), 200

@app.route('/api/candidates/<candidate_id>/interview-scores', methods=['GET'])
def get_candidate_interview_scores(candidate_id):
    """Get interview scores for a candidate from their AI-evaluated interview session"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    # Check if candidate has completed interview round 1
    interview_data = candidate.get('interview_round_1', {})
    
    if interview_data.get('status') != 'completed':
        return jsonify({
            'error': 'No completed interview found',
            'status': interview_data.get('status', 'not_started')
        }), 404
    
    # Get detailed scores
    overall_score = interview_data.get('score', 0)
    technical_score = interview_data.get('technical_score', 0)
    behavioral_score = interview_data.get('behavioral_score', 0)
    coding_score = interview_data.get('coding_score', 0)
    
    # Get AI evaluation feedback/recommendation
    ai_evaluation = interview_data.get('ai_evaluation', {})
    recommendation = interview_data.get('recommendation', ai_evaluation.get('recommendation', 'N/A'))
    ai_feedback = ai_evaluation.get('recommendation_detail', ai_evaluation.get('detailed_feedback', ''))
    
    # Check HR qualification status
    HR_INTERVIEW_THRESHOLD = 80
    qualifies_for_hr = overall_score >= HR_INTERVIEW_THRESHOLD
    
    return jsonify({
        'success': True,
        'candidate_id': candidate_id,
        'candidate_name': candidate.get('name'),
        'overall_score': overall_score,
        'technical_score': technical_score,
        'behavioral_score': behavioral_score,
        'coding_score': coding_score,
        'recommendation': recommendation,
        'ai_feedback': ai_feedback,
        'qualifies_for_hr_interview': qualifies_for_hr,
        'hr_threshold': HR_INTERVIEW_THRESHOLD,
        'completed_at': interview_data.get('completed_at'),
        'status': candidate.get('status'),
        'hr_interview': candidate.get('hr_interview')
    }), 200

# ======================== PHASE 3: OFFER & ONBOARDING ========================

@app.route('/api/candidates/<candidate_id>/offer', methods=['POST'])
def generate_offer(candidate_id):
    """Generate and send offer letter"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    offer_data = request.json
    job_id = offer_data.get('job_id')
    job = next((j for j in jobs if j['id'] == job_id), None)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Get salary recommendation
    location = job.get('location', 'Remote')
    experience = 5
    salary_rec = salary_recommender.get_salary_recommendation(
        job.get('title'),
        location,
        experience
    )
    
    # Create offer package
    offer_package = {
        'candidate_id': candidate_id,
        'candidate_name': candidate.get('name'),
        'candidate_email': candidate.get('email'),
        'position': job.get('title'),
        'department': job.get('department'),
        'location': job.get('location'),
        'salary': offer_data.get('salary', salary_rec.get('suggested', 20)),
        'joining_date': offer_data.get('joining_date'),
        'benefits': ['Health Insurance', 'Stock Options', 'Flexible WFH', '20 Days PTO'],
        'created_at': datetime.now().isoformat()
    }
    
    # Send for e-signature
    docusign_result = integration_manager.send_offer_for_signature(offer_package)
    
    # Save offer record
    candidate['offer'] = {
        'job_id': job_id,
        'status': 'pending_signature',
        'salary': offer_package['salary'],
        'joining_date': offer_package['joining_date'],
        'created_at': offer_package['created_at'],
        'envelope_id': docusign_result.get('envelope_id'),
        'signing_link': docusign_result.get('signing_link')
    }
    save_json(CANDIDATES_FILE, candidates)
    
    # Send offer email
    email_template = f"""
    <h2>Offer Letter - {job.get('title')}</h2>
    <p>Hi {candidate.get('name')},</p>
    <p>Congratulations! We're pleased to offer you the position of <strong>{job.get('title')}</strong> at [Company].</p>
    <p><strong>Offer Details:</strong></p>
    <ul>
        <li>Position: {job.get('title')}</li>
        <li>Salary: ₹{offer_package['salary']} LPA</li>
        <li>Joining Date: {offer_package['joining_date']}</li>
        <li>Location: {job.get('location')}</li>
    </ul>
    <p><a href="{docusign_result.get('signing_link')}">Sign Offer Letter</a></p>
    """
    integration_manager.send_notification(candidate, 'offer_sent', email_template)
    
    return jsonify({
        'success': True,
        'offer_id': docusign_result.get('envelope_id'),
        'status': 'sent_for_signature',
        'signing_link': docusign_result.get('signing_link'),
        'salary': offer_package['salary'],
        'benefits': offer_package['benefits']
    }), 200

@app.route('/api/candidates/<candidate_id>/offer/status', methods=['GET'])
def check_offer_status(candidate_id):
    """Check offer signature status"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    offer = candidate.get('offer')
    if not offer:
        return jsonify({'error': 'No offer found'}), 404
    
    envelope_id = offer.get('envelope_id')
    
    # Check signature status
    sig_status = integration_manager.docusign.check_signature_status(envelope_id)
    
    if sig_status.get('status') == 'completed':
        candidate['offer']['status'] = 'accepted'
        candidate['offer']['signed_at'] = sig_status.get('signed_at')
        candidate['status'] = 'Offer Accepted'
        save_json(CANDIDATES_FILE, candidates)
        
        # Trigger onboarding
        return jsonify({
            'success': True,
            'status': 'accepted',
            'signed_at': sig_status.get('signed_at'),
            'next_step': 'Onboarding Started'
        }), 200
    
    return jsonify({
        'success': True,
        'status': 'pending',
        'message': 'Waiting for candidate to sign'
    }), 200

@app.route('/api/send-offer-letter', methods=['POST'])
def send_offer_letter_email():
    """Send offer letter via email to selected candidate"""
    data = request.json
    candidate_id = data.get('candidate_id')
    
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'success': False, 'error': 'Candidate not found'}), 404
    
    salary = data.get('salary', 0)
    position = data.get('position', 'Software Developer')
    joining_date = data.get('joining_date', 'To be confirmed')
    benefits = data.get('benefits', '')
    additional_notes = data.get('additional_notes', '')
    
    candidate_name = candidate.get('name', 'Candidate')
    candidate_email = candidate.get('email')
    
    if not candidate_email:
        return jsonify({'success': False, 'error': 'Candidate email not found'}), 400
    
    # Create beautiful HTML offer letter email
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🎉 Congratulations!</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Job Offer Letter</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <p style="color: #1f2937; font-size: 16px; margin: 0 0 20px 0;">
                    Dear <strong>{candidate_name}</strong>,
                </p>
                
                <p style="color: #4b5563; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                    We are thrilled to extend an offer to join our team! After careful consideration of your qualifications and interview performance, we believe you would be an excellent addition to our organization.
                </p>
                
                <!-- Offer Details Card -->
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border-radius: 12px; padding: 24px; margin: 30px 0; border-left: 4px solid #10b981;">
                    <h2 style="color: #047857; margin: 0 0 20px 0; font-size: 20px;">📋 Offer Details</h2>
                    
                    <div style="margin-bottom: 16px;">
                        <p style="color: #6b7280; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Position</p>
                        <p style="color: #1f2937; margin: 4px 0 0 0; font-size: 18px; font-weight: 600;">{position}</p>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <p style="color: #6b7280; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Annual Salary</p>
                        <p style="color: #10b981; margin: 4px 0 0 0; font-size: 24px; font-weight: 700;">${salary:,} USD</p>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <p style="color: #6b7280; margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Proposed Start Date</p>
                        <p style="color: #1f2937; margin: 4px 0 0 0; font-size: 16px; font-weight: 600;">{joining_date}</p>
                    </div>
                </div>
                
                {f'''
                <!-- Benefits -->
                <div style="background-color: #f3f4f6; border-radius: 12px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #374151; margin: 0 0 12px 0; font-size: 16px;">✨ Benefits Package</h3>
                    <p style="color: #4b5563; margin: 0; font-size: 14px; line-height: 1.6;">{benefits}</p>
                </div>
                ''' if benefits else ''}
                
                {f'''
                <!-- Additional Notes -->
                <div style="background-color: #fef3c7; border-radius: 12px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #92400e; margin: 0 0 12px 0; font-size: 16px;">📝 Additional Information</h3>
                    <p style="color: #78350f; margin: 0; font-size: 14px; line-height: 1.6;">{additional_notes}</p>
                </div>
                ''' if additional_notes else ''}
                
                <p style="color: #4b5563; font-size: 15px; line-height: 1.6; margin: 30px 0 20px 0;">
                    We are confident that your skills and experience will make a significant contribution to our team. Please review the offer details and let us know your decision.
                </p>
                
                <!-- CTA Button -->
                <div style="text-align: center; margin: 30px 0;">
                    <a href="mailto:hr@company.com?subject=Offer%20Acceptance%20-%20{candidate_name}" 
                       style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; padding: 16px 40px; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(16,185,129,0.3);">
                        ✅ Accept This Offer
                    </a>
                </div>
                
                <p style="color: #6b7280; font-size: 13px; text-align: center; margin-top: 30px;">
                    If you have any questions, please don't hesitate to contact us.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #1f2937; padding: 30px; text-align: center;">
                <p style="color: #9ca3af; margin: 0; font-size: 13px;">
                    This offer is contingent upon successful background verification and reference checks.
                </p>
                <p style="color: #6b7280; margin: 10px 0 0 0; font-size: 12px;">
                    © {datetime.now().year} GCC Hiring System
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    try:
        # Send via SendGrid
        from config.email_config import send_offer_email
        result = send_offer_email(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            position=position,
            salary=salary,
            joining_date=joining_date,
            html_content=html_content
        )
        
        if result.get('success'):
            # Update candidate record
            candidate['offer'] = {
                'status': 'sent',
                'position': position,
                'salary': salary,
                'joining_date': joining_date,
                'sent_at': datetime.now().isoformat(),
                'email_sent': True
            }
            candidate['status'] = 'Offer Sent'
            save_json(CANDIDATES_FILE, candidates)
            
            print(f"[Offer] ✅ Offer letter sent to {candidate_email}")
            
            return jsonify({
                'success': True,
                'message': f'Offer letter sent to {candidate_email}',
                'offer': candidate['offer']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to send email')
            }), 500
            
    except Exception as e:
        print(f"[Offer] ❌ Error sending offer: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidates/<candidate_id>/onboarding', methods=['POST'])
def start_onboarding(candidate_id):
    """Start onboarding workflow"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    onboarding_data = request.json
    
    # Provision employee across systems
    employee_data = {
        'first_name': candidate.get('name', '').split()[0],
        'last_name': candidate.get('name', '').split()[-1] if len(candidate.get('name', '').split()) > 1 else '',
        'email': candidate.get('email'),
        'position': onboarding_data.get('position'),
        'department': onboarding_data.get('department'),
        'joining_date': onboarding_data.get('joining_date'),
        'salary': onboarding_data.get('salary')
    }
    
    # Provision in SAP and ServiceNow
    provisioning_result = integration_manager.provision_employee(employee_data)
    
    # Create onboarding record
    candidate['onboarding'] = {
        'status': 'in_progress',
        'started_at': datetime.now().isoformat(),
        'employee_id': provisioning_result.get('hris', {}).get('employee_id'),
        'it_ticket': provisioning_result.get('it', {}).get('ticket_number'),
        'tasks': [
            {'task': 'IT Provisioning', 'status': 'in_progress', 'owner': 'IT Team'},
            {'task': 'Benefits Enrollment', 'status': 'pending', 'owner': 'HR'},
            {'task': 'Manager Intro', 'status': 'pending', 'owner': 'Manager'},
            {'task': 'Team Onboarding', 'status': 'pending', 'owner': 'Buddy'}
        ],
        'engagement_score': 95,
        'engagement_last_checked': datetime.now().isoformat()
    }
    save_json(CANDIDATES_FILE, candidates)
    
    # Send onboarding email
    email_template = f"""
    <h2>Welcome to [Company]!</h2>
    <p>Hi {candidate.get('name')},</p>
    <p>We're excited to have you joining us!</p>
    <p><strong>Your Onboarding Journey:</strong></p>
    <ul>
        <li>✅ Offer Accepted</li>
        <li>⏳ IT Setup (Laptop, Email, Tools)</li>
        <li>⏳ Benefits Enrollment</li>
        <li>⏳ Day 1 Orientation</li>
        <li>⏳ Manager & Team Meeting</li>
    </ul>
    <p>We'll send you detailed instructions and access links soon.</p>
    <p><a href="http://localhost:3000/onboarding">View Onboarding Portal</a></p>
    """
    integration_manager.send_notification(candidate, 'onboarding_started', email_template)
    
    return jsonify({
        'success': True,
        'onboarding_status': 'started',
        'employee_id': provisioning_result.get('hris', {}).get('employee_id'),
        'it_ticket': provisioning_result.get('it', {}).get('ticket_number'),
        'tasks': candidate['onboarding']['tasks']
    }), 200

@app.route('/api/candidates/<candidate_id>/onboarding/progress', methods=['GET'])
def get_onboarding_progress(candidate_id):
    """Get onboarding progress and engagement tracking"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    onboarding = candidate.get('onboarding', {})
    
    # Mock engagement tracking
    engagement_data = {
        'candidate_id': candidate_id,
        'name': candidate.get('name'),
        'onboarding_stage': onboarding.get('status'),
        'email_engagement': {
            'opened': random.randint(5, 15),
            'clicked': random.randint(2, 8),
            'open_rate': f"{random.randint(60, 100)}%"
        },
        'portal_activity': {
            'logins': random.randint(5, 20),
            'documents_viewed': random.randint(3, 10),
            'tasks_completed': random.randint(1, 4)
        },
        'engagement_score': onboarding.get('engagement_score', 0),
        'risk_level': 'Low' if random.random() > 0.7 else 'Medium',
        'tasks': onboarding.get('tasks', []),
        'recommended_action': 'Continue engagement' if random.random() > 0.3 else 'Schedule check-in call'
    }
    
    return jsonify(engagement_data), 200


# ======================== AI-POWERED INTERVIEW SYSTEM ========================

@app.route('/api/candidates/<candidate_id>/generate-interview', methods=['POST'])
def generate_interview(candidate_id):
    """
    Generate AI-powered interview for candidate if score > 50%
    Includes technical questions, coding challenges, and behavioral questions
    """
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    # Check if candidate score is above threshold
    if candidate.get('match_score', 0) < AUTO_REJECT_THRESHOLD:
        return jsonify({
            'error': f'Candidate score ({candidate.get("match_score")}%) is below interview threshold ({AUTO_REJECT_THRESHOLD}%)',
            'eligible': False
        }), 400
    
    # Get job details
    job = next((j for j in jobs if j['id'] == candidate.get('job_id')), None)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    print(f"\n[Interview Generation] Generating interview for {candidate.get('name')} - {job.get('title')}")
    print(f"[Interview Generation] Resume ATS Score: {candidate.get('match_score')}%")
    
    # Generate interview questions
    interview_questions = interview_generator.generate_interview_questions(
        job.get('requirements', {}),
        candidate.get('skills', []),
        candidate_id=candidate_id,
        job_id=candidate.get('job_id')
    )
    
    if 'error' in interview_questions:
        return jsonify({'error': 'Failed to generate interview questions'}), 500
    
    # Create interview session with public link
    session_info = interview_session_manager.create_interview_session(
        candidate_id=candidate_id,
        candidate_name=candidate.get('name'),
        job_id=candidate.get('job_id'),
        interview_questions=interview_questions
    )
    
    # Update candidate with interview link
    candidate['interview_round_1'] = {
        'status': 'generated',
        'session_id': session_info['session_id'],
        'interview_link': session_info['interview_link'],
        'generated_at': datetime.now().isoformat(),
        'expires_at': session_info['expires_at'],
        'duration_minutes': session_info['interview_duration_minutes']
    }
    save_json(CANDIDATES_FILE, candidates)
    
    # Send interview link via email
    email_result = send_email(
        to_email=candidate.get('email'),
        subject=f"Your AI Interview for {job.get('title')} - GCC Hiring",
        html_content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #3b82f6; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border-radius: 0 0 8px 8px; }}
                .button {{ background: #10b981; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; margin-top: 20px; }}
                .button:hover {{ background: #059669; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 Your AI Interview Round</h1>
                </div>
                <div class="content">
                    <p>Dear {candidate.get('name')},</p>
                    
                    <p>Congratulations! Your resume score of <strong>{candidate.get('match_score')}%</strong> qualifies you for the next round.</p>
                    
                    <p>We're excited to conduct your first round interview using our advanced AI interview system!</p>
                    
                    <h3>📋 Interview Format:</h3>
                    <ul>
                        <li><strong>Duration:</strong> {session_info['interview_duration_minutes']} minutes</li>
                        <li><strong>Format:</strong> AI-powered adaptive interview</li>
                        <li><strong>Components:</strong>
                            <ul>
                                <li>Technical Questions (4)</li>
                                <li>Coding Challenge (1)</li>
                                <li>Behavioral Questions (2)</li>
                            </ul>
                        </li>
                    </ul>
                    
                    <p><strong>⏰ Important:</strong> This interview link expires on <strong>{session_info['expires_at']}</strong></p>
                    
                    <p>Click the button below to start your interview:</p>
                    
                    <a href="{session_info['interview_link']}" class="button">Start Interview →</a>
                    
                    <p style="margin-top: 30px; color: #6b7280; font-size: 13px;">
                        Good luck! The AI will evaluate your technical skills, coding ability, and cultural fit in real-time.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    )
    
    return jsonify({
        'success': True,
        'session_id': session_info['session_id'],
        'interview_link': session_info['interview_link'],
        'interview_token': session_info['interview_token'],
        'duration_minutes': session_info['interview_duration_minutes'],
        'questions_count': {
            'technical': len(interview_questions.get('technical', [])),
            'behavioral': len(interview_questions.get('behavioral', [])),
            'coding': 1 if interview_questions.get('coding') else 0,
            'system_design': 1 if interview_questions.get('system_design') else 0
        },
        'email_sent': email_result.get('success', False),
        'expires_at': session_info['expires_at']
    }), 201


@app.route('/api/interview/<interview_token>/start', methods=['POST'])
def start_interview(interview_token):
    """Start an interview session and generate FRESH unique questions"""
    print(f"\n[API] POST /api/interview/{interview_token}/start")
    
    result = interview_session_manager.start_interview_session(interview_token)
    
    if 'error' in result:
        print(f"[API] ❌ Session not found")
        return jsonify(result), 404
    
    session = interview_session_manager.get_interview_session(interview_token)
    print(f"[API] Session found: {session['session_id']}")
    print(f"[API] Candidate ID: {session['candidate_id']}, Job ID: {session['job_id']}")
    
    # Get candidate and job details to generate FRESH questions
    candidate_id = session.get('candidate_id')
    job_id = session.get('job_id')
    
    # Load candidate details
    candidates_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'candidates.json')
    candidate_data = None
    candidate_skills = []
    
    try:
        with open(candidates_file, 'r') as f:
            data = json.load(f)
            candidates_list = data.get('candidates', [])
            for cand in candidates_list:
                if cand.get('id') == candidate_id:
                    candidate_data = cand
                    candidate_skills = cand.get('skills', [])
                    break
    except Exception as e:
        print(f"[API] Warning: Could not load candidate: {e}")
    
    # Load job details
    jobs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'jobs.json')
    job_data = None
    job_requirements = {}
    
    try:
        with open(jobs_file, 'r') as f:
            data = json.load(f)
            jobs_list = data.get('jobs', [])
            for job in jobs_list:
                if job.get('id') == job_id:
                    job_data = job
                    job_requirements = job.get('requirements', {})
                    break
    except Exception as e:
        print(f"[API] Warning: Could not load job: {e}")
    
    # Generate FRESH unique questions for this candidate
    print(f"[API] 🔄 Generating FRESH unique questions for candidate {candidate_id}...")
    fresh_questions = interview_generator.generate_interview_questions(
        job_requirements,
        candidate_skills,
        candidate_id=candidate_id,  # This ensures uniqueness per candidate
        job_id=job_id,
        job_title=job_data.get('title', 'Software Engineer')
    )
    
    # Flatten the questions for the frontend
    questions = []
    
    # Add technical questions
    technical = fresh_questions.get('technical', [])
    print(f"[API] Adding {len(technical)} technical questions")
    if isinstance(technical, list):
        for q in technical:
            if 'type' not in q:
                q['type'] = 'technical'
            questions.append(q)
    
    # Add behavioral questions
    behavioral = fresh_questions.get('behavioral', [])
    print(f"[API] Adding {len(behavioral)} behavioral questions")
    if isinstance(behavioral, list):
        for q in behavioral:
            if 'type' not in q:
                q['type'] = 'behavioral'
            questions.append(q)
    
    # Add coding questions
    coding = fresh_questions.get('coding', [])
    # Normalize coding structure: handle dicts with medium/easy/hard or questions array
    if isinstance(coding, dict):
        collected = []
        if 'questions' in coding and isinstance(coding['questions'], list):
            collected.extend(coding['questions'])
        for key in ['easy', 'medium', 'hard']:
            if key in coding and isinstance(coding[key], list):
                collected.extend(coding[key])
        if collected:
            coding = collected
        else:
            coding = [coding]
    print(f"[API] Adding {len(coding) if isinstance(coding, list) else 0} coding questions")
    if isinstance(coding, list):
        for q in coding:
            if isinstance(q, dict):
                if 'type' not in q:
                    q['type'] = 'coding'
                questions.append(q)
    
    # Update session with fresh questions ONLY if generation was successful
    if fresh_questions and 'error' not in fresh_questions:
        session['questions'] = fresh_questions
        interview_session_manager.save_sessions()
    else:
        print(f"[API] ⚠️ Question generation failed or returned error. Using existing questions.")
        # Try to use existing questions if possible
        if 'questions' in session and session['questions']:
            fresh_questions = session['questions']
            # Re-flatten questions for the loop below
            questions = []
            for q_type in ['technical', 'behavioral', 'coding']:
                qs = fresh_questions.get(q_type, [])
                if isinstance(qs, list):
                    for q in qs:
                        if 'type' not in q: q['type'] = q_type
                        questions.append(q)
                elif isinstance(qs, dict):
                    if 'type' not in qs: qs['type'] = q_type
                    questions.append(qs)
    
    print(f"[API] ✅ Generated {len(questions)} FRESH unique questions")
    print(f"[API]   - Technical: {len([q for q in questions if q.get('type') == 'technical'])}")
    print(f"[API]   - Behavioral: {len([q for q in questions if q.get('type') == 'behavioral'])}")
    print(f"[API]   - Coding: {len([q for q in questions if q.get('type') == 'coding'])}")
    
    return jsonify({
        'success': True,
        'candidate_name': session['candidate_name'],
        'questions': questions,
        'started_at': result['started_at'],
        'total_questions': len(questions),
        'question_breakdown': {
            'technical': len([q for q in questions if q.get('type') == 'technical']),
            'behavioral': len([q for q in questions if q.get('type') == 'behavioral']),
            'coding': len([q for q in questions if q.get('type') == 'coding'])
        }
    }), 200


@app.route('/api/interview/<interview_token>/submit-response', methods=['POST'])
def submit_response(interview_token):
    """Submit response to a question and evaluate it with AI in real-time"""
    print(f"\n[API] POST /api/interview/{interview_token}/submit-response")
    data = request.json
    question_id = data.get('question_id')
    response = data.get('response')
    question_text = data.get('question_text', '') # Frontend should ideally send this
    question_type = data.get('question_type', 'technical') # Frontend should send this
    
    if not question_id or not response:
        return jsonify({'error': 'Missing question_id or response'}), 400
    
    # 1. Store the response
    result = interview_session_manager.submit_question_response(interview_token, question_id, response)
    
    if 'error' in result:
        return jsonify(result), 404
        
    # 2. Perform real-time AI evaluation
    session = interview_session_manager.get_interview_session(interview_token)
    evaluation = None
    
    if session:
        candidate_id = session.get('candidate_id')
        job_id = session.get('job_id')
        
        # Get candidate/job data for context
        candidate = next((c for c in candidates if c['id'] == candidate_id), None)
        job = next((j for j in jobs if j['id'] == job_id), None) if job_id else None
        
        candidate_skills = candidate.get('skills', []) if candidate else []
        job_title = job.get('title', 'Position') if job else 'Position'
        
        # If question text wasn't provided, try to find it in the session's questions
        if not question_text:
            questions_data = session.get('questions', {})
            # Search in all question lists
            for q_list in questions_data.values():
                if isinstance(q_list, list):
                    for q in q_list:
                        if q.get('id') == question_id:
                            question_text = q.get('question', q.get('description', ''))
                            question_type = q.get('type', question_type)
                            break
        
        print(f"[API] Evaluating answer for {question_id} ({question_type})...")
        evaluation = evaluate_single_answer(
            question=question_text,
            answer=response,
            question_type=question_type,
            candidate_skills=candidate_skills,
            job_title=job_title
        )
        
        # Store evaluation in session
        if 'evaluations' not in session:
            session['evaluations'] = {}
        session['evaluations'][question_id] = evaluation
        interview_session_manager.save_sessions()
        
        print(f"[API] ✅ AI Evaluation Score: {evaluation.get('overall_score', 0)}%")
    
    return jsonify({
        'success': True,
        'message': 'Response submitted and evaluated by AI',
        'evaluation': evaluation
    }), 200


@app.route('/api/interview/<interview_token>/transcribe-speech', methods=['POST'])
def transcribe_speech(interview_token):
    """Transcribe audio using OpenAI Whisper API"""
    print(f"\n[API] POST /api/interview/{interview_token}/transcribe-speech")
    
    try:
        import os
        import tempfile
        from openai import OpenAI
        
        # Check if audio file is in request
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Get OpenAI API key
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("[Whisper] OpenAI API key not configured")
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_path = temp_audio.name
        
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=openai_api_key)
            
            # Transcribe with Whisper
            print(f"[Whisper] Transcribing audio file: {temp_path}")
            with open(temp_path, 'rb') as audio:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en",
                    response_format="text"
                )
            
            transcript_text = transcription if isinstance(transcription, str) else transcription.text
            print(f"[Whisper] ✅ Transcription successful: {transcript_text[:100]}...")
            
            return jsonify({
                'success': True,
                'transcript': transcript_text
            }), 200
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        print(f"[Whisper] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/evaluate-speech', methods=['POST'])
def evaluate_speech(interview_token):
    """Evaluate speech transcript from candidate's verbal answer"""
    print(f"\n[API] POST /api/interview/{interview_token}/evaluate-speech")
    
    try:
        data = request.json
        question_id = data.get('question_id')
        question_text = data.get('question_text', '')
        transcript = data.get('transcript', '')
        recording_duration = data.get('recording_duration', 0)
        
        if not transcript or not transcript.strip():
            return jsonify({'error': 'No transcript provided'}), 400
        
        print(f"[Speech] Question: {question_text[:50]}...")
        print(f"[Speech] Transcript ({len(transcript)} chars, {recording_duration}s): {transcript[:100]}...")
        
        # Get session context
        session = interview_session_manager.get_interview_session(interview_token)
        job_title = "Position"
        
        if session:
            job_id = session.get('job_id')
            job = next((j for j in jobs if j['id'] == job_id), None) if job_id else None
            job_title = job.get('title', 'Position') if job else 'Position'
        
        # Evaluate speech with Groq AI
        evaluation = evaluate_speech_answer(
            question=question_text,
            transcript=transcript,
            duration=recording_duration,
            job_title=job_title
        )
        
        # Store in session
        if session:
            if 'speech_evaluations' not in session:
                session['speech_evaluations'] = {}
            session['speech_evaluations'][question_id] = {
                'transcript': transcript,
                'duration': recording_duration,
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            }
            interview_session_manager.save_sessions()
        
        print(f"[Speech] ✅ Evaluation Score: {evaluation.get('overall_score', 0)}%")
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        }), 200
        
    except Exception as e:
        print(f"[Speech] Error: {e}")
        return jsonify({'error': str(e)}), 500


def evaluate_speech_answer(question, transcript, duration, job_title):
    """Use Groq AI to evaluate speech transcript for behavioral questions"""
    from config.groq_config import call_groq
    
    system_prompt = """You are an expert interview evaluator assessing a candidate's verbal response.
Evaluate the speech transcript based on:

1. CLARITY (0-100): How clear and articulate is the response?
2. CONTENT (0-100): How relevant and substantive is the answer?
3. COMMUNICATION (0-100): How well does the candidate communicate their ideas?
4. STRUCTURE (0-100): Is the answer well-organized (STAR method, etc.)?

Return JSON with:
{
    "overall_score": <0-100>,
    "clarity_score": <0-100>,
    "content_score": <0-100>,
    "communication_score": <0-100>,
    "structure_score": <0-100>,
    "strengths": ["strength1", "strength2"],
    "improvements": ["improvement1", "improvement2"],
    "feedback": "<constructive feedback paragraph>"
}

Be encouraging but honest. Consider that this is a transcription so minor grammar issues are expected."""

    user_prompt = f"""Evaluate this candidate's verbal response for a {job_title} position:

QUESTION: {question}

TRANSCRIPT OF VERBAL ANSWER:
\"\"\"{transcript}\"\"\"

Recording Duration: {duration} seconds
Word Count: ~{len(transcript.split())} words

Please evaluate and return JSON only."""

    try:
        response = call_groq(user_prompt, system_prompt, max_tokens=800)
        
        # Parse JSON from response
        import json
        import re
        
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            evaluation = json.loads(json_match.group())
            return evaluation
        else:
            # Return default evaluation if parsing fails
            return {
                "overall_score": 70,
                "clarity_score": 70,
                "content_score": 70,
                "communication_score": 70,
                "structure_score": 70,
                "feedback": "Your response was recorded and evaluated. Keep practicing clear and structured communication."
            }
            
    except Exception as e:
        print(f"[Speech] Groq evaluation error: {e}")
        return {
            "overall_score": 65,
            "clarity_score": 65,
            "content_score": 65,
            "communication_score": 65,
            "feedback": f"Speech recorded successfully. Duration: {duration}s"
        }


# ======================== ADAPTIVE INTERVIEW ENDPOINTS ========================

@app.route('/api/interview/<interview_token>/generate-questions', methods=['POST'])
def generate_adaptive_questions(interview_token):
    """Generate adaptive interview questions based on job and skills"""
    try:
        data = request.json
        job_title = data.get('job_title', 'Software Engineer')
        candidate_skills = data.get('candidate_skills', [])
        interview_type = data.get('interview_type', 'behavioral')  # behavioral, technical, system_design
        
        result = adaptive_interview_manager.generate_initial_questions(
            job_title=job_title,
            candidate_skills=candidate_skills,
            interview_type=interview_type
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/follow-up-question', methods=['POST'])
def get_follow_up_question(interview_token):
    """Generate contextual follow-up question based on candidate response"""
    try:
        data = request.json
        original_question = data.get('original_question', '')
        candidate_response = data.get('candidate_response', '')
        interview_type = data.get('interview_type', 'behavioral')
        depth_level = data.get('depth_level', 1)
        
        if not original_question or not candidate_response:
            return jsonify({'error': 'Missing original_question or candidate_response'}), 400
        
        result = adaptive_interview_manager.generate_follow_up_question(
            original_question=original_question,
            candidate_response=candidate_response,
            interview_type=interview_type,
            depth_level=min(depth_level, 3)
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/assess-responses', methods=['POST'])
def assess_interview_responses(interview_token):
    """Generate skill assessment based on all responses in a phase"""
    try:
        data = request.json
        responses = data.get('responses', [])
        interview_type = data.get('interview_type', 'behavioral')
        
        if not responses:
            return jsonify({'error': 'No responses provided'}), 400
        
        result = adaptive_interview_manager.generate_skill_assessment(
            responses=responses,
            interview_type=interview_type
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/next-phase-suggestion', methods=['POST'])
def suggest_next_phase(interview_token):
    """Get recommendation for next interview phase based on performance"""
    try:
        data = request.json
        current_phase = data.get('current_phase', 'behavioral')
        candidate_performance = data.get('candidate_performance', {})
        
        result = adaptive_interview_manager.suggest_next_interview_path(
            current_phase=current_phase,
            candidate_performance=candidate_performance
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/submit-code', methods=['POST'])
def submit_coding_solution(interview_token):
    """Submit coding solution for evaluation"""
    data = request.json
    code = data.get('code')
    language = data.get('language', 'python')
    
    if not code:
        return jsonify({'error': 'No code submitted'}), 400
    
    result = interview_session_manager.submit_coding_solution(interview_token, code, language)
    
    if 'error' in result:
        return jsonify(result), 404
    
    evaluation = result.get('evaluation', {})
    
    return jsonify({
        'success': True,
        'evaluation': {
            'overall_score': evaluation.get('overall_score'),
            'passed_tests': evaluation.get('passed_tests'),
            'total_tests': evaluation.get('total_tests'),
            'code_quality_score': evaluation.get('code_quality_score'),
            'test_results': evaluation.get('test_results', [])[:3]  # Limit results
        }
    }), 200


@app.route('/api/interview/<interview_token>/complete', methods=['POST'])
def complete_interview(interview_token):
    """Complete interview and generate comprehensive AI-powered score"""
    print(f"\n[Interview Complete] Processing completion for token: {interview_token}")
    
    # Get session data
    session = interview_session_manager.get_interview_session(interview_token)
    if not session:
        return jsonify({'error': 'Interview session not found'}), 404
    
    candidate_id = session['candidate_id']
    job_id = session.get('job_id')
    
    # Get candidate and job data for context
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    job = next((j for j in jobs if j['id'] == job_id), None) if job_id else None
    
    candidate_skills = candidate.get('skills', []) if candidate else []
    job_title = job.get('title', 'Position') if job else 'Position'
    
    # Collect all responses from session
    responses = session.get('responses', {})
    
    # Format responses for AI evaluation
    formatted_responses = []
    questions = session.get('questions', {})
    
    # Process technical questions
    for q in questions.get('technical', []):
        q_id = q.get('id', '')
        answer = responses.get(q_id, '')
        if answer:
            formatted_responses.append({
                'id': q_id,
                'question': q.get('question', ''),
                'answer': answer,
                'type': 'technical',
                'skill': q.get('skill', '')
            })
    
    # Process behavioral questions
    for q in questions.get('behavioral', []):
        q_id = q.get('id', '')
        answer = responses.get(q_id, '')
        if answer:
            formatted_responses.append({
                'id': q_id,
                'question': q.get('question', ''),
                'answer': answer,
                'type': 'behavioral',
                'competency': q.get('competency', '')
            })
    
    # Process coding questions
    coding_submission = session.get('coding_submission') or {}
    for q in questions.get('coding', []):
        q_id = q.get('id', '')
        code = coding_submission.get('code', '') if coding_submission else ''
        if not code:
            code = responses.get(q_id, '') if responses else ''
        if code:
            formatted_responses.append({
                'id': q_id,
                'question': q.get('description', q.get('title', '')),
                'answer': code,
                'type': 'coding'
            })
    
    print(f"[Interview Complete] Evaluating {len(formatted_responses)} responses with AI...")
    
    # Use AI to evaluate all responses
    if formatted_responses:
        ai_evaluation = evaluate_all_responses(
            responses=formatted_responses,
            candidate_skills=candidate_skills,
            job_title=job_title
        )
    else:
        ai_evaluation = {
            'summary': {
                'overall_score': 0,
                'technical_score': 0,
                'behavioral_score': 0,
                'coding_score': 0
            },
            'recommendation': 'No Responses',
            'recommendation_detail': 'No responses were submitted for evaluation.'
        }
    
    # Get scores from AI evaluation
    overall_score = ai_evaluation.get('summary', {}).get('overall_score', 0)
    technical_score = ai_evaluation.get('summary', {}).get('technical_score', 0)
    behavioral_score = ai_evaluation.get('summary', {}).get('behavioral_score', 0)
    coding_score = ai_evaluation.get('summary', {}).get('coding_score', 0)
    recommendation = ai_evaluation.get('recommendation', 'Pending')
    
    print(f"[Interview Complete] ✅ AI Evaluation Complete:")
    print(f"[Interview Complete]   - Overall Score: {overall_score}%")
    print(f"[Interview Complete]   - Technical: {technical_score}%")
    print(f"[Interview Complete]   - Behavioral: {behavioral_score}%")
    print(f"[Interview Complete]   - Coding: {coding_score}%")
    print(f"[Interview Complete]   - Recommendation: {recommendation}")
    
    # Complete the session
    result = interview_session_manager.complete_interview(interview_token)
    
    if 'error' in result:
        return jsonify(result), 404
    
    # Determine if candidate qualifies for HR interview (score >= 80%)
    HR_INTERVIEW_THRESHOLD = 80
    qualifies_for_hr = overall_score >= HR_INTERVIEW_THRESHOLD
    
    # Update candidate with detailed interview scores
    hr_email_sent = False
    rejection_email_sent = False
    
    if candidate:
        candidate['interview_round_1']['status'] = 'completed'
        candidate['interview_round_1']['score'] = overall_score
        candidate['interview_round_1']['technical_score'] = technical_score
        candidate['interview_round_1']['behavioral_score'] = behavioral_score
        candidate['interview_round_1']['coding_score'] = coding_score
        candidate['interview_round_1']['recommendation'] = recommendation
        candidate['interview_round_1']['ai_evaluation'] = ai_evaluation
        candidate['interview_round_1']['completed_at'] = datetime.now().isoformat()
        
        # Update overall status based on score threshold (80%)
        if qualifies_for_hr:
            candidate['status'] = 'HR Interview Scheduled'
            candidate['hr_interview'] = {
                'status': 'pending',
                'scheduled_at': None,
                'invited_at': datetime.now().isoformat()
            }
            print(f"[Interview Complete] ✅ Candidate {candidate.get('name')} QUALIFIES for HR interview (Score: {overall_score}%)")
        else:
            candidate['status'] = 'Rejected - Interview'
            candidate['rejection_reason'] = f'Interview score {overall_score}% below HR threshold ({HR_INTERVIEW_THRESHOLD}%)'
            print(f"[Interview Complete] ❌ Candidate {candidate.get('name')} does NOT qualify (Score: {overall_score}%)")
        
        save_json(CANDIDATES_FILE, candidates)
        print(f"[Interview Complete] ✅ Candidate {candidate.get('name')} scores updated")
    
    # Send appropriate email based on score
    if candidate:
        try:
            if qualifies_for_hr:
                # Send HR interview invitation email
                hr_result = send_hr_interview_invitation(
                    candidate_name=candidate.get('name', 'Candidate'),
                    candidate_email=candidate.get('email'),
                    job_title=job_title,
                    interview_score=overall_score
                )
                hr_email_sent = hr_result.get('success', False)
                print(f"[Interview Complete] ✅ HR Interview invitation sent to {candidate.get('email')}: {hr_email_sent}")
            else:
                # Send rejection email
                feedback = ai_evaluation.get('recommendation_detail', '')
                rejection_result = send_interview_rejection_email(
                    candidate_name=candidate.get('name', 'Candidate'),
                    candidate_email=candidate.get('email'),
                    job_title=job_title,
                    interview_score=overall_score,
                    feedback=feedback
                )
                rejection_email_sent = rejection_result.get('success', False)
                print(f"[Interview Complete] ✅ Rejection email sent to {candidate.get('email')}: {rejection_email_sent}")
        except Exception as e:
            print(f"[Interview Complete] ⚠️ Failed to send email: {e}")
    
    return jsonify({
        'success': True,
        'session_id': result.get('session_id', session.get('session_id')),
        'interview_score': overall_score,
        'scores': {
            'overall': overall_score,
            'technical': technical_score,
            'behavioral': behavioral_score,
            'coding': coding_score
        },
        'recommendation': recommendation,
        'recommendation_detail': ai_evaluation.get('recommendation_detail', ''),
        'qualifies_for_hr_interview': qualifies_for_hr,
        'hr_email_sent': hr_email_sent,
        'rejection_email_sent': rejection_email_sent,
        'evaluations': ai_evaluation.get('evaluations', [])[:5],
        'completed_at': datetime.now().isoformat()
    }), 200


@app.route('/api/interview/<interview_token>/evaluate-answer', methods=['POST'])
def evaluate_answer_realtime(interview_token):
    """Evaluate a single answer in real-time using AI"""
    try:
        data = request.json
        question = data.get('question', '')
        answer = data.get('answer', '')
        question_type = data.get('question_type', 'technical')
        
        if not question or not answer:
            return jsonify({'error': 'Question and answer are required'}), 400
        
        # Get session for context
        session = interview_session_manager.get_interview_session(interview_token)
        candidate_skills = []
        job_title = 'Position'
        
        if session:
            candidate_id = session.get('candidate_id')
            job_id = session.get('job_id')
            
            candidate = next((c for c in candidates if c['id'] == candidate_id), None)
            job = next((j for j in jobs if j['id'] == job_id), None) if job_id else None
            
            candidate_skills = candidate.get('skills', []) if candidate else []
            job_title = job.get('title', 'Position') if job else 'Position'
        
        # Use AI to evaluate the single answer
        evaluation = evaluate_single_answer(
            question=question,
            answer=answer,
            question_type=question_type,
            candidate_skills=candidate_skills,
            job_title=job_title
        )
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        }), 200
        
    except Exception as e:
        print(f"[Evaluate Answer] Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/status', methods=['GET'])
def get_interview_status(interview_token):
    """Get interview session status"""
    session = interview_session_manager.get_interview_session(interview_token)
    
    if not session:
        return jsonify({'error': 'Interview session not found'}), 404
    
    # Get candidate data for additional context
    candidate_id = session.get('candidate_id')
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    
    return jsonify({
        'session_id': session['session_id'],
        'candidate_name': session['candidate_name'],
        'status': session['status'],
        'started_at': session['started_at'],
        'completed_at': session['completed_at'],
        'expires_at': session['expires_at'],
        'questions': session.get('questions', {}),
        'questions_answered': len(session['responses']),
        'coding_submitted': bool(session['coding_submission']),
        'interview_score': session['scores'].get('interview_score'),
        'candidate_skills': candidate.get('skills', []) if candidate else [],
        'matched_skills': session.get('questions', {}).get('matched_skills', [])
    }), 200



# ======================== ENHANCED INTERVIEW ENDPOINTS ========================

@app.route('/api/interview/<interview_token>/generate-full-interview', methods=['POST'])
def generate_full_interview(interview_token):
    """Generate complete interview with 20 behavioral + 15 technical questions"""
    try:
        data = request.json
        job_title = data.get('job_title', 'Software Engineer')
        candidate_skills = data.get('candidate_skills', [])
        
        result = enhanced_interview_manager.generate_full_interview_questions(
            job_title=job_title,
            candidate_skills=candidate_skills
        )
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/adaptive-followup', methods=['POST'])
def get_adaptive_followup(interview_token):
    """Generate adaptive follow-up question based on candidate answer"""
    try:
        data = request.json
        question = data.get('question', '')
        candidate_response = data.get('candidate_response', '')
        question_type = data.get('question_type', 'behavioral')
        
        if not question or not candidate_response:
            return jsonify({'error': 'Missing question or response'}), 400
        
        result = enhanced_interview_manager.generate_adaptive_follow_up(
            question=question,
            candidate_response=candidate_response,
            question_type=question_type
        )
        
        return jsonify({'success': True, **result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/evaluate-code-strict', methods=['POST'])
def evaluate_code_strict(interview_token):
    """Strictly evaluate submitted code using execution and AI"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'No code submitted'}), 400
            
        # Get session to find test cases
        session = interview_session_manager.get_interview_session(interview_token)
        test_cases = None
        problem_title = "Coding Problem"
        
        if session and 'questions' in session:
            # Find coding challenge in fresh questions
            coding_qs = session['questions'].get('coding', [])
            if coding_qs and isinstance(coding_qs, list):
                # Use first coding question for now
                problem = coding_qs[0]
                test_cases = problem.get('test_cases')
                problem_title = problem.get('title', 'Coding Problem')
        
        evaluation = enhanced_interview_manager.evaluate_code_strictly(
            code=code,
            problem_type=problem_title,
            language=language,
            test_cases=test_cases
        )
        
        return jsonify({
            'success': True,
            'evaluation': evaluation
        }), 200
    except Exception as e:
        print(f"[API] Error in code evaluation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/assess-phase-comprehensive', methods=['POST'])
def assess_phase_comprehensive(interview_token):
    """Comprehensive assessment of phase responses"""
    try:
        data = request.json
        responses = data.get('responses', [])
        question_type = data.get('question_type', 'behavioral')
        difficulty_distribution = data.get('difficulty_distribution', {})
        
        if not responses:
            return jsonify({'error': 'No responses provided'}), 400
        
        assessment = enhanced_interview_manager.assess_phase_comprehensive(
            responses=responses,
            question_type=question_type,
            difficulty_distribution=difficulty_distribution
        )
        
        return jsonify({
            'success': True,
            'assessment': assessment
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/interview/<interview_token>/generate-full-interview-fast', methods=['POST'])
def generate_full_interview_fast(interview_token):
    """Generate interview questions using Groq AI with ACTUAL job title and resume-extracted skills"""
    try:
        print(f'[GENERATE] Starting interview generation for {interview_token}')
        
        # Get interview session to find job_id and candidate_id
        session = interview_session_manager.get_interview_session(interview_token)
        
        if not session:
            print(f'[GENERATE] Session not found for token {interview_token}')
            return jsonify({'error': 'Session not found'}), 404
        
        print(f'[GENERATE] Found session - Job ID: {session.get("job_id")}, Candidate ID: {session.get("candidate_id")}')
        
        # ===== GET ACTUAL JOB TITLE =====
        job_title = None
        jobs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'jobs.json')
        with open(jobs_file, 'r') as f:
            jobs = json.load(f).get('jobs', [])
            for job in jobs:
                if job.get('id') == session.get('job_id'):
                    job_title = job.get('title')
                    print(f'[GENERATE] Job Title: "{job_title}"')
                    break
        
        if not job_title:
            print(f'[GENERATE] Job title not found!')
            return jsonify({'error': 'Job title not found'}), 404
        
        # ===== EXTRACT SKILLS FROM RESUME =====
        candidate_skills = []
        candidates_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'candidates.json')
        with open(candidates_file, 'r') as f:
            candidates = json.load(f).get('candidates', [])
            for candidate in candidates:
                if candidate.get('id') == session.get('candidate_id'):
                    resume_path = candidate.get('resume_path')
                    print(f'[GENERATE] Resume path: {resume_path}')
                    
                    # Convert relative path to absolute
                    if resume_path and not os.path.isabs(resume_path):
                        resume_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), resume_path)
                        print(f'[GENERATE] Absolute resume path: {resume_path}')
                    
                    if resume_path and os.path.exists(resume_path):
                        print(f'[GENERATE] Parsing resume...')
                        extracted = parser.parse_resume(resume_path)
                        
                        if extracted and 'skills' in extracted and extracted['skills']:
                            candidate_skills = extracted['skills']
                            print(f'[GENERATE] Extracted {len(candidate_skills)} skills from resume: {candidate_skills}')
                        else:
                            print(f'[GENERATE] No skills found in resume parse result, using job requirements as fallback')
                    else:
                        print(f'[GENERATE] Resume file not found: {resume_path}')
                    break
        
        # ===== FALLBACK: Use job requirements if resume skills not found =====
        if not candidate_skills:
            print(f'[GENERATE] Resume parsing failed, trying job requirements...')
            jobs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'jobs.json')
            try:
                with open(jobs_file, 'r') as f:
                    jobs = json.load(f).get('jobs', [])
                    for job in jobs:
                        if job.get('id') == session.get('job_id'):
                            # Get skills from job requirements
                            must_have = job.get('requirements', {}).get('must_have', job.get('must_have_skills', '').split(', '))
                            good_to_have = job.get('requirements', {}).get('good_to_have', job.get('good_to_have_skills', '').split(', '))
                            candidate_skills = must_have + good_to_have
                            candidate_skills = [s.strip() for s in candidate_skills if s.strip()]
                            if candidate_skills:
                                print(f'[GENERATE] Using job requirements: {candidate_skills}')
                                break
            except Exception as e:
                print(f'[GENERATE] Could not extract job requirements: {e}')
        
        # ===== FINAL FALLBACK: Generate generic skills from job title =====
        if not candidate_skills:
            print(f'[GENERATE] Job requirements not found, generating generic skills from job title...')
            # Extract keywords from job title to create generic skills
            job_title_lower = job_title.lower()
            generic_skills = []
            
            # Common skill mappings
            skill_keywords = {
                'python': ['Python', 'Backend Development', 'APIs', 'Databases', 'Problem Solving'],
                'javascript': ['JavaScript', 'Frontend Development', 'React', 'Web Development', 'UI/UX'],
                'java': ['Java', 'Enterprise Development', 'Spring Boot', 'Backend', 'Microservices'],
                'react': ['React', 'Frontend', 'JavaScript', 'State Management', 'Component Design'],
                'developer': ['Programming', 'Problem Solving', 'Code Quality', 'Testing', 'Debugging'],
                'engineer': ['Software Engineering', 'System Design', 'Architecture', 'Optimization', 'Performance'],
                'devops': ['DevOps', 'CI/CD', 'Cloud Infrastructure', 'Automation', 'Monitoring'],
                'data': ['Data Analysis', 'SQL', 'Machine Learning', 'Statistics', 'Database Design'],
                'fullstack': ['Full-Stack Development', 'Frontend', 'Backend', 'Databases', 'APIs'],
            }
            
            for keyword, skills in skill_keywords.items():
                if keyword in job_title_lower:
                    generic_skills.extend(skills)
            
            # If no specific match, use generic developer skills
            if not generic_skills:
                generic_skills = ['Programming', 'Problem Solving', 'Software Design', 'Testing', 'Communication']
            
            candidate_skills = list(set(generic_skills))  # Remove duplicates
            print(f'[GENERATE] Generated generic skills from job title: {candidate_skills}')
        
        # ===== CALL GROQ WITH ACTUAL DATA =====
        print(f'[GENERATE] Calling Groq with: Job="{job_title}", Skills={candidate_skills}')
        result = enhanced_interview_manager.generate_full_interview_questions(
            job_title=job_title,
            candidate_skills=candidate_skills
        )
        
        print(f'[GENERATE] Successfully generated questions from Groq')
        
        # Format response to match frontend expectations
        # Flatten questions from nested structure (easy/medium/hard) to flat list
        questions = []
        
        interview_data = result.get('interview', {})
        
        # Add behavioral questions
        behavioral = interview_data.get('behavioral', {})
        if isinstance(behavioral, dict):
            behavioral_questions = behavioral.get('questions', [])
            questions.extend(behavioral_questions)
        
        # Add technical questions
        technical = interview_data.get('technical', {})
        if isinstance(technical, dict):
            technical_questions = technical.get('questions', [])
            questions.extend(technical_questions)
        
        # Add coding questions
        coding = interview_data.get('coding', {})
        if isinstance(coding, dict):
            coding_questions = coding.get('questions', [])
            if coding_questions:
                questions.extend(coding_questions)
            elif 'medium' in coding:
                # Old format - coding structured by difficulty
                for difficulty in ['easy', 'medium', 'hard']:
                    qs = coding.get(difficulty, [])
                    questions.extend(qs)
            else:
                # Single coding problem
                questions.append(coding)
        
        print(f'[GENERATE] Total questions flattened: {len(questions)}')
        if len(questions) > 0:
            print(f'[GENERATE] Questions successfully generated and flattened')
        else:
            print(f'[GENERATE] No questions extracted from Groq responses')
        
        return jsonify({
            'success': True,
            'questions': questions,
            'job_title': job_title,
            'candidate_skills': candidate_skills
        }), 200
    except Exception as e:
        print(f'[ERROR] Failed to generate interview: {str(e)}')
        import traceback
        traceback.print_exc()
        # Return fallback questions if Groq fails
        fallback_questions = [
            {'id': 1, 'question': 'Explain the difference between REST and GraphQL', 'difficulty': 'Easy', 'type': 'technical'},
            {'id': 2, 'question': 'What are the benefits of microservices architecture?', 'difficulty': 'Easy', 'type': 'technical'},
            {'id': 3, 'question': 'How do you optimize database queries?', 'difficulty': 'Easy', 'type': 'technical'},
            {'id': 4, 'question': 'Explain async/await in JavaScript', 'difficulty': 'Easy', 'type': 'technical'},
            {'id': 5, 'question': 'What is the difference between let and const?', 'difficulty': 'Easy', 'type': 'technical'},
            {'id': 6, 'question': 'Explain the event loop in Node.js', 'difficulty': 'Easy', 'type': 'technical'},
            {'id': 7, 'question': 'How would you design a caching system?', 'difficulty': 'Medium', 'type': 'technical'},
            {'id': 8, 'question': 'Explain the CAP theorem and trade-offs', 'difficulty': 'Medium', 'type': 'technical'},
            {'id': 9, 'question': 'How do you handle race conditions?', 'difficulty': 'Medium', 'type': 'technical'},
            {'id': 10, 'question': 'Design a distributed rate limiting system', 'difficulty': 'Medium', 'type': 'technical'},
            {'id': 11, 'question': 'Explain database replication and consistency', 'difficulty': 'Medium', 'type': 'technical'},
            {'id': 12, 'question': 'How would you scale a system to handle 1M requests/sec?', 'difficulty': 'Hard', 'type': 'technical'},
            {'id': 13, 'question': 'Design a real-time notification system', 'difficulty': 'Hard', 'type': 'technical'},
            {'id': 14, 'question': 'How do you handle distributed transactions?', 'difficulty': 'Hard', 'type': 'technical'},
            {'id': 15, 'question': 'Explain eventual consistency and how to implement it', 'difficulty': 'Hard', 'type': 'technical'},
            {'id': 1, 'question': 'Tell me about yourself and your professional background', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 2, 'question': 'What are your strengths and how do they apply to this role?', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 3, 'question': 'Describe your approach to learning new technologies', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 4, 'question': 'How do you stay updated with industry trends?', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 5, 'question': 'Tell us about a project you are proud of', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 6, 'question': 'How do you handle pressure and tight deadlines?', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 7, 'question': 'Describe your communication style when working with teams', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 8, 'question': 'What motivates you in your professional work?', 'difficulty': 'Easy', 'type': 'behavioral'},
            {'id': 9, 'question': 'Tell me about a time you resolved a conflict with a colleague', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 10, 'question': 'Describe a situation where you had to make a tough decision', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 11, 'question': 'Give an example of when you took initiative on a project', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 12, 'question': 'How do you handle feedback and criticism?', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 13, 'question': 'Tell me about a time you failed and what you learned', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 14, 'question': 'Describe your experience working with diverse teams', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 15, 'question': 'How do you prioritize multiple competing tasks?', 'difficulty': 'Medium', 'type': 'behavioral'},
            {'id': 16, 'question': 'Tell me about your leadership experience and style', 'difficulty': 'Hard', 'type': 'behavioral'},
            {'id': 17, 'question': 'Describe a complex problem you solved and your approach', 'difficulty': 'Hard', 'type': 'behavioral'},
            {'id': 18, 'question': 'How do you mentor and develop other team members?', 'difficulty': 'Hard', 'type': 'behavioral'},
            {'id': 19, 'question': 'Tell me about a time you had to change strategy mid-project', 'difficulty': 'Hard', 'type': 'behavioral'},
            {'id': 20, 'question': 'How do you see your career developing over the next 5 years?', 'difficulty': 'Hard', 'type': 'behavioral'},
            {'id': 1, 'question': 'Write a function that reverses a string', 'difficulty': 'Easy', 'type': 'coding'},
        ]
        return jsonify({
            'success': True,
            'questions': fallback_questions
        }), 200


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)


