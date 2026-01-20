# GCC Hiring System - Backend

A Flask-based backend powering an AI-driven recruitment platform with Groq LLM integration, SendGrid email automation, LinkedIn OAuth, and intelligent resume parsing.

## 🌟 Features

### AI & Machine Learning

- **Resume Parsing** - Extract skills, experience, and qualifications from PDF resumes
- **Skill Matching** - AI-based candidate-to-job matching with scoring
- **ML Predictions** - Candidate success prediction using scikit-learn
- **AI Recommendations** - Salary suggestions, interview panel selection, assessment planning

### Interview System

- **Adaptive Interviews** - Dynamic question generation based on responses
- **Coding Evaluation** - Integrated code assessment with Judge0
- **Enhanced Interview** - Multi-stage interview management
- **AI Evaluation** - Automated response scoring and feedback

### 🔒 Enterprise Proctoring System

Backend support for real-time interview integrity monitoring:

- **Violation Recording** - Store and track all proctoring violations
- **Risk Level Calculation** - Automatic risk assessment based on violation patterns
- **Proctoring Reports** - Comprehensive violation summaries for HR review
- **Session Statistics** - Time tracking, focus analytics, and behavioral data
- **Integration with Interview Completion** - Proctoring data included in final evaluation

### Integrations

- **Groq LLM (LLaMA 3.3)** - AI-generated content (job descriptions, emails, posts)
- **SendGrid** - Email automation (confirmations, rejections, offers, invitations)
- **LinkedIn OAuth 2.0** - Social authentication and profile sharing
- **Magical AI** - Advanced skill extraction

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Application                         │
├─────────────────────────────────────────────────────────────────┤
│                           Routes                                 │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │  Main API   │  │  LinkedIn Auth  │  │   LinkedIn Share    │  │
│  │  (app.py)   │  │  (OAuth 2.0)    │  │   (Post Creation)   │  │
│  └─────────────┘  └─────────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                           Models                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │Resume Parser│  │Skill Matcher│  │   Interview System      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ML Predictor │  │AI Recommends│  │   Adaptive Interview    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                         Config                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐  │
│  │Groq Config  │  │Email Config │  │LinkedIn Cfg │  │Judge0  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘  │
└────────┬────────────────┬──────────────────┬────────────────────┘
         │                │                  │
         ▼                ▼                  ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────────┐
│  Groq API   │   │  SendGrid   │   │    LinkedIn     │
│ (LLaMA 3.3) │   │  (Emails)   │   │   OAuth 2.0     │
└─────────────┘   └─────────────┘   └─────────────────┘
```

## 📁 Directory Structure

```
backend/
├── app.py                    # Main Flask application (3500+ lines)
├── requirements.txt          # Python dependencies
├── diagnose_persistence.py   # Data persistence diagnostics
│
├── config/                   # Configuration modules
│   ├── ai_evaluator.py       # AI-based response evaluation
│   ├── api_integrations.py   # External API integrations
│   ├── devtunnel_config.py   # Dev tunnel (ngrok) configuration
│   ├── email_config.py       # SendGrid email setup
│   ├── groq_config.py        # Groq LLM configuration
│   ├── judge0_config.py      # Code execution API
│   ├── linkedin_config.py    # LinkedIn OAuth settings
│   └── magical_config.py     # Magical AI skill extraction
│
├── models/                   # AI/ML models
│   ├── adaptive_interview.py # Dynamic interview management
│   ├── ai_recommendations.py # Salary, panel, assessment recommendations
│   ├── enhanced_interview.py # Multi-stage interview system
│   ├── interview_system.py   # Core interview logic
│   ├── ml_predictor.py       # ML-based predictions
│   ├── resume_parser.py      # Resume parsing with NLP
│   └── skill_matcher.py      # Candidate-job skill matching
│
├── routes/                   # API route blueprints
│   ├── linkedin_auth.py      # LinkedIn OAuth endpoints
│   └── linkedin_share.py     # LinkedIn sharing endpoints
│
└── data/                     # Data storage
    ├── candidates.json       # Candidate data
    ├── interview_sessions.json
    ├── jobs.json             # Job postings
    └── resumes/              # Uploaded resume files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

The server will start at `http://localhost:5000`

## ⚙️ Configuration

Create a `.env` file in the backend directory:

