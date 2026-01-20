# Backend & Frontend URL Configuration Guide

## Overview

This document explains how to configure the hiring system to work with your dev tunnel backend and frontend URLs.

## Current Setup

### Backend (Port 5000)

- **Dev Tunnel:** `https://3h16jwxk-5000.inc1.devtunnels.ms`
- **Local Dev:** `http://localhost:5000`

### Frontend (Port 3000)

- **Dev Tunnel:** `https://3h16jwxk-3000.inc1.devtunnels.ms`
- **Local Dev:** `http://localhost:3000`

## Configuration Files

### Backend Configuration (`.env`)

Located in: `backend/.env`

```env
# Frontend URL for generating interview links
FRONTEND_URL=https://3h16jwxk-3000.inc1.devtunnels.ms

# Other critical configs:
SENDGRID_API_KEY=...
GROQ_API_KEY=...
# etc.
```

### Frontend Configuration (`.env.local`)

Located in: `frontend/.env.local`

```env
REACT_APP_API_BASE_URL=https://3h16jwxk-5000.inc1.devtunnels.ms
```

## How It Works

### 1. Backend Interview Links

When an interview session is created, the backend generates a link using `FRONTEND_URL`:

```
${FRONTEND_URL}/interview/{interview_token}
```

Example:

```
https://3h16jwxk-3000.inc1.devtunnels.ms/interview/b0cc184e-492d-47b3-8aa3-48af40684aea
```

### 2. Frontend API Calls

All API calls from the frontend use `REACT_APP_API_BASE_URL`:

```javascript
// Example API call
axios.get(`${API_BASE_URL}/api/jobs`);
// Resolves to:
// https://3h16jwxk-5000.inc1.devtunnels.ms/api/jobs
```

## Setup Instructions

### Switch Between Environments

#### Local Development (Localhost)

**Backend** - `backend/.env`:

```env
FRONTEND_URL=http://localhost:3000
```

**Frontend** - `frontend/.env.local`:

```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

#### Dev Tunnel

**Backend** - `backend/.env`:

```env
FRONTEND_URL=https://3h16jwxk-3000.inc1.devtunnels.ms
```

**Frontend** - `frontend/.env.local`:

```env
REACT_APP_API_BASE_URL=https://3h16jwxk-5000.inc1.devtunnels.ms
```

#### Production

**Backend** - `backend/.env`:

```env
FRONTEND_URL=https://hiring.yourcompany.com
```

**Frontend** - `frontend/.env.local`:

```env
REACT_APP_API_BASE_URL=https://api.hiring.yourcompany.com
```

## Implementation Details

### Backend Changes

**File:** `backend/models/interview_system.py`

```python
from dotenv import load_dotenv
import os

load_dotenv()
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# When creating interview sessions:
interview_link = f"{FRONTEND_URL}/interview/{interview_token}"
```

### Frontend Changes

**File:** `frontend/src/config/api.js`

```javascript
const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:5000";
export default API_BASE_URL;
```

**Usage in Components:**

```javascript
import API_BASE_URL from "../config/api";

// API call
axios.get(`${API_BASE_URL}/api/jobs`);
```

### Updated Components

All frontend components have been updated to use the centralized `API_BASE_URL`:

- `ApplicationUpload.jsx`
- `CandidateList.jsx`
- `CandidateManagement.jsx`
- `CodingChallenge.jsx`
- `Dashboard.jsx`
- `FeedbackScorecard.jsx`
- `InterviewScheduler.jsx`
- `InterviewSession.jsx`
- `JobApplicationForm.jsx`
- `JobCreation.jsx`
- `JobManagement.jsx`
- `JobsList.jsx`
- `LinkedInLogin.jsx`
- `LinkedInShare.jsx`
- `OfferManagement.jsx`
- `SpeechTest.jsx`

## API Endpoints

All backend endpoints are now accessible via the dev tunnel:

```
POST   https://3h16jwxk-5000.inc1.devtunnels.ms/api/apply
GET    https://3h16jwxk-5000.inc1.devtunnels.ms/api/jobs
GET    https://3h16jwxk-5000.inc1.devtunnels.ms/api/candidates
POST   https://3h16jwxk-5000.inc1.devtunnels.ms/api/interview/{token}/start
POST   https://3h16jwxk-5000.inc1.devtunnels.ms/api/interview/{token}/submit-response
POST   https://3h16jwxk-5000.inc1.devtunnels.ms/api/interview/{token}/resend-email
```

## Testing

### Verify Backend API Reachability

```bash
curl https://3h16jwxk-5000.inc1.devtunnels.ms/api/jobs
```

### Verify Frontend Configuration

Open browser console in frontend app:

```javascript
console.log(process.env.REACT_APP_API_BASE_URL);
// Should output: https://3h16jwxk-5000.inc1.devtunnels.ms
```

## Troubleshooting

### CORS Errors

If you see CORS errors when calling the API:

1. Ensure backend has CORS enabled:

   ```python
   from flask_cors import CORS
   CORS(app)
   ```

2. Backend must allow requests from frontend dev tunnel URL

### Wrong Interview Link

If candidates receive wrong interview links:

1. Check `FRONTEND_URL` in `backend/.env`
2. Restart backend server
3. Use the resend email endpoint to send updated links:
   ```bash
   POST /api/interview/{interview_token}/resend-email
   ```

### API Not Found Errors

If frontend can't reach API:

1. Verify `REACT_APP_API_BASE_URL` in `frontend/.env.local`
2. Check that dev tunnel backend is running
3. Verify CORS configuration on backend

## Environment Variable Reference

### Backend Variables

| Variable           | Purpose                  | Example                                    |
| ------------------ | ------------------------ | ------------------------------------------ |
| `FRONTEND_URL`     | Generate interview links | `https://3h16jwxk-3000.inc1.devtunnels.ms` |
| `FLASK_ENV`        | Flask environment        | `development`                              |
| `SENDGRID_API_KEY` | Email sending            | `SG.xxx...`                                |
| `GROQ_API_KEY`     | AI questions             | `gsk_xxx...`                               |

### Frontend Variables

| Variable                 | Purpose         | Example                                    |
| ------------------------ | --------------- | ------------------------------------------ |
| `REACT_APP_API_BASE_URL` | Backend API URL | `https://3h16jwxk-5000.inc1.devtunnels.ms` |

## Summary

✅ Backend configured to generate links with `FRONTEND_URL`
✅ Frontend components centralized to use `API_BASE_URL`
✅ Dev tunnel URLs configured in `.env` files
✅ All API calls updated to use environment variables
✅ Production-ready configuration system
