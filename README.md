# GCC Hiring System

An AI-powered recruitment and hiring management platform built with React and Flask, featuring intelligent resume parsing, automated candidate evaluation, AI-driven interviews, and seamless LinkedIn integration.

## 🌟 Features

### AI-Powered Recruitment

- **Smart Resume Parsing** - Automatically extract skills, experience, and qualifications from resumes using AI
- **Skill Matching** - AI-based matching of candidates to job requirements
- **Automated Screening** - Auto-rejection of candidates below threshold scores
- **AI Recommendations** - Intelligent salary suggestions, interview panel recommendations, and assessment planning

### Interview Management

- **Adaptive Interviews** - Dynamic question generation based on candidate responses
- **Coding Challenges** - Integrated coding assessment with Judge0 integration
- **Speech Testing** - Voice-based interview capabilities
- **AI Evaluation** - Automated response analysis and scoring

### Communication & Integration

- **Email Automation** - SendGrid-powered email workflows (confirmations, rejections, offers)
- **LinkedIn OAuth** - Social login and profile sharing
- **AI-Generated Content** - Job descriptions, rejection emails, and LinkedIn posts using Groq LLM

### Dashboard & Analytics

- **Real-time Dashboard** - Overview of hiring pipeline and metrics
- **Candidate Management** - Track candidates through each stage
- **Job Management** - Create, edit, and manage job postings
- **Offer Management** - Handle offer letters and negotiations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│   Dashboard │ Jobs │ Candidates │ Interviews │ Offers           │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (Flask API)                         │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  Resume Parser  │  Skill Matcher  │  Interview System           │
│  AI Recommender │  ML Predictor   │  Adaptive Interview         │
└────────┬────────┴────────┬────────┴──────────────┬──────────────┘
         │                 │                       │
         ▼                 ▼                       ▼
┌─────────────┐   ┌─────────────┐        ┌─────────────────┐
│  Groq API   │   │  SendGrid   │        │    LinkedIn     │
│ (LLaMA 3.3) │   │  (Emails)   │        │   OAuth 2.0     │
└─────────────┘   └─────────────┘        └─────────────────┘
```

## 📁 Project Structure

```
gcc-hiring-system/
├── backend/                 # Flask API server
│   ├── app.py              # Main application entry point
│   ├── requirements.txt    # Python dependencies
│   ├── config/             # Configuration modules
│   │   ├── ai_evaluator.py
│   │   ├── email_config.py
│   │   ├── groq_config.py
│   │   └── linkedin_config.py
│   ├── models/             # AI/ML models
│   │   ├── resume_parser.py
│   │   ├── skill_matcher.py
│   │   ├── interview_system.py
│   │   ├── adaptive_interview.py
│   │   └── ai_recommendations.py
│   ├── routes/             # API route blueprints
│   │   ├── linkedin_auth.py
│   │   └── linkedin_share.py
│   └── data/               # Data storage (JSON files)
│
├── frontend/               # React application
│   ├── src/
│   │   ├── App.jsx         # Main application component
│   │   ├── components/     # React components
│   │   ├── config/         # API configuration
│   │   └── styles/         # CSS stylesheets
│   └── public/             # Static assets
│
└── package.json            # Root package configuration
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.10+
- **pip** (Python package manager)

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Flask
FLASK_SECRET_KEY=your-secret-key

# Groq API (for AI features)
GROQ_API_KEY=your-groq-api-key

# SendGrid (for email automation)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_FROM_EMAIL=your-email@domain.com

# LinkedIn OAuth (optional)
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:5000/auth/linkedin/callback

# Judge0 (for coding challenges, optional)
JUDGE0_API_KEY=your-judge0-api-key
```

### Installation & Running

#### 1. Clone the Repository

```bash
git clone https://github.com/your-org/gcc-hiring-system.git
cd gcc-hiring-system
```

#### 2. Start the Backend

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

Backend will be available at `http://localhost:5000`

#### 3. Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open at `http://localhost:3000`

## 🔧 Tech Stack

### Frontend

- **React 18** - UI framework
- **Axios** - HTTP client
- **Material-UI** - Component library
- **Recharts** - Data visualization
- **Lucide React** - Icons

### Backend

- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Groq** - LLM API (LLaMA 3.3)
- **SendGrid** - Email delivery
- **scikit-learn** - Machine learning
- **NLTK** - Natural language processing
- **PyPDF2** - PDF parsing

## 📖 Documentation

- [Backend README](./backend/README.md) - Detailed backend documentation
- [Frontend README](./frontend/README.md) - Detailed frontend documentation

## 🔑 API Endpoints

| Method | Endpoint                  | Description                  |
| ------ | ------------------------- | ---------------------------- |
| GET    | `/api/jobs`               | List all jobs                |
| POST   | `/api/jobs`               | Create a new job             |
| GET    | `/api/candidates`         | List all candidates          |
| POST   | `/api/candidates`         | Add new candidate            |
| POST   | `/api/resume/parse`       | Parse resume file            |
| POST   | `/api/interview/start`    | Start interview session      |
| POST   | `/api/interview/evaluate` | Evaluate interview responses |
| POST   | `/api/email/send`         | Send email notification      |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for lightning-fast LLM inference
- [SendGrid](https://sendgrid.com/) for email delivery
- [LinkedIn](https://developer.linkedin.com/) for OAuth integration
