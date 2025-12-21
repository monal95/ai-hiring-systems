"""
API Integration Configuration and Manager
Handles all external API calls to job boards, calendars, assessment platforms, etc.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from abc import ABC, abstractmethod

# ======================== JOB BOARD INTEGRATIONS ========================

class JobBoardAPI(ABC):
    """Base class for job board APIs"""
    
    @abstractmethod
    def post_job(self, job_data: Dict) -> Dict:
        """Post job to platform"""
        pass
    
    @abstractmethod
    def get_job_metrics(self, job_id: str) -> Dict:
        """Get views, applications, etc"""
        pass


class LinkedInAPI(JobBoardAPI):
    """LinkedIn Talent Solutions API"""
    
    def __init__(self):
        self.api_key = os.getenv('LINKEDIN_API_KEY', 'demo-key')
        self.base_url = 'https://api.linkedin.com/v2'
    
    def post_job(self, job_data: Dict) -> Dict:
        """Post job to LinkedIn"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'title': job_data['title'],
                'description': job_data['description'],
                'location': job_data['location'],
                'experience_level': self._map_experience(job_data['experience_required']),
                'job_functions': ['Engineering'],
                'employment_type': 'FULL_TIME'
            }
            
            # Mock response for demo
            return {
                'success': True,
                'platform': 'linkedin',
                'job_url': f'https://linkedin.com/jobs/view/JOB{job_data.get("id", "1")}',
                'posted_at': datetime.now().isoformat(),
                'status': 'published'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_job_metrics(self, job_id: str) -> Dict:
        """Get LinkedIn job metrics"""
        # Mock data - in production, fetch from LinkedIn API
        return {
            'platform': 'linkedin',
            'views': 347,
            'applications': 23,
            'clicks': 45
        }
    
    def _map_experience(self, exp_range: str) -> str:
        """Map experience range to LinkedIn level"""
        years = int(exp_range.split('-')[0])
        if years < 2:
            return 'ENTRY_LEVEL'
        elif years < 5:
            return 'MID_LEVEL'
        else:
            return 'SENIOR'


class IndeedAPI(JobBoardAPI):
    """Indeed API"""
    
    def __init__(self):
        self.api_key = os.getenv('INDEED_API_KEY', 'demo-key')
        self.base_url = 'https://api.indeed.com/v2'
    
    def post_job(self, job_data: Dict) -> Dict:
        """Post job to Indeed"""
        try:
            payload = {
                'title': job_data['title'],
                'description': job_data['description'],
                'location': job_data['location'],
                'job_type': 'full time',
                'company_name': os.getenv('COMPANY_NAME', 'My Company')
            }
            
            # Mock response
            return {
                'success': True,
                'platform': 'indeed',
                'job_url': f'https://indeed.com/jobs?jk=JOB{job_data.get("id", "1")}',
                'posted_at': datetime.now().isoformat(),
                'status': 'published'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_job_metrics(self, job_id: str) -> Dict:
        """Get Indeed job metrics"""
        return {
            'platform': 'indeed',
            'views': 189,
            'applications': 15,
            'clicks': 28
        }


class NaukriAPI(JobBoardAPI):
    """Naukri Job Posting API"""
    
    def __init__(self):
        self.api_key = os.getenv('NAUKRI_API_KEY', 'demo-key')
        self.base_url = 'https://api.naukri.com/v1'
    
    def post_job(self, job_data: Dict) -> Dict:
        """Post job to Naukri"""
        try:
            payload = {
                'title': job_data['title'],
                'description': job_data['description'],
                'location': job_data['location'],
                'skills': job_data.get('requirements', {}).get('must_have', []),
                'experience_min': int(job_data['experience_required'].split('-')[0]),
                'experience_max': int(job_data['experience_required'].split('-')[1])
            }
            
            # Mock response
            return {
                'success': True,
                'platform': 'naukri',
                'job_url': f'https://naukri.com/job-listings-JOB{job_data.get("id", "1")}',
                'posted_at': datetime.now().isoformat(),
                'status': 'published'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_job_metrics(self, job_id: str) -> Dict:
        """Get Naukri job metrics"""
        return {
            'platform': 'naukri',
            'views': 256,
            'applications': 31,
            'clicks': 38
        }


# ======================== CALENDAR INTEGRATIONS ========================

class CalendarAPI(ABC):
    """Base class for calendar APIs"""
    
    @abstractmethod
    def get_free_slots(self, organizer_email: str, duration_minutes: int) -> List[Dict]:
        """Get available time slots"""
        pass
    
    @abstractmethod
    def create_event(self, event_data: Dict) -> Dict:
        """Create calendar event"""
        pass


class GoogleCalendarAPI(CalendarAPI):
    """Google Calendar API"""
    
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_CALENDAR_API_KEY', 'demo-key')
    
    def get_free_slots(self, organizer_email: str, duration_minutes: int = 60) -> List[Dict]:
        """Get free slots for next 7 days"""
        # Mock response - returns 3 time slots
        today = datetime.now().date()
        slots = []
        
        for day_offset in range(1, 4):
            future_date = today + timedelta(days=day_offset)
            
            slots.append({
                'start': f"{future_date.isoformat()}T10:00:00",
                'end': f"{future_date.isoformat()}T11:00:00",
                'available': True
            })
            
            slots.append({
                'start': f"{future_date.isoformat()}T14:00:00",
                'end': f"{future_date.isoformat()}T15:00:00",
                'available': True
            })
        
        return slots
    
    def create_event(self, event_data: Dict) -> Dict:
        """Create Google Calendar event"""
        try:
            payload = {
                'summary': event_data['title'],
                'description': event_data['description'],
                'start': {'dateTime': event_data['start_time']},
                'end': {'dateTime': event_data['end_time']},
                'attendees': [{'email': email} for email in event_data.get('attendees', [])]
            }
            
            # Mock response
            return {
                'success': True,
                'event_id': f"EVENT{datetime.now().timestamp()}",
                'calendar_link': 'https://calendar.google.com/calendar/u/0/r/eventedit',
                'status': 'created'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class OutlookAPI(CalendarAPI):
    """Microsoft Outlook/Office 365 API"""
    
    def __init__(self):
        self.api_key = os.getenv('OUTLOOK_API_KEY', 'demo-key')
    
    def get_free_slots(self, organizer_email: str, duration_minutes: int = 60) -> List[Dict]:
        """Get free slots from Outlook calendar"""
        # Mock response
        today = datetime.now().date()
        slots = []
        
        for day_offset in [1, 2, 3]:
            future_date = today + timedelta(days=day_offset)
            slots.append({
                'start': f"{future_date.isoformat()}T09:00:00",
                'end': f"{future_date.isoformat()}T10:00:00",
                'available': True
            })
        
        return slots
    
    def create_event(self, event_data: Dict) -> Dict:
        """Create Outlook event"""
        return {
            'success': True,
            'event_id': f"OUTLOOK_EVENT{datetime.now().timestamp()}",
            'status': 'created'
        }


# ======================== ASSESSMENT PLATFORMS ========================

class AssessmentAPI(ABC):
    """Base class for assessment platforms"""
    
    @abstractmethod
    def create_assessment(self, assessment_data: Dict) -> Dict:
        """Create and send assessment"""
        pass
    
    @abstractmethod
    def get_assessment_score(self, assessment_id: str) -> Dict:
        """Get assessment results"""
        pass


class HackerRankAPI(AssessmentAPI):
    """HackerRank API for coding assessments"""
    
    def __init__(self):
        self.api_key = os.getenv('HACKERRANK_API_KEY', 'demo-key')
        self.base_url = 'https://api.hackerrank.com/v1'
    
    def create_assessment(self, assessment_data: Dict) -> Dict:
        """Send HackerRank test"""
        try:
            payload = {
                'test_id': 'python-intermediate',
                'candidate_email': assessment_data['candidate_email'],
                'candidate_name': assessment_data['candidate_name'],
                'duration_minutes': 120,
                'languages': ['python', 'sql']
            }
            
            # Mock response
            return {
                'success': True,
                'platform': 'hackerrank',
                'assessment_id': f"HR{datetime.now().timestamp()}",
                'invite_link': 'https://www.hackerrank.com/test/invite/xyz123',
                'status': 'sent',
                'expires_in_days': 7
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_assessment_score(self, assessment_id: str) -> Dict:
        """Get HackerRank test score"""
        # Mock score
        return {
            'success': True,
            'platform': 'hackerrank',
            'assessment_id': assessment_id,
            'score': 78,
            'total': 100,
            'status': 'completed',
            'submitted_at': datetime.now().isoformat(),
            'details': {
                'coding_test': 75,
                'logic': 80,
                'problem_solving': 78
            }
        }


class CodilityAPI(AssessmentAPI):
    """Codility API for technical assessments"""
    
    def __init__(self):
        self.api_key = os.getenv('CODILITY_API_KEY', 'demo-key')
    
    def create_assessment(self, assessment_data: Dict) -> Dict:
        """Send Codility test"""
        return {
            'success': True,
            'platform': 'codility',
            'assessment_id': f"COD{datetime.now().timestamp()}",
            'invite_link': 'https://codility.com/candidates/xyz123',
            'status': 'sent'
        }
    
    def get_assessment_score(self, assessment_id: str) -> Dict:
        """Get Codility score"""
        return {
            'success': True,
            'score': 82,
            'percentile': 65,
            'status': 'completed'
        }


# ======================== EMAIL & COMMUNICATION ========================

class EmailServiceAPI(ABC):
    """Base class for email services"""
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict:
        """Send email"""
        pass


class SendGridAPI(EmailServiceAPI):
    """SendGrid Email API"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY', 'demo-key')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@company.com')
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> Dict:
        """Send email via SendGrid"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'personalizations': [{'to': [{'email': to}]}],
                'from': {'email': self.from_email},
                'subject': subject,
                'content': [{'type': 'text/html' if html else 'text/plain', 'value': body}]
            }
            
            # Mock response
            return {
                'success': True,
                'message_id': f"SG{datetime.now().timestamp()}",
                'status': 'sent'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TwilioAPI:
    """Twilio SMS API"""
    
    def __init__(self):
        self.api_key = os.getenv('TWILIO_API_KEY', 'demo-key')
        self.phone_number = os.getenv('TWILIO_PHONE', '+1234567890')
    
    def send_sms(self, phone: str, message: str) -> Dict:
        """Send SMS notification"""
        try:
            # Mock response
            return {
                'success': True,
                'message_id': f"SMS{datetime.now().timestamp()}",
                'status': 'sent',
                'phone': phone
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# ======================== E-SIGNATURE ========================

class DocuSignAPI:
    """DocuSign E-Signature API"""
    
    def __init__(self):
        self.api_key = os.getenv('DOCUSIGN_API_KEY', 'demo-key')
        self.account_id = os.getenv('DOCUSIGN_ACCOUNT_ID', 'demo-account')
    
    def send_for_signature(self, offer_data: Dict) -> Dict:
        """Send offer letter for e-signature"""
        try:
            payload = {
                'document_name': f"Offer_Letter_{offer_data['candidate_name']}",
                'recipient_email': offer_data['candidate_email'],
                'recipient_name': offer_data['candidate_name'],
                'document_content': self._generate_offer_document(offer_data)
            }
            
            # Mock response
            return {
                'success': True,
                'envelope_id': f"ENV{datetime.now().timestamp()}",
                'signing_link': 'https://na3.docusign.net/signing?token=xyz123',
                'status': 'sent',
                'expires_in_days': 30
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def check_signature_status(self, envelope_id: str) -> Dict:
        """Check if document has been signed"""
        # Mock response
        return {
            'envelope_id': envelope_id,
            'status': 'completed',
            'signed_at': datetime.now().isoformat(),
            'signer_email': 'candidate@example.com'
        }
    
    def _generate_offer_document(self, offer_data: Dict) -> str:
        """Generate offer letter HTML"""
        return f"""
        <html>
            <body>
                <h1>Offer Letter</h1>
                <p>Dear {offer_data.get('candidate_name')},</p>
                <p>We are pleased to offer you the position of <strong>{offer_data.get('position')}</strong></p>
                <p><strong>Salary:</strong> ₹{offer_data.get('salary')} LPA</p>
                <p><strong>Joining Date:</strong> {offer_data.get('joining_date')}</p>
                <p>Best regards,<br/>Talent Team</p>
            </body>
        </html>
        """


# ======================== ENTERPRISE SYSTEMS ========================

class SuccessFactorsAPI:
    """SAP SuccessFactors HRIS API"""
    
    def __init__(self):
        self.api_key = os.getenv('SUCCESSFACTORS_API_KEY', 'demo-key')
        self.instance = os.getenv('SUCCESSFACTORS_INSTANCE', 'demo')
    
    def create_employee(self, employee_data: Dict) -> Dict:
        """Create employee record in SuccessFactors"""
        try:
            payload = {
                'firstName': employee_data.get('first_name'),
                'lastName': employee_data.get('last_name'),
                'email': employee_data.get('email'),
                'jobTitle': employee_data.get('position'),
                'department': employee_data.get('department'),
                'startDate': employee_data.get('joining_date'),
                'salary': employee_data.get('salary')
            }
            
            # Mock response
            return {
                'success': True,
                'employee_id': f"EMP{datetime.now().timestamp()}",
                'status': 'created'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_benefits(self, employee_id: str, benefits_data: Dict) -> Dict:
        """Sync benefits enrollment"""
        return {
            'success': True,
            'employee_id': employee_id,
            'benefits_synced': True
        }


class ServiceNowAPI:
    """ServiceNow IT Service Management API"""
    
    def __init__(self):
        self.api_key = os.getenv('SERVICENOW_API_KEY', 'demo-key')
        self.instance = os.getenv('SERVICENOW_INSTANCE', 'demo')
    
    def create_it_ticket(self, ticket_data: Dict) -> Dict:
        """Create IT provisioning ticket"""
        try:
            payload = {
                'short_description': ticket_data.get('description'),
                'description': f"Provision for new hire: {ticket_data.get('employee_name')}",
                'priority': 'high',
                'assignment_group': 'IT Hardware',
                'type': 'New Hardware',
                'cmdb_ci': 'Laptop'
            }
            
            # Mock response
            return {
                'success': True,
                'ticket_id': f"INC{datetime.now().timestamp()}",
                'ticket_number': f"INC000{int(datetime.now().timestamp()) % 10000}",
                'status': 'open',
                'assigned_to': 'IT Team'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_ticket_status(self, ticket_id: str) -> Dict:
        """Get ticket status"""
        return {
            'ticket_id': ticket_id,
            'status': 'in_progress',
            'updated_at': datetime.now().isoformat()
        }


# ======================== INTEGRATION MANAGER ========================

class IntegrationManager:
    """Central manager for all API integrations"""
    
    def __init__(self):
        # Job Board APIs
        self.linkedin = LinkedInAPI()
        self.indeed = IndeedAPI()
        self.naukri = NaukriAPI()
        
        # Calendar APIs
        self.google_calendar = GoogleCalendarAPI()
        self.outlook = OutlookAPI()
        
        # Assessment APIs
        self.hackerrank = HackerRankAPI()
        self.codility = CodilityAPI()
        
        # Email APIs
        self.sendgrid = SendGridAPI()
        self.twilio = TwilioAPI()
        
        # E-Signature
        self.docusign = DocuSignAPI()
        
        # Enterprise
        self.successfactors = SuccessFactorsAPI()
        self.servicenow = ServiceNowAPI()
    
    def post_job_to_all_platforms(self, job_data: Dict, platforms: List[str]) -> Dict:
        """Post job to selected platforms"""
        results = {}
        
        if 'linkedin' in platforms:
            results['linkedin'] = self.linkedin.post_job(job_data)
        if 'indeed' in platforms:
            results['indeed'] = self.indeed.post_job(job_data)
        if 'naukri' in platforms:
            results['naukri'] = self.naukri.post_job(job_data)
        
        return results
    
    def post_job_to_platform(self, platform: str, job_data: Dict) -> Dict:
        """Post job to a single platform"""
        if platform == 'linkedin':
            return self.linkedin.post_job(job_data)
        elif platform == 'indeed':
            return self.indeed.post_job(job_data)
        elif platform == 'naukri':
            return self.naukri.post_job(job_data)
        
        # For other platforms (company_portal, internal_referral), return mock success
        return {
            'success': True,
            'platform': platform,
            'post_id': f'{platform}_{job_data.get("job_id", "unknown")}',
            'posted_at': datetime.now().isoformat()
        }
    
    def delete_job_post(self, platform: str, post_id: str) -> Dict:
        """Delete job post from a platform"""
        # Mock implementation - in production, call actual API to delete
        return {
            'success': True,
            'platform': platform,
            'post_id': post_id,
            'deleted_at': datetime.now().isoformat(),
            'message': f'Job removed from {platform}'
        }
    
    def send_assessment(self, assessment_type: str, candidate_data: Dict) -> Dict:
        """Send assessment to candidate"""
        if assessment_type == 'coding':
            return self.hackerrank.create_assessment(candidate_data)
        elif assessment_type == 'sql':
            return self.codility.create_assessment(candidate_data)
        
        return {'success': False, 'error': 'Unknown assessment type'}
    
    def send_interview_invite(self, calendar_provider: str, event_data: Dict) -> Dict:
        """Send interview invitation via calendar"""
        if calendar_provider == 'google':
            return self.google_calendar.create_event(event_data)
        elif calendar_provider == 'outlook':
            return self.outlook.create_event(event_data)
        
        return {'success': False, 'error': 'Unknown calendar provider'}
    
    def send_notification(self, candidate_data: Dict, message_type: str, email_template: str) -> Dict:
        """Send notification to candidate"""
        results = {}
        
        # Send email
        results['email'] = self.sendgrid.send_email(
            to=candidate_data['email'],
            subject=self._get_subject(message_type),
            body=email_template,
            html=True
        )
        
        # Send SMS if phone available
        if 'phone' in candidate_data:
            results['sms'] = self.twilio.send_sms(
                phone=candidate_data['phone'],
                message=f"Status update: {message_type}"
            )
        
        return results
    
    def send_offer_for_signature(self, offer_data: Dict) -> Dict:
        """Send offer for e-signature"""
        return self.docusign.send_for_signature(offer_data)
    
    def provision_employee(self, employee_data: Dict) -> Dict:
        """Provision new employee across systems"""
        results = {}
        
        # Create in HRIS
        sf_result = self.successfactors.create_employee(employee_data)
        results['hris'] = sf_result
        
        if sf_result['success']:
            employee_id = sf_result['employee_id']
            
            # Create IT provisioning ticket
            results['it'] = self.servicenow.create_it_ticket({
                'employee_name': f"{employee_data.get('first_name')} {employee_data.get('last_name')}",
                'description': 'Laptop, email, software licenses'
            })
        
        return results
    
    def _get_subject(self, message_type: str) -> str:
        """Get email subject based on message type"""
        subjects = {
            'application_received': 'Application Received - We\'re reviewing your profile',
            'screening_passed': 'Congratulations! You\'ve passed our screening',
            'screening_failed': 'Application Status Update',
            'assessment_ready': 'Your Assessment Awaits - Complete in 7 days',
            'interview_scheduled': 'Interview Scheduled - Confirm Your Availability',
            'offer_sent': 'Offer Letter - Awaiting Your Acceptance'
        }
        return subjects.get(message_type, 'Application Status Update')


# Initialize global integration manager
integration_manager = IntegrationManager()
