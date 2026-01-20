# GCC Hiring System - Frontend

A modern React-based frontend for an AI-driven recruitment platform with dashboard analytics, candidate management, and LinkedIn integration.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
├─────────────────────────────────────────────────────────────┤
│  Dashboard │ Jobs │ Candidates │ Interviews │ Offers        │
├─────────────────────────────────────────────────────────────┤
│                    Component Layer                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐   │
│  │Dashboard│ │  Jobs   │ │Candidate│ │  Interview      │   │
│  │         │ │ Mgmt    │ │  Mgmt   │ │  Scheduler      │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                      Axios HTTP Client                      │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Flask Backend     │
                  │   (localhost:5000)  │
                  └─────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 16+
- npm or yarn
- Backend server running on port 5000

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The application will open at `http://localhost:3000`

## ⚙️ Configuration

The frontend connects to the backend API at `http://localhost:5000` by default.

To change the API URL, you can:

1. Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:5000
```

2. Or modify the axios base URL in your components.

## 📁 Project Structure

```
frontend/
├── package.json              # Node.js dependencies & scripts
├── postcss.config.js         # PostCSS configuration
├── public/
│   └── index.html            # HTML template
└── src/
    ├── index.js              # React entry point
    ├── App.jsx               # Main application component
    ├── App.css               # Global styles
    └── components/
        ├── Dashboard.jsx          # Main dashboard with analytics
        ├── Dashboard.css
        ├── JobCreation.jsx        # Create new job postings
        ├── JobCreation.css
        ├── JobManagement.jsx      # Manage existing jobs
        ├── JobManagement.css
        ├── JobsList.jsx           # List all jobs
        ├── JobApplicationForm.jsx # Public job application form
        ├── JobApplicationForm.css
        ├── CandidateList.jsx      # List candidates
        ├── CandidateList.css
        ├── CandidateManagement.jsx # Manage candidates
        ├── CandidateManagement.css
        ├── ApplicationUpload.jsx  # Upload resumes/applications
        ├── InterviewScheduler.jsx # Schedule interviews
        ├── InterviewScheduler.css
        ├── OfferManagement.jsx    # Manage job offers
        ├── OfferManagement.css
        ├── FeedbackScorecard.jsx  # Interview feedback
        ├── LinkedInLogin.jsx      # LinkedIn OAuth login
        ├── LinkedInShare.jsx      # Share jobs on LinkedIn
        └── PrivacyPolicy.jsx      # Privacy policy page
```

## 🎯 Features

### Dashboard

- Overview of hiring metrics and statistics
- Quick navigation to all modules
- Real-time data visualization

### Job Management

- Create new job postings with AI assistance
- Edit and manage existing positions
- Share jobs on LinkedIn
- Generate public application links

### Candidate Management

- View and manage all candidates
- AI-powered resume parsing
- Skill matching and scoring
- Track application status

### Interview Scheduling

- Schedule interviews with candidates
- Send email notifications via SendGrid
- Track interview status

### Offer Management

- Create and send job offers
- Track offer acceptance/rejection
- Manage compensation details

### LinkedIn Integration

- OAuth 2.0 authentication
- Share job postings to LinkedIn
- Professional branding

## 📜 Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Eject from Create React App
npm run eject
```

## 🔧 Tech Stack

- **React 18** - UI framework
- **Axios** - HTTP client for API calls
- **CSS3** - Styling (no external UI library)
- **Create React App** - Build tooling

## 🌐 Routes

| Path                      | Component          | Description            |
| ------------------------- | ------------------ | ---------------------- |
| `/`                       | Dashboard          | Main dashboard view    |
| `/apply/:jobId`           | JobApplicationForm | Public job application |
| `/auth/linkedin/callback` | LinkedInLogin      | OAuth callback handler |

## 🔗 API Integration

The frontend communicates with the Flask backend through RESTful APIs:

| Endpoint            | Method   | Description            |
| ------------------- | -------- | ---------------------- |
| `/api/jobs`         | GET      | Fetch all jobs         |
| `/api/jobs`         | POST     | Create new job         |
| `/api/jobs/:id`     | PUT      | Update job             |
| `/api/jobs/:id`     | DELETE   | Delete job             |
| `/api/candidates`   | GET      | Fetch all candidates   |
| `/api/candidates`   | POST     | Add new candidate      |
| `/api/apply/:jobId` | POST     | Submit job application |
| `/api/interviews`   | GET/POST | Manage interviews      |
| `/api/offers`       | GET/POST | Manage offers          |

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
