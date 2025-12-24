"""
LinkedIn Job Sharing Routes
Handles posting jobs to LinkedIn via share/redirect/mock
"""

from flask import Blueprint, request, jsonify
import requests
import json
from datetime import datetime
from config.linkedin_config import LINKEDIN_CONFIG, get_linkedin_mode
from config.groq_config import generate_linkedin_post as groq_generate_post
from routes.linkedin_auth import get_user_access_token, user_profiles

linkedin_share_bp = Blueprint('linkedin_share', __name__)

# Track shared posts
shared_posts = {}

def generate_ai_linkedin_post(job_data: dict) -> str:
    """Generate an AI-powered LinkedIn job post using Groq"""
    # Try Groq AI first
    try:
        ai_post = groq_generate_post(job_data)
        if ai_post and len(ai_post) > 50:
            return ai_post
    except Exception as e:
        print(f"[LinkedIn] Groq AI failed, using fallback: {e}")
    
    # Fallback to simple template
    title = job_data.get('title', 'Position')
    location = job_data.get('location', 'Remote')
    description = job_data.get('description', '')[:150]
    must_have = job_data.get('requirements', {}).get('must_have', [])
    experience = job_data.get('experience_required', 'Experience required')
    application_url = job_data.get('application_url', '')
    
    post = f"""🚀 We're Hiring: {title}!

📍 {location} | 💼 {experience}

{description}...

🔑 Skills: {', '.join(must_have[:4])}

👉 Apply: {application_url}

#Hiring #NowHiring #{title.replace(' ', '')} #Careers"""
    
    return post


@linkedin_share_bp.route('/api/linkedin/share/job', methods=['POST'])
def share_job_to_linkedin():
    """Share a job posting to LinkedIn"""
    session_token = request.headers.get('X-LinkedIn-Session')
    data = request.json
    job_data = data.get('job_data', {})
    
    mode = get_linkedin_mode()
    
    # Generate AI post content
    post_content = generate_ai_linkedin_post(job_data)
    job_id = job_data.get('id', f"JOB_{datetime.now().timestamp()}")
    
    if mode == 'MOCK':
        # Mock mode - simulate LinkedIn API response
        return mock_share_job(job_id, post_content, job_data)
    
    elif mode == 'REDIRECT':
        # Redirect mode - return URL for manual posting
        return redirect_share_job(job_id, post_content, job_data)
    
    elif mode == 'API':
        # Real API mode - post to LinkedIn
        access_token = get_user_access_token(session_token)
        if not access_token:
            return jsonify({
                'error': 'Not connected to LinkedIn. Please login first.',
                'fallback': 'REDIRECT'
            }), 401
        
        return api_share_job(access_token, session_token, job_id, post_content, job_data)
    
    return jsonify({'error': 'Invalid LinkedIn mode'}), 400


def mock_share_job(job_id: str, post_content: str, job_data: dict):
    """Mock LinkedIn share - simulates API behavior"""
    mock_post_id = f"urn:li:share:MOCK_{int(datetime.now().timestamp())}"
    
    result = {
        'success': True,
        'mode': 'MOCK',
        'platform': 'LINKEDIN',
        'post_id': mock_post_id,
        'job_id': job_id,
        'status': 'PUBLISHED',
        'post_content': post_content,
        'published_at': datetime.now().isoformat(),
        'message': '✅ This is a MOCK post - simulates LinkedIn API behavior.',
        'mock_url': f'https://linkedin.com/feed/update/{mock_post_id}'
    }
    
    # Store for tracking
    shared_posts[job_id] = result
    
    return jsonify(result)


def redirect_share_job(job_id: str, post_content: str, job_data: dict):
    """Redirect mode - provide URL for manual LinkedIn posting"""
    # LinkedIn share URL with pre-filled text
    import urllib.parse
    encoded_text = urllib.parse.quote(post_content)
    
    # LinkedIn share/post composer URL (works for all users)
    share_url = "https://www.linkedin.com/feed/?shareActive=true"
    
    # Free LinkedIn job posting URL (available to all users)
    job_post_url = "https://www.linkedin.com/jobs/post/"
    
    result = {
        'success': True,
        'mode': 'REDIRECT',
        'platform': 'LINKEDIN',
        'job_id': job_id,
        'status': 'REDIRECT_READY',
        'post_content': post_content,
        'share_url': share_url,
        'job_post_url': job_post_url,
        'message': '📤 Click the button to post on LinkedIn manually.',
        'instructions': [
            '1. Click "Post on LinkedIn" button',
            '2. The post content has been copied to clipboard',
            '3. Paste and customize your post',
            '4. Publish on LinkedIn'
        ]
    }
    
    # Track internally
    shared_posts[job_id] = {
        **result,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify(result)


def api_share_job(access_token: str, session_token: str, job_id: str, post_content: str, job_data: dict):
    """Real LinkedIn API share - posts to user's feed"""
    try:
        # Get user's LinkedIn ID (person URN)
        profile = user_profiles.get(session_token, {})
        person_id = profile.get('id')
        
        if not person_id:
            return jsonify({'error': 'User profile not found'}), 400
        
        # UGC Post payload for LinkedIn API v2
        payload = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.post(
            LINKEDIN_CONFIG['share_url'],
            json=payload,
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            post_data = response.json()
            post_id = post_data.get('id', f"urn:li:share:{int(datetime.now().timestamp())}")
            
            result = {
                'success': True,
                'mode': 'API',
                'platform': 'LINKEDIN',
                'post_id': post_id,
                'job_id': job_id,
                'status': 'PUBLISHED',
                'post_content': post_content,
                'published_at': datetime.now().isoformat(),
                'message': '✅ Job posted to LinkedIn successfully!',
                'linkedin_url': f'https://linkedin.com/feed/update/{post_id}'
            }
            
            shared_posts[job_id] = result
            return jsonify(result)
        
        else:
            # API failed, fallback to redirect mode
            return jsonify({
                'error': f'LinkedIn API error: {response.status_code}',
                'details': response.text,
                'fallback': 'REDIRECT',
                'post_content': post_content
            }), 400
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'fallback': 'REDIRECT',
            'post_content': post_content
        }), 500