```env
# Flask
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development

# Groq AI (LLaMA 3.3)
GROQ_API_KEY=your-groq-api-key

# SendGrid Email
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=your-verified-email@example.com
FROM_NAME=GCC Hiring System

# LinkedIn OAuth 2.0
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:3001/auth/linkedin/callback
LINKEDIN_MODE=REDIRECT  # MOCK, REDIRECT, or API
```

## 📁 Project Structure

```
backend/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── config/
│   ├── groq_config.py       # Groq AI integration
│   ├── email_config.py      # SendGrid email service
│   ├── linkedin_config.py   # LinkedIn OAuth config
│   └── api_integrations.py  # External API integrations
├── models/
│   ├── resume_parser.py     # Resume parsing logic
│   ├── skill_matcher.py     # Skill matching algorithms
│   ├── ai_recommendations.py # AI scoring & recommendations
│   └── ml_predictor.py      # ML prediction models
├── routes/
│   ├── linkedin_auth.py     # LinkedIn OAuth routes
│   └── linkedin_share.py    # LinkedIn job posting
└── data/
    ├── jobs.json            # Jobs database
    ├── candidates.json      # Candidates database
    └── resumes/             # Uploaded resumes
```

## 🤖 AI Features (Groq LLM)

### Auto-Generate Job Description

```bash
POST /api/ai/generate-job-description
Content-Type: application/json

{
  "job_title": "Senior Python Developer",
  "department": "Engineering",
  "location": "Remote"
}
```

### AI Skill Suggestions

```bash
POST /api/ai/suggest-skills
Content-Type: application/json

{
  "job_title": "Data Scientist",
  "current_skills": ["Python", "SQL"]
}
```

### Auto-Rejection System

- **Threshold**: 60%
- Candidates scoring below 60% are automatically rejected
- AI generates personalized rejection emails
- Candidates scoring ≥75% are shortlisted with congratulatory emails

## 📧 Email Automation (SendGrid)

| Event                 | Email Type   | Trigger                          |
| --------------------- | ------------ | -------------------------------- |
| Application Submitted | Confirmation | Automatic on apply               |
| Score ≥ 75%           | Shortlisted  | Automatic on scoring             |
| Score < 60%           | Rejection    | Automatic on scoring             |
| Manual Rejection      | Rejection    | When recruiter removes candidate |

## 🔗 API Endpoints

### Dashboard

| Method | Endpoint               | Description              |
| ------ | ---------------------- | ------------------------ |
| GET    | `/api/dashboard/stats` | Get dashboard statistics |

### Jobs

| Method | Endpoint                                   | Description                  |
| ------ | ------------------------------------------ | ---------------------------- |
| GET    | `/api/jobs`                                | List all jobs                |
| POST   | `/api/jobs`                                | Create new job               |
| GET    | `/api/jobs/<id>`                           | Get job details              |
| PUT    | `/api/jobs/<id>`                           | Update job                   |
| DELETE | `/api/jobs/<id>`                           | Delete job                   |
| GET    | `/api/jobs/<id>/salary-recommendation`     | AI salary recommendation     |
| GET    | `/api/jobs/<id>/interview-panel`           | AI panel recommendation      |
| GET    | `/api/jobs/<id>/assessment-recommendation` | AI assessment recommendation |

### Candidates

| Method | Endpoint                              | Description                                 |
| ------ | ------------------------------------- | ------------------------------------------- |
| GET    | `/api/candidates`                     | List all candidates                         |
| GET    | `/api/candidates/<id>`                | Get candidate details                       |
| PUT    | `/api/candidates/<id>`                | Update candidate                            |
| DELETE | `/api/candidates/<id>`                | Remove candidate (sends rejection email)    |
| GET    | `/api/candidates/<id>/score`          | AI scoring (triggers auto-reject/shortlist) |
| POST   | `/api/candidates/<id>/send-rejection` | Send rejection email                        |

### Applications

| Method | Endpoint                   | Description                    |
| ------ | -------------------------- | ------------------------------ |
| POST   | `/api/apply`               | Submit application with resume |
| POST   | `/api/applications/public` | Public application form        |

### AI Endpoints

| Method | Endpoint                           | Description            |
| ------ | ---------------------------------- | ---------------------- |
| POST   | `/api/ai/generate-job-description` | Generate JD from title |
| POST   | `/api/ai/suggest-skills`           | Get skill suggestions  |
| POST   | `/api/ai/generate-linkedin-post`   | Generate LinkedIn post |

