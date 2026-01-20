# Interview Email Configuration Guide

## Overview

This document explains how to configure the interview system to send interview invitations with the correct frontend URL, and how to resend interview emails with updated links.

## Configuration

### 1. Set Frontend URL in `.env`

The interview system now uses the `FRONTEND_URL` environment variable to generate interview invitation links. By default, it uses `http://localhost:3000`, but you can change it to any public URL (including dev tunnels).

**Example .env configuration:**

```dotenv
# For local development
FRONTEND_URL=http://localhost:3000

# For dev tunnel
FRONTEND_URL=https://3h16jwxk-3000.inc1.devtunnels.ms

# For production
FRONTEND_URL=https://hiring.yourcompany.com
```

### 2. How Interview Links Are Generated

When an interview session is created, the system automatically generates interview links using the configured `FRONTEND_URL`:

```
{FRONTEND_URL}/interview/{interview_token}
```

Example with dev tunnel:

```
https://3h16jwxk-3000.inc1.devtunnels.ms/interview/b0cc184e-492d-47b3-8aa3-48af40684aea
```

## Using the Resend Interview Email Endpoint

### Endpoint Details

- **Route:** `/api/interview/{interview_token}/resend-email`
- **Method:** `POST`
- **Purpose:** Resend interview invitation email with the current interview link

### Request Example

```bash
curl -X POST http://localhost:3001/api/interview/b0cc184e-492d-47b3-8aa3-48af40684aea/resend-email \
  -H "Content-Type: application/json"
```

### Response Success (200)

```json
{
  "success": true,
  "message": "Interview email resent to candidate@example.com",
  "interview_link": "https://3h16jwxk-3000.inc1.devtunnels.ms/interview/b0cc184e-492d-47b3-8aa3-48af40684aea"
}
```

### Response Error (404/500)

```json
{
  "success": false,
  "error": "Interview session not found",
  "message": "The interview session does not exist"
}
```

## Use Cases

### 1. Candidate Needs Interview Link Again

If a candidate loses or forgets their interview link, you can resend it using the endpoint:

```bash
POST /api/interview/{interview_token}/resend-email
```

The candidate will receive an email with the interview link.

### 2. Updating the Frontend URL

If you change the `FRONTEND_URL` in `.env`:

1. Update the `.env` file with the new URL
2. Restart the backend server
3. Use the resend email endpoint to send updated links to candidates

Example workflow:

```bash
# 1. Change .env (FRONTEND_URL from localhost to dev tunnel)
# 2. Restart backend
# 3. Resend emails with updated links
curl -X POST http://localhost:3001/api/interview/b0cc184e-492d-47b3-8aa3-48af40684aea/resend-email
```

## Current Configuration

The current configuration uses:

```
FRONTEND_URL=https://3h16jwxk-3000.inc1.devtunnels.ms
```

This means all interview links will now point to the dev tunnel URL instead of localhost.

## Troubleshooting

### Interview email not received

1. Check that `SENDGRID_API_KEY` is configured in `.env`
2. Verify that `FROM_EMAIL` is verified in SendGrid
3. Check the backend logs for email sending errors

### Wrong interview link in email

1. Verify `FRONTEND_URL` is set correctly in `.env`
2. Restart the backend after changing `FRONTEND_URL`
3. Use the resend email endpoint to send corrected links

### Interview token not found

1. Ensure the `interview_token` is correct
2. Check that the interview session hasn't expired (7-day default)
3. Verify the session exists in `backend/data/interview_sessions.json`

## System Architecture

The interview system flow:

1. **Interview Session Created** → Generates interview link using `FRONTEND_URL`
2. **Interview Invitation Email Sent** → Contains the interview link
3. **Candidate Clicks Link** → Opens interview at `{FRONTEND_URL}/interview/{token}`
4. **Resend Email** → Uses current `FRONTEND_URL` to send updated link if needed

## Files Modified

- `backend/.env` - Added `FRONTEND_URL` configuration
- `backend/models/interview_system.py` - Updated to use `FRONTEND_URL` from environment
- `backend/app.py` - Added `/api/interview/{interview_token}/resend-email` endpoint
