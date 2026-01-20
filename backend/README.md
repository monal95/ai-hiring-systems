# GCC Hiring System - Backend

A Flask-based backend powering an AI-driven recruitment platform with Groq LLM integration, SendGrid email automation, and LinkedIn OAuth.

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   Flask API     │────▶│   Groq API      │
│   (Backend)     │     │  (LLaMA 3.3)    │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│   SendGrid      │     │   LinkedIn      │
│   (Emails)      │     │   OAuth 2.0     │
└─────────────────┘     └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
cd backend

# Create virtual environment (optional but recommended)
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