### LinkedIn Integration

| Method | Endpoint                      | Description               |
| ------ | ----------------------------- | ------------------------- |
| GET    | `/api/auth/linkedin/login`    | Initiate OAuth login      |
| GET    | `/api/auth/linkedin/callback` | OAuth callback            |
| GET    | `/api/auth/linkedin/status`   | Check connection status   |
| POST   | `/api/linkedin/share/job`     | Share job to LinkedIn     |
| POST   | `/api/linkedin/auto-post`     | Auto-post job on creation |

### 🔒 Proctoring Endpoints

| Method | Endpoint                                      | Description                          |
| ------ | --------------------------------------------- | ------------------------------------ |
| POST   | `/api/interview/<token>/proctoring-violation` | Record a proctoring violation        |
| GET    | `/api/interview/<token>/proctoring-report`    | Get proctoring report for interview  |
| POST   | `/api/interview/<token>/proctoring-stats`     | Update proctoring session statistics |

#### Record Proctoring Violation

```bash
POST /api/interview/<token>/proctoring-violation
Content-Type: application/json

{
  "violation": {
    "type": "tab_switch",
    "severity": "high",
    "message": "Switched to another tab",
    "timestamp": "2026-01-20T10:30:00Z"
  }
}
```

**Violation Types:**

- `tab_switch` - Tab switch detected
- `focus_lost` - Browser lost focus
- `face_not_detected` - Face not visible
- `multiple_faces` - Multiple faces detected
- `copy_attempt` - Copy action blocked
- `paste_attempt` - Paste action blocked
- `fullscreen_exit` - Exited fullscreen mode
- `keyboard_shortcut` - Blocked keyboard shortcut

**Severity Levels:**

- `low` - Minor infractions
- `medium` - Moderate violations
- `high` - Serious violations
- `critical` - Critical integrity concerns

#### Get Proctoring Report

```bash
GET /api/interview/<token>/proctoring-report
```

Response:

```json
{
  "success": true,
  "proctoring_report": {
    "total_violations": 5,
    "violation_types": {
      "tab_switch": 2,
      "focus_lost": 3
    },
    "severity_breakdown": {
      "low": 1,
      "medium": 2,
      "high": 2,
      "critical": 0
    },
    "risk_level": "medium",
    "violations": [...]
  }
}
```

## 🔐 LinkedIn OAuth Setup

1. Create app at [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Add OAuth 2.0 scopes: `openid`, `profile`, `email`, `w_member_social`
3. Set redirect URI: `http://localhost:3001/auth/linkedin/callback`
4. Add credentials to `.env`

### LinkedIn Modes

- **MOCK**: Simulates API (for testing)
- **REDIRECT**: Opens LinkedIn for manual posting
- **API**: Direct API posting (requires verified app)

## 📊 Candidate Scoring

The AI scoring system evaluates candidates on:

- Skill match (40%)
- Experience relevance (30%)
- Education fit (15%)
- Overall profile (15%)

### Score Categories

| Score   | Category        | Action                 |
| ------- | --------------- | ---------------------- |
| 75-100% | High Priority   | Auto-shortlist + Email |
| 60-74%  | Medium Priority | Manual review          |
| 0-59%   | Low Priority    | Auto-reject + Email    |

## 🧪 Testing

```bash
# Test Groq AI
curl -X POST http://localhost:5000/api/ai/suggest-skills \
  -H "Content-Type: application/json" \
  -d '{"job_title": "Python Developer"}'

# Test job creation
curl -X POST http://localhost:5000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"title": "Software Engineer", "location": "Remote"}'
```

## 📦 Dependencies

| Package       | Purpose               |
| ------------- | --------------------- |
| Flask         | Web framework         |
| Flask-CORS    | Cross-origin requests |
| requests      | HTTP client           |
| sendgrid      | Email service         |
| python-dotenv | Environment variables |
| PyPDF2        | Resume parsing        |
| scikit-learn  | ML models             |
| pandas        | Data processing       |
| numpy         | Numerical computing   |

## 🚨 Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message",
  "details": "Additional context"
}
```

HTTP Status Codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Server Error

## 📝 License

MIT License - See [LICENSE](../LICENSE)

---

**GCC Hiring System** - AI-Powered Recruitment Platform
