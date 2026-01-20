"""
SendGrid Email Configuration
Handles email sending via SendGrid API
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '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')
FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@gcc-hiring.com')  # Default sender email
FROM_NAME = os.environ.get('FROM_NAME', 'GCC Hiring System')

# Check if API key is configured
if not SENDGRID_API_KEY:
    print("[SendGrid] WARNING: SENDGRID_API_KEY is not configured!")
    print("[SendGrid] Emails will not be sent. Please set the SENDGRID_API_KEY environment variable.")


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
        
        # Check if API key is configured
        if not SENDGRID_API_KEY:
            print("[SendGrid] ERROR: SENDGRID_API_KEY is not configured!")
            return {
                'success': False,
                'error': 'SENDGRID_API_KEY not configured',
                'message': 'Email service is not configured. Please configure the SENDGRID_API_KEY environment variable.'
            }
        
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
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1f2937; background: #f3f4f6; }}
            .email-wrapper {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ 
                background: linear-gradient(135deg, #1f2937 0%, #111827 100%); 
                color: white; 
                padding: 40px 30px; 
                text-align: center; 
            }}
            .header h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
            .content {{ padding: 40px 35px; background: white; }}
            .greeting {{ font-size: 18px; margin-bottom: 20px; color: #111827; }}
            .message {{ color: #4b5563; margin-bottom: 25px; font-size: 16px; line-height: 1.8; }}
            .skills-badge-container {{ margin: 25px 0; }}
            .skills-badge {{ 
                display: inline-block; 
                background: #f3f4f6; 
                color: #4b5563; 
                padding: 12px 20px; 
                border-radius: 8px; 
                font-size: 14px;
                border-left: 4px solid #9ca3af;
                font-style: italic;
            }}
            .footer {{ 
                background: #f9fafb; 
                padding: 30px; 
                text-align: center; 
                border-top: 1px solid #f3f4f6;
                color: #6b7280;
                font-size: 13px;
            }}
            .divider {{ height: 1px; background: #f3f4f6; margin: 30px 0; }}
            .signature {{ margin-top: 30px; color: #111827; font-weight: 600; font-size: 15px; }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <h1>Application Update</h1>
            </div>
            <div class="content">
                <p class="greeting">Dear <strong>{candidate_name}</strong>,</p>
                
                <p class="message">Thank you for your interest in the <strong>{job_title}</strong> position at GCC. We truly appreciate you taking the time to apply and share your background with us.</p>
                
                <p class="message">After a thorough review of your application, we wanted to let you know that we've decided to move forward with other candidates whose experience more closely matches our technical requirements at this stage.</p>
                
                <div class="skills-badge-container">
                    <div class="skills-badge">
                        "Particularly impressed by your experience with {skills_text}"
                    </div>
                </div>
                
                <p class="message">Our team focuses on specific skill sets for each project, and while this position isn't the right fit right now, we'll keep your profile in our talent network for future openings that align with your unique expertise.</p>
                
                <div class="divider"></div>
                
                <p class="message">We appreciate your interest in GCC and wish you the very best in your job search and professional journey.</p>
                
                <p class="signature">
                    Best regards,<br>
                    <span style="color: #6366f1;">The Recruitment Team</span><br>
                    GCC Hiring System
                </p>
            </div>
            <div class="footer">
                <p>This is an automated message. Please do not reply directly.</p>
                <p>© 2024 GCC Hiring System</p>
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
    """Send an interview invitation email - ENHANCED VERSION with modern design"""
    
    subject = f"🎉 Interview Invitation: {job_title} - GCC Hiring"
    
    location_info = meeting_link if interview_type == "Video Call" else location or "To be confirmed"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #1f2937; background: #f3f4f6; }}
            .email-wrapper {{ max-width: 600px; margin: 0 auto; background: #ffffff; }}
            .header {{ 
                background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%); 
                color: white; 
                padding: 40px 30px; 
                text-align: center; 
                border-radius: 0;
            }}
            .header-icon {{ font-size: 48px; margin-bottom: 15px; }}
            .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; text-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .header p {{ font-size: 16px; opacity: 0.95; }}
            .content {{ padding: 40px 30px; }}
            .greeting {{ font-size: 18px; margin-bottom: 20px; }}
            .greeting strong {{ color: #059669; }}
            .message {{ color: #4b5563; margin-bottom: 25px; font-size: 15px; }}
            .details-card {{ 
                background: linear-gradient(180deg, #f0fdf4 0%, #ecfdf5 100%); 
                border: 1px solid #a7f3d0; 
                border-radius: 12px; 
                padding: 25px; 
                margin: 25px 0;
            }}
            .details-card h3 {{ 
                color: #059669; 
                font-size: 18px; 
                margin-bottom: 20px; 
                display: flex; 
                align-items: center; 
                gap: 8px;
            }}
            .detail-row {{ 
                display: flex; 
                align-items: flex-start; 
                margin-bottom: 15px; 
                padding-bottom: 15px; 
                border-bottom: 1px dashed #d1fae5;
            }}
            .detail-row:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
            .detail-icon {{ 
                width: 40px; 
                height: 40px; 
                background: #059669; 
                color: white; 
                border-radius: 10px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 18px; 
                margin-right: 15px;
                flex-shrink: 0;
            }}
            .detail-content {{ flex: 1; }}
            .detail-label {{ color: #6b7280; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }}
            .detail-value {{ color: #1f2937; font-weight: 600; font-size: 15px; }}
            .cta-section {{ text-align: center; margin: 30px 0; }}
            .cta-button {{ 
                display: inline-block; 
                background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                color: white !important; 
                padding: 16px 40px; 
                text-decoration: none; 
                border-radius: 8px; 
                font-weight: 600; 
                font-size: 16px;
                box-shadow: 0 4px 14px rgba(5, 150, 105, 0.4);
                transition: all 0.3s ease;
            }}
            .tips-section {{ 
                background: #fef3c7; 
                border-left: 4px solid #f59e0b; 
                padding: 20px; 
                border-radius: 0 8px 8px 0; 
                margin: 25px 0;
            }}
            .tips-section h4 {{ color: #92400e; margin-bottom: 12px; font-size: 14px; }}
            .tips-section ul {{ color: #92400e; font-size: 14px; padding-left: 20px; }}
            .tips-section li {{ margin-bottom: 8px; }}
            .footer {{ 
                background: #f9fafb; 
                padding: 25px 30px; 
                text-align: center; 
                border-top: 1px solid #e5e7eb;
            }}
            .footer p {{ color: #6b7280; font-size: 13px; margin-bottom: 5px; }}
            .social-links {{ margin-top: 15px; }}
            .social-links a {{ color: #059669; text-decoration: none; margin: 0 10px; font-size: 13px; }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="header">
                <div class="header-icon">🎉</div>
                <h1>You're Invited!</h1>
                <p>Interview Scheduled for {job_title}</p>
            </div>
            
            <div class="content">
                <p class="greeting">Dear <strong>{candidate_name}</strong>,</p>
                
                <p class="message">
                    Congratulations! We are thrilled to invite you for an interview for the <strong>{job_title}</strong> position. 
                    Your application stood out among many candidates, and we're excited to learn more about you!
                </p>
                
                <div class="details-card">
                    <h3>📅 Interview Details</h3>
                    
                    <div class="detail-row">
                        <div class="detail-icon">📅</div>
                        <div class="detail-content">
                            <div class="detail-label">Date</div>
                            <div class="detail-value">{interview_date}</div>
                        </div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-icon">⏰</div>
                        <div class="detail-content">
                            <div class="detail-label">Time</div>
                            <div class="detail-value">{interview_time}</div>
                        </div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-icon">📍</div>
                        <div class="detail-content">
                            <div class="detail-label">{"Meeting Link" if interview_type == "Video Call" else "Location"}</div>
                            <div class="detail-value">{location_info}</div>
                        </div>
                    </div>
                    
                    <div class="detail-row">
                        <div class="detail-icon">💼</div>
                        <div class="detail-content">
                            <div class="detail-label">Interview Type</div>
                            <div class="detail-value">{interview_type}</div>
                        </div>
                    </div>
                </div>
                
                {f'<div class="cta-section"><a href="{meeting_link}" class="cta-button">Join Interview →</a></div>' if meeting_link else ''}
                
                <div class="tips-section">
                    <h4>💡 Tips for a Successful Interview:</h4>
                    <ul>
                        <li>Test your camera and microphone beforehand</li>
                        <li>Find a quiet, well-lit space</li>
                        <li>Have your resume and portfolio ready</li>
                        <li>Prepare questions about the role and company</li>
                    </ul>
                </div>
                
                <p class="message">
                    Please confirm your attendance by replying to this email. If you need to reschedule, 
                    please let us know at least 24 hours in advance.
                </p>
                
                <p style="margin-top: 25px; color: #1f2937;">
                    Best regards,<br>
                    <strong style="color: #059669;">The GCC Hiring Team</strong>
                </p>
            </div>
            
            <div class="footer">
                <p><strong>GCC Hiring System</strong></p>
                <p>Automated Recruitment Platform</p>
                <div class="social-links">
                    <a href="#">LinkedIn</a> • <a href="#">Website</a> • <a href="#">Support</a>
                </div>
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


def send_hr_interview_invitation(candidate_name: str, candidate_email: str, job_title: str, 
                                  interview_score: int, interviewer_name: str = None,
                                  scheduled_date: str = None, scheduled_time: str = None) -> dict:
    """Send HR interview invitation for candidates scoring 80%+ in technical interview"""
    
    subject = f"🎉 Congratulations! HR Interview Invitation - {job_title} | GCC"
    
    interviewer_display = interviewer_name or "Our HR Representative"
    date_display = scheduled_date or "To be scheduled"
    time_display = scheduled_time or "Will be communicated"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 40px 30px; text-align: center; }}
            .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
            .header .emoji {{ font-size: 48px; margin-bottom: 15px; }}
            .content {{ padding: 35px 30px; }}
            .score-badge {{ display: inline-block; background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 12px 28px; border-radius: 30px; font-weight: 700; font-size: 20px; margin: 20px 0; }}
            .info-card {{ background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 20px; margin: 25px 0; }}
            .info-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed #bbf7d0; }}
            .info-row:last-child {{ border-bottom: none; }}
            .info-label {{ color: #059669; font-weight: 600; }}
            .info-value {{ color: #1f2937; font-weight: 500; }}
            .next-steps {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px 20px; margin: 25px 0; border-radius: 0 8px 8px 0; }}
            .footer {{ background: #f9fafb; padding: 25px; text-align: center; color: #6b7280; font-size: 13px; border-top: 1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="emoji">🎉</div>
                <h1>Congratulations!</h1>
                <p>You've Passed the Technical Interview</p>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>We are thrilled to inform you that you have <strong>successfully passed</strong> the technical interview for the <strong>{job_title}</strong> position at GCC!</p>
                
                <div style="text-align: center;">
                    <span class="score-badge">🏆 Interview Score: {interview_score}%</span>
                </div>
                
                <p>Your performance was exceptional, and we would like to invite you to the next stage of our hiring process - the <strong>HR Interview</strong>.</p>
                
                <div class="info-card">
                    <h3 style="margin: 0 0 15px 0; color: #059669;">📋 HR Interview Details</h3>
                    <div class="info-row">
                        <span class="info-label">Interview Type</span>
                        <span class="info-value">In-Person Meeting</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Interviewer</span>
                        <span class="info-value">{interviewer_display}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Proposed Date</span>
                        <span class="info-value">{date_display}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Time</span>
                        <span class="info-value">{time_display}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Location</span>
                        <span class="info-value">GCC Office (Address will be shared)</span>
                    </div>
                </div>
                
                <div class="next-steps">
                    <strong>📌 What to Expect:</strong>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>Discussion about your career goals and aspirations</li>
                        <li>Cultural fit assessment</li>
                        <li>Salary and benefits discussion</li>
                        <li>Q&A session about the role and company</li>
                    </ul>
                </div>
                
                <p>Our HR team will contact you shortly to confirm the exact date and time. Please keep your phone and email accessible.</p>
                
                <p>We look forward to meeting you in person!</p>
                
                <p style="margin-top: 30px;">
                    Warm regards,<br>
                    <strong style="color: #059669;">The Recruitment Team</strong><br>
                    GCC Hiring System
                </p>
            </div>
            <div class="footer">
                <p>© 2025 GCC Hiring System. All rights reserved.</p>
                <p>This is an automated message from GCC Hiring System.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)


def send_interview_rejection_email(candidate_name: str, candidate_email: str, job_title: str,
                                    interview_score: int, feedback: str = None) -> dict:
    """Send rejection email for candidates scoring below 80% in interview"""
    
    subject = f"Interview Results - {job_title} | GCC Hiring Team"
    
    feedback_text = feedback or "While your responses showed potential in some areas, they did not fully meet our requirements for this specific role."
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 20px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; padding: 40px 30px; text-align: center; }}
            .header h1 {{ margin: 0 0 10px 0; font-size: 24px; }}
            .content {{ padding: 35px 30px; }}
            .score-badge {{ display: inline-block; background: #f3f4f6; color: #4b5563; padding: 10px 24px; border-radius: 25px; font-weight: 600; font-size: 16px; margin: 15px 0; }}
            .feedback-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px 20px; margin: 25px 0; border-radius: 0 8px 8px 0; }}
            .encourage-box {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px 20px; margin: 25px 0; border-radius: 0 8px 8px 0; }}
            .footer {{ background: #f9fafb; padding: 25px; text-align: center; color: #6b7280; font-size: 13px; border-top: 1px solid #e5e7eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Interview Results</h1>
                <p>Thank you for your time and effort</p>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>Thank you for taking the time to complete the interview for the <strong>{job_title}</strong> position at GCC. We truly appreciate the effort you put into the process.</p>
                
                <div style="text-align: center;">
                    <span class="score-badge">Interview Score: {interview_score}%</span>
                </div>
                
                <p>After careful evaluation of your interview responses, we regret to inform you that we will not be moving forward with your application at this time.</p>
                
                <div class="feedback-box">
                    <strong>📝 Feedback:</strong>
                    <p style="margin: 10px 0 0 0;">{feedback_text}</p>
                </div>
                
                <div class="encourage-box">
                    <strong>💡 Keep Growing!</strong>
                    <p style="margin: 10px 0 0 0;">This doesn't reflect your overall potential. We encourage you to:</p>
                    <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                        <li>Continue building your technical skills</li>
                        <li>Practice mock interviews and coding challenges</li>
                        <li>Consider applying for other roles that match your current skill level</li>
                        <li>Feel free to reapply after gaining more experience</li>
                    </ul>
                </div>
                
                <p>We wish you all the best in your career journey and future endeavors.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The Recruitment Team</strong><br>
                    GCC Hiring System
                </p>
            </div>
            <div class="footer">
                <p>© 2025 GCC Hiring System. All rights reserved.</p>
                <p>This is an automated message. Please do not reply directly.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)


def send_application_confirmation(candidate_name: str, candidate_email: str, job_title: str) -> dict:
    """Send application received confirmation email - Thank you for registering"""
    
    subject = f"Thank You for Registering - {job_title} | GCC Hiring Team"
    
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
            .highlight-box {{ background: #dbeafe; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
            .timeline {{ margin: 20px 0; }}
            .timeline-item {{ display: flex; align-items: flex-start; margin-bottom: 15px; }}
            .timeline-icon {{ width: 30px; height: 30px; background: #3b82f6; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px; font-size: 14px; }}
            .timeline-content {{ flex: 1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="check-icon">🎉</div>
                <h1>Thank You for Registering!</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>Thank you for registering and applying for the <strong>{job_title}</strong> position at GCC. We are excited to receive your application!</p>
                
                <div class="highlight-box">
                    <strong>📋 What happens next?</strong><br>
                    Our recruitment team will carefully analyze your resume and assess your qualifications. We will keep you updated on any upcoming events and next steps in the hiring process.
                </div>
                
                <p><strong>🚀 Our Hiring Process:</strong></p>
                
                <div class="timeline">
                    <div class="timeline-item">
                        <div class="timeline-icon">1</div>
                        <div class="timeline-content">
                            <strong>Resume Analysis</strong><br>
                            <span style="color: #6b7280; font-size: 14px;">Our AI-powered system will analyze your resume and match your skills with the job requirements.</span>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-icon">2</div>
                        <div class="timeline-content">
                            <strong>Profile Review</strong><br>
                            <span style="color: #6b7280; font-size: 14px;">Our HR team will review shortlisted candidates for the next round.</span>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-icon">3</div>
                        <div class="timeline-content">
                            <strong>Interview & Updates</strong><br>
                            <span style="color: #6b7280; font-size: 14px;">Selected candidates will be contacted for interviews. Stay tuned for upcoming events!</span>
                        </div>
                    </div>
                </div>
                
                <p>We appreciate your interest in joining our team and will be in touch soon!</p>
                
                <p>Warm regards,<br>
                <strong>GCC Hiring Team</strong><br>
                <span style="color: #6b7280; font-size: 13px;">Human Resources Department</span></p>
            </div>
            <div class="footer">
                <p>© 2025 GCC Hiring System. All rights reserved.<br>
                This is an automated message. Please do not reply directly to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)


def send_auto_rejection_email(candidate_name: str, candidate_email: str, job_title: str, match_score: int) -> dict:
    """Send automatic rejection email for candidates with ATS score below 50%"""
    
    subject = f"Application Update: {job_title} - GCC Hiring Team"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            .encourage-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
            .tip-box {{ background: #e0e7ff; border-left: 4px solid #6366f1; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Application Update</h1>
            </div>
            <div class="content">
                <p>Dear <strong>{candidate_name}</strong>,</p>
                
                <p>Thank you for your interest in the <strong>{job_title}</strong> position at GCC and for taking the time to submit your application.</p>
                
                <p>After carefully reviewing your resume and qualifications, we regret to inform you that we will not be moving forward with your application at this time. The position requires specific skills and experience that more closely match other candidates in our current pool.</p>
                
                <div class="encourage-box">
                    <strong>💡 Don't be discouraged!</strong><br>
                    This decision was based on the specific requirements of this role. We encourage you to apply for other positions that may better match your skill set.
                </div>
                
                <div class="tip-box">
                    <strong>📝 Tips to improve your application:</strong><br>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Tailor your resume to highlight relevant skills for each position</li>
                        <li>Include specific keywords from the job description</li>
                        <li>Quantify your achievements with numbers and metrics</li>
                        <li>Keep your resume format clean and ATS-friendly</li>
                    </ul>
                </div>
                
                <p>We wish you the very best in your job search and future career endeavors. Please feel free to apply for other opportunities at GCC that align with your qualifications.</p>
                
                <p>Best regards,<br>
                <strong>GCC Hiring Team</strong><br>
                <span style="color: #6b7280; font-size: 13px;">Human Resources Department</span></p>
            </div>
            <div class="footer">
                <p>© 2025 GCC Hiring System. All rights reserved.<br>
                This is an automated message. Please do not reply directly to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(candidate_email, subject, html_content)


def send_offer_email(candidate_name: str, candidate_email: str, position: str, salary: int, joining_date: str, html_content: str = None) -> dict:
    """Send offer letter email to candidate"""
    
    subject = f"🎉 Job Offer: {position} - GCC Hiring Team"
    
    # Use provided HTML content or generate default
    if not html_content:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white;">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 40px 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">🎉 Congratulations!</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">Job Offer Letter</p>
                </div>
                
                <div style="padding: 40px 30px;">
                    <p style="color: #1f2937; font-size: 16px;">Dear <strong>{candidate_name}</strong>,</p>
                    
                    <p style="color: #4b5563; font-size: 15px; line-height: 1.6;">
                        We are thrilled to extend an offer for the position of <strong>{position}</strong>.
                    </p>
                    
                    <div style="background-color: #f0fdf4; border-radius: 12px; padding: 24px; margin: 30px 0; border-left: 4px solid #10b981;">
                        <h3 style="color: #047857; margin: 0 0 16px 0;">Offer Details</h3>
                        <p><strong>Position:</strong> {position}</p>
                        <p><strong>Salary:</strong> ${salary:,} USD per year</p>
                        <p><strong>Start Date:</strong> {joining_date}</p>
                    </div>
                    
                    <p style="color: #4b5563; font-size: 15px;">
                        Please review the offer details and let us know your decision.
                    </p>
                    
                    <p>Best regards,<br><strong>GCC Hiring Team</strong></p>
                </div>
                
                <div style="background-color: #1f2937; padding: 20px; text-align: center;">
                    <p style="color: #9ca3af; margin: 0; font-size: 12px;">© 2025 GCC Hiring System</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    print(f"[SendGrid] Sending offer letter to {candidate_email} for position: {position}")
    return send_email(candidate_email, subject, html_content)
