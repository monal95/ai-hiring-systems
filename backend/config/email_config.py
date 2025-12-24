"""
SendGrid Email Configuration
Handles email sending via SendGrid API
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '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')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'monalprashanth98@gmail.com')  # Verified in SendGrid
FROM_NAME = os.environ.get('FROM_NAME', 'GCC Hiring System')


def send_email(to_email: str, subject: str, html_content: str, plain_content: str = None) -> dict:
    """
    Send an email using SendGrid API
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_content: HTML formatted email body
        plain_content: Plain text fallback (optional)
    
    Returns:
        dict with success status and message
    """
    try:
        print(f"[SendGrid] Attempting to send email to: {to_email}")
        print(f"[SendGrid] From: {FROM_EMAIL}")
        print(f"[SendGrid] Subject: {subject}")
        
        message = Mail(
            from_email=(FROM_EMAIL, FROM_NAME),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        
        if plain_content:
            message.add_content(Content("text/plain", plain_content))
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"[SendGrid] SUCCESS! Status code: {response.status_code}")
        
        return {
            'success': True,
            'status_code': response.status_code,
            'message': f'Email sent successfully to {to_email}',
            'message_id': response.headers.get('X-Message-Id', '')
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"[SendGrid] ERROR: {error_msg}")
        
        # Check for common issues
        if '403' in error_msg or 'Forbidden' in error_msg:
            print("[SendGrid] ⚠️  403 Error - Your sender email is NOT verified in SendGrid!")
            print("[SendGrid] Go to: https://app.sendgrid.com/settings/sender_auth/senders")
            print(f"[SendGrid] Add and verify: {FROM_EMAIL}")
        elif '401' in error_msg or 'Unauthorized' in error_msg:
            print("[SendGrid] ⚠️  401 Error - API key is invalid or expired!")
        
        return {
            'success': False,
            'error': error_msg,
            'message': f'Failed to send email to {to_email}'
        }


def send_rejection_email(candidate_name: str, candidate_email: str, job_title: str, skills: list = None) -> dict:
    """Send a rejection email to a candidate"""
    
    skills_text = ", ".join(skills[:3]) if skills else "your qualifications"
    
    subject = f"Update on Your Application for {job_title} - GCC Hiring"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            .highlight {{ color: #667eea; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>GCC Hiring System</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>Thank you for taking the time to apply for the <span class="highlight">{job_title}</span> position with us. We truly appreciate your interest in joining our team.</p>
                
                <p>After careful consideration of all applications, we regret to inform you that we have decided to move forward with other candidates whose experience more closely aligns with our current needs.</p>
                
                <p>We were impressed by {skills_text} and encourage you to apply for future opportunities that match your profile.</p>
                
                <p>We wish you the very best in your career journey and future endeavors.</p>
                
                <p>Warm regards,<br>
                <strong>The Recruitment Team</strong><br>
                GCC Hiring System</p>
            </div>
            <div class="footer">
                <p>This is an automated message from GCC Hiring System.<br>
                Please do not reply directly to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
    Dear {candidate_name},
    
    Thank you for applying for the {job_title} position with us.
    
    After careful consideration, we have decided to move forward with other candidates.
    
    We were impressed by {skills_text} and encourage you to apply for future opportunities.
    
    Best regards,
    The Recruitment Team
    GCC Hiring System
    """
    
    return send_email(candidate_email, subject, html_content, plain_content)


def send_interview_invitation(candidate_name: str, candidate_email: str, job_title: str, 
                              interview_date: str, interview_time: str, interview_type: str,
                              meeting_link: str = None, location: str = None) -> dict:
    """Send an interview invitation email"""
    
    subject = f"Interview Invitation: {job_title} - GCC Hiring"
    
    location_info = meeting_link if interview_type == "Video Call" else location or "To be confirmed"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .details-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            .btn {{ display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Interview Invitation</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>Congratulations! We are pleased to invite you for an interview for the <strong>{job_title}</strong> position.</p>
                
                <div class="details-box">
                    <h3>📅 Interview Details</h3>
                    <p><strong>Date:</strong> {interview_date}</p>
                    <p><strong>Time:</strong> {interview_time}</p>
                    <p><strong>Type:</strong> {interview_type}</p>
                    <p><strong>{"Meeting Link" if interview_type == "Video Call" else "Location"}:</strong> {location_info}</p>
                </div>
                
                <p>Please confirm your attendance by replying to this email.</p>
                
                {f'<a href="{meeting_link}" class="btn">Join Meeting</a>' if meeting_link else ''}
                
                <p>Best regards,<br>
                <strong>The Recruitment Team</strong></p>
            </div>
            <div class="footer">
                <p>GCC Hiring System - Automated Notification</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)


def send_offer_letter(candidate_name: str, candidate_email: str, job_title: str,
                      salary: str, start_date: str, benefits: list = None) -> dict:
    """Send an offer letter email"""
    
    subject = f"🎊 Job Offer: {job_title} - GCC Hiring"
    
    benefits_html = ""
    if benefits:
        benefits_html = "<ul>" + "".join([f"<li>{b}</li>" for b in benefits]) + "</ul>"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .offer-box {{ background: white; padding: 25px; border-radius: 8px; margin: 20px 0; border: 2px solid #f59e0b; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            .highlight {{ color: #d97706; font-weight: bold; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎊 Congratulations!</h1>
                <p>You've Got the Job!</p>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>We are thrilled to extend an official offer for the position of <strong>{job_title}</strong>!</p>
                
                <div class="offer-box">
                    <h3>📋 Offer Details</h3>
                    <p><strong>Position:</strong> {job_title}</p>
                    <p><strong>Salary:</strong> <span class="highlight">{salary}</span></p>
                    <p><strong>Start Date:</strong> {start_date}</p>
                    {f"<p><strong>Benefits:</strong></p>{benefits_html}" if benefits else ""}
                </div>
                
                <p>Please review the offer and let us know your decision within 5 business days.</p>
                
                <p>We're excited about the possibility of you joining our team!</p>
                
                <p>Best regards,<br>
                <strong>The Recruitment Team</strong></p>
            </div>
            <div class="footer">
                <p>GCC Hiring System - Official Offer Letter</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)


def send_application_confirmation(candidate_name: str, candidate_email: str, job_title: str) -> dict:
    """Send application received confirmation email"""
    
    subject = f"Application Received: {job_title} - GCC Hiring"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .check-icon {{ font-size: 48px; margin-bottom: 10px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="check-icon">✅</div>
                <h1>Application Received!</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>Thank you for applying for the <strong>{job_title}</strong> position. We have successfully received your application.</p>
                
                <p>Our recruitment team will review your profile and get back to you within 5-7 business days.</p>
                
                <p><strong>What's Next?</strong></p>
                <ul>
                    <li>Our team reviews your application</li>
                    <li>Shortlisted candidates will be contacted for interviews</li>
                    <li>You'll receive updates on your application status</li>
                </ul>
                
                <p>Best of luck!</p>
                
                <p>Best regards,<br>
                <strong>The Recruitment Team</strong></p>
            </div>
            <div class="footer">
                <p>GCC Hiring System - Automated Confirmation</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)
