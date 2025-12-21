from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import random
from datetime import datetime, timedelta
from models.resume_parser import ResumeParser
from models.skill_matcher import SkillMatcher
from models.ai_recommendations import (
    candidate_scorer, salary_recommender, 
    interview_panel_recommender, assessment_recommender
)
from config.api_integrations import integration_manager

app = Flask(__name__)
CORS(app)

# Initialize models
parser = ResumeParser()
matcher = SkillMatcher()

# Mock databases (in real app, use PostgreSQL)
CANDIDATES_FILE = 'data/candidates.json'
JOBS_FILE = 'data/jobs.json'

# Ensure data directory exists
os.makedirs('data/resumes', exist_ok=True)

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
    
    return jsonify({
        'message': 'Application submitted successfully',
        'candidate': candidate
    }), 201

@app.route('/api/candidates', methods=['GET'])
def get_candidates():
    """Get all candidates with optional filtering"""
    job_id = request.args.get('job_id')
    
    if job_id:
        filtered = [c for c in candidates if c['job_id'] == job_id]
        return jsonify(filtered), 200
    
    return jsonify(candidates), 200

@app.route('/api/candidates/<candidate_id>', methods=['GET', 'PUT'])
def handle_candidate(candidate_id):
    """Get or update candidate details"""
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    if request.method == 'PUT':
        updates = request.json
        candidate.update(updates)
        save_json(CANDIDATES_FILE, candidates)
        return jsonify(candidate), 200
    
    return jsonify(candidate), 200

# ======================== PHASE 1: CANDIDATE SCREENING ========================

@app.route('/api/candidates/<candidate_id>/score', methods=['GET'])
def get_candidate_score(candidate_id):
    """Get AI-generated candidate score"""
    job_id = request.args.get('job_id', 'JOB1')
    
    candidate = next((c for c in candidates if c['id'] == candidate_id), None)
    if not candidate:
        return jsonify({'error': 'Candidate not found'}), 404
    
    # Use AI scorer
    score = candidate_scorer.score_candidate(candidate, jobs[0] if jobs else {})
    
    # Update candidate
    candidate['score'] = score['overall_score']
    candidate['category'] = score['category']
    candidate['skill_gaps'] = score.get('skill_gaps', [])
    save_json(CANDIDATES_FILE, candidates)
    
    # Send email notification
    integration_manager.send_grid.send_email(
        to=candidate['email'],
        subject='Screening Assessment Result',
        template='screening_result',
        data={'candidate_name': candidate['name'], 'score': score['overall_score'], 'category': score['category']}
    )
    
    return jsonify(score), 200

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
    <h2>Interview Scheduled!</h2>
    <p>Hi {candidate.get('name')},</p>
    <p>Great news! Your interview is scheduled for <strong>{available_slots[0]['start'] if available_slots else 'TBD'}</strong></p>
    <p><strong>Interview Details:</strong></p>
    <ul>
        <li>Round 1: Technical (1 hour) - {panel_recommendation['recommended_panel'][0].get('name') if panel_recommendation.get('recommended_panel') else 'TBD'}</li>
        <li>Round 2: System Design (1 hour) - {panel_recommendation['recommended_panel'][1].get('name') if len(panel_recommendation.get('recommended_panel', [])) > 1 else 'TBD'}</li>
        <li>Round 3: Cultural Fit (30 min) - {panel_recommendation['recommended_panel'][2].get('name') if len(panel_recommendation.get('recommended_panel', [])) > 2 else 'TBD'}</li>
    </ul>
    <p><a href="https://zoom.us/j/xyz123">Join Zoom Meeting</a></p>
    <p><a href="http://localhost:3000">Confirm Availability</a></p>
    """
    integration_manager.send_notification(candidate, 'interview_scheduled', email_template)
    
    return jsonify({
        'success': True,
        'interview_scheduled': True,
        'scheduled_time': available_slots[0]['start'] if available_slots else None,
        'interview_panel': panel_recommendation['recommended_panel'],
        'zoom_link': 'https://zoom.us/j/xyz123',
        'available_slots': available_slots[:3]
    }), 200

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
