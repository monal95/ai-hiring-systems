# LinkedIn Integration for GCC Hiring System

This document explains the LinkedIn OAuth 2.0 integration for the GCC Hiring System.

## Features Implemented

### 1. LinkedIn OAuth 2.0 Login

- **Login with LinkedIn** button for recruiters
- Secure token exchange flow
- Profile display (name, email, picture)
- Session management with secure tokens

### 2. LinkedIn Job Sharing

- **AI-Generated Posts**: Automatically generates engaging LinkedIn posts from job data
- **Three Sharing Modes**:
  - **REDIRECT** (Default): Opens LinkedIn with post content ready to paste
  - **MOCK**: Simulates LinkedIn API for demo/testing
  - **API**: Direct posting to LinkedIn (requires OAuth login)

### 3. Privacy Policy Page

- Compliant with LinkedIn requirements
- Accessible at `/privacy-policy`

## Files Created

### Backend

- `backend/config/linkedin_config.py` - LinkedIn OAuth configuration
- `backend/routes/linkedin_auth.py` - OAuth endpoints (login, callback, status)
- `backend/routes/linkedin_share.py` - Job sharing endpoints
- `backend/routes/__init__.py` - Routes package init
- `backend/.env` - Environment variables (LinkedIn credentials)

### Frontend

- `frontend/src/components/LinkedInLogin.jsx` - LinkedIn login component
- `frontend/src/components/LinkedInShare.jsx` - LinkedIn share component
- `frontend/src/components/PrivacyPolicy.jsx` - Privacy policy page

## Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure LinkedIn App

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Select your app
3. Enable Products:
   - ✅ Sign In with LinkedIn using OpenID Connect
   - ✅ Share on LinkedIn (optional)
4. Add Redirect URL in OAuth 2.0 settings:
   ```
   http://localhost:3000/auth/linkedin/callback
   ```
5. Your credentials are already in `.env`:
   - Client ID: `86yvqgasdy2sr3`
   - Client Secret: `WPL_AP1.1jYf2tAlOTfaGwRX.v4foRg==`

### 3. Start the Backend

```bash
cd backend
python app.py
```

### 4. Start the Frontend

```bash
cd frontend
npm start
```

## How It Works

### Job Creation Flow with LinkedIn Sharing

1. Recruiter creates a new job
2. Selects LinkedIn in the platforms list
3. After job creation, sees **LinkedIn Share** section
4. Can optionally **Login with LinkedIn** for API mode
5. Clicks **Share to LinkedIn**:
   - **REDIRECT mode**: Post content is copied, LinkedIn opens
   - **MOCK mode**: Simulates successful post for demo
   - **API mode**: Posts directly to LinkedIn feed

### API Endpoints

| Endpoint                      | Method   | Description                    |
| ----------------------------- | -------- | ------------------------------ |
| `/api/auth/linkedin/login`    | GET      | Get OAuth authorization URL    |
| `/api/auth/linkedin/callback` | POST     | Exchange code for access token |
| `/api/auth/linkedin/status`   | GET      | Check connection status        |
| `/api/auth/linkedin/logout`   | POST     | Disconnect LinkedIn            |
| `/api/linkedin/share/job`     | POST     | Share job to LinkedIn          |
| `/api/linkedin/generate-post` | POST     | Generate AI post preview       |
| `/api/linkedin/mode`          | GET/POST | Get/set sharing mode           |
| `/api/mock/linkedin/jobs`     | POST     | Mock LinkedIn Jobs API         |

## LinkedIn Scopes Used

- `openid` - OpenID Connect authentication
- `profile` - Basic profile info (name, picture)
- `email` - Email address
- `w_member_social` - Share content on LinkedIn

## Demo Flow

1. **Create a Job** → Fill job details
2. **Select LinkedIn** → Keep LinkedIn checked in platforms
3. **Submit** → Job created successfully
4. **Login with LinkedIn** (optional) → Authenticate
5. **Preview AI Post** → See generated content
6. **Share to LinkedIn** → Post via chosen mode

## Security Notes

⚠️ **Important**: In production:

- Store credentials in environment variables only
- Use HTTPS for all OAuth callbacks
- Implement proper session management with Redis/Database
- Add CSRF protection
- Encrypt stored tokens

## Troubleshooting

### "Failed to connect LinkedIn"

- Verify redirect URI matches exactly in LinkedIn app settings
- Check client ID and secret are correct
- Ensure required products are enabled

### "Authorization code expired"

- OAuth codes expire quickly (usually 30 seconds)
- Make sure callback is processed immediately

### CORS errors

- Backend CORS is configured for localhost:3000
- For production, update CORS origins
