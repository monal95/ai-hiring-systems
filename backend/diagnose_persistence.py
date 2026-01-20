#!/usr/bin/env python3
"""
Diagnostic script to check interview session persistence
"""

import os
import json
from pathlib import Path

def check_status():
    """Check interview persistence status"""
    
    print("📋 Interview Session Persistence Diagnostic\n")
    print("=" * 50)
    
    # Check sessions file
    sessions_file = Path('data/interview_sessions.json')
    print(f"\n1️⃣  Sessions File: {sessions_file}")
    
    if sessions_file.exists():
        print(f"   ✅ File exists")
        with open(sessions_file, 'r') as f:
            sessions = json.load(f)
        print(f"   📊 Total sessions: {len(sessions)}")
        print(f"   📁 File size: {sessions_file.stat().st_size} bytes")
        
        # List all sessions
        if sessions:
            print(f"\n   Sessions in file:")
            for session_id, session in sessions.items():
                print(f"   - {session_id}: {session.get('candidate_name')} ({session.get('status')})")
    else:
        print(f"   ❌ File not found (will be created when first interview is generated)")
    
    # Check candidates file
    print(f"\n2️⃣  Candidates File: data/candidates.json")
    candidates_file = Path('data/candidates.json')
    if candidates_file.exists():
        with open(candidates_file, 'r') as f:
            candidates_data = json.load(f)
        total_candidates = len(candidates_data.get('candidates', []))
        print(f"   ✅ Found {total_candidates} candidates")
        
        # Show candidates with interview
        print(f"\n   Candidates with interviews:")
        for cand in candidates_data.get('candidates', [])[:3]:
            print(f"   - {cand.get('name')}: Score {cand.get('match_score')}% - Status: {cand.get('status')}")
    
    # Check code changes
    print(f"\n3️⃣  Code Changes Verification")
    interview_system_file = Path('models/interview_system.py')
    if interview_system_file.exists():
        with open(interview_system_file, 'r') as f:
            content = f.read()
        
        checks = {
            'load_sessions method': 'def load_sessions' in content,
            'save_sessions method': 'def save_sessions' in content,
            'sessions_file path': "self.sessions_file = 'data/interview_sessions.json'" in content,
            'save in create_interview_session': 'create_interview_session' in content and 'self.save_sessions()' in content
        }
        
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
    
    print("\n" + "=" * 50)
    print("\n✅ Diagnostic complete!\n")

if __name__ == '__main__':
    check_status()