@linkedin_share_bp.route('/api/linkedin/share/status/<job_id>', methods=['GET'])
def get_share_status(job_id: str):
    """Get LinkedIn share status for a job"""
    if job_id in shared_posts:
        return jsonify(shared_posts[job_id])
    
    return jsonify({
        'job_id': job_id,
        'status': 'NOT_SHARED',
        'platform': 'LINKEDIN'
    })


@linkedin_share_bp.route('/api/linkedin/posts', methods=['GET'])
def get_all_shared_posts():
    """Get all LinkedIn shared posts"""
    return jsonify({
        'posts': list(shared_posts.values()),
        'total': len(shared_posts)
    })


@linkedin_share_bp.route('/api/linkedin/generate-post', methods=['POST'])
def generate_post_preview():
    """Generate AI post preview without sharing"""
    job_data = request.json
    post_content = generate_ai_linkedin_post(job_data)
    
    return jsonify({
        'success': True,
        'post_content': post_content,
        'character_count': len(post_content)
    })


@linkedin_share_bp.route('/api/mock/linkedin/jobs', methods=['POST'])
def mock_linkedin_jobs():
    """Mock LinkedIn Jobs API - for enterprise demo"""
    job_data = request.json
    
    mock_job_urn = f"urn:li:jobPosting:MOCK_{int(datetime.now().timestamp())}"
    
    return jsonify({
        'jobUrn': mock_job_urn,
        'status': 'PUBLISHED',
        'mode': 'MOCK',
        'message': 'This is a mock service that simulates LinkedIn\'s real API behavior.',
        'job_data': job_data,
        'created_at': datetime.now().isoformat()
    })


@linkedin_share_bp.route('/api/linkedin/mode', methods=['GET', 'POST'])
def linkedin_mode():
    """Get or set LinkedIn integration mode"""
    from config.linkedin_config import set_linkedin_mode, get_linkedin_mode
    
    if request.method == 'GET':
        return jsonify({'mode': get_linkedin_mode()})
    
    mode = request.json.get('mode')
    if set_linkedin_mode(mode):
        return jsonify({'success': True, 'mode': mode})
    
    return jsonify({'error': 'Invalid mode. Use MOCK, REDIRECT, or API'}), 400


@linkedin_share_bp.route('/api/linkedin/auto-post', methods=['POST'])
def auto_post_to_linkedin():
    """
    Automatically post job to LinkedIn when job is created.
    This endpoint is called right after job creation.
    """
    session_token = request.headers.get('X-LinkedIn-Session')
    data = request.json
    job_data = data.get('job_data', {})
    
    # Ensure application URL is included
    if not job_data.get('application_url'):
        job_id = job_data.get('id', '')
        job_data['application_url'] = f"http://localhost:3001/apply/{job_id}"
    
    # Generate the elaborate post content
    post_content = generate_ai_linkedin_post(job_data)
    job_id = job_data.get('id', f"JOB_{datetime.now().timestamp()}")
    
    # Check if user is connected to LinkedIn
    access_token = get_user_access_token(session_token) if session_token else None
    
    if access_token:
        # User is logged in - attempt real API post
        try:
            profile = user_profiles.get(session_token, {})
            person_id = profile.get('id')
            
            if person_id:
                # UGC Post payload for LinkedIn API v2
                payload = {
                    "author": f"urn:li:person:{person_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {
                                "text": post_content
                            },
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {
                        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
                
                response = requests.post(
                    LINKEDIN_CONFIG['share_url'],
                    json=payload,
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    post_data = response.json()
                    post_id = post_data.get('id', f"urn:li:share:{int(datetime.now().timestamp())}")
                    
                    result = {
                        'success': True,
                        'auto_posted': True,
                        'mode': 'API',
                        'platform': 'LINKEDIN',
                        'post_id': post_id,
                        'job_id': job_id,
                        'status': 'PUBLISHED',
                        'post_content': post_content,
                        'published_at': datetime.now().isoformat(),
                        'message': '✅ Job automatically posted to LinkedIn!',
                        'linkedin_url': f'https://linkedin.com/feed/update/{post_id}'
                    }
                    
                    shared_posts[job_id] = result
                    return jsonify(result)
        except Exception as e:
            print(f"LinkedIn API error: {e}")
    
    # If not logged in or API fails, return content for manual posting
    result = {
        'success': True,
        'auto_posted': False,
        'mode': 'MANUAL',
        'platform': 'LINKEDIN',
        'job_id': job_id,
        'status': 'READY_TO_POST',
        'post_content': post_content,
        'share_url': 'https://www.linkedin.com/feed/?shareActive=true',
        'message': '📋 Post content ready! Click to share on LinkedIn.',
        'instructions': 'Content copied to clipboard. Open LinkedIn and paste to post.'
    }
    
    shared_posts[job_id] = result
    return jsonify(result)

