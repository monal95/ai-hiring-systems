from PyPDF2 import PdfReader
import re
import json
from config.magical_config import parse_resume_with_magical, extract_skills_with_magical


class ResumeParser:
    def __init__(self):
        # Fallback skills database if Magical API is unavailable
        self.skills_db = [
            'python', 'java', 'javascript', 'react', 'sql', 'aws', 
            'docker', 'kubernetes', 'machine learning', 'tensorflow',
            'fastapi', 'django', 'nodejs', 'mongodb', 'postgresql',
            'c++', 'c#', '.net', 'golang', 'rust', 'typescript',
            'angular', 'vue', 'nodejs', 'express', 'spring boot',
            'microservices', 'rest api', 'graphql', 'ci/cd', 'git'
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF resume"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"[ResumeParser] Error reading PDF: {e}")
            return None
    
    def extract_email(self, text):
        """Extract email using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    def extract_phone(self, text):
        """Extract phone number"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else None
    
    def extract_skills_fallback(self, text):
        """Fallback: Extract skills by matching against skills database"""
        text_lower = text.lower()
        found_skills = []
        for skill in self.skills_db:
            if skill in text_lower:
                if skill not in found_skills:
                    found_skills.append(skill)
        return found_skills
    
    def extract_experience(self, text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*:?\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\+?\s*years?',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return 0
    
    def parse_resume(self, pdf_path):
        """
        Main parsing function using Magical AI API
        Falls back to regex/NLP if API is unavailable
        """
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print("[ResumeParser] Failed to extract text from PDF")
            return None
        
        print(f"[ResumeParser] Extracted text length: {len(text)} chars")
        
        # Try Magical API first
        try:
            result = parse_resume_with_magical(text)
            
            if result.get('success'):
                print("[ResumeParser] ✅ Successfully parsed with Magical AI")
                return result
            else:
                print(f"[ResumeParser] Magical API failed: {result.get('error')}")
                print("[ResumeParser] Falling back to regex parsing...")
        except Exception as e:
            print(f"[ResumeParser] Magical API exception: {e}")
            print("[ResumeParser] Falling back to regex parsing...")
        
        # Fallback: Use regex and skills database
        return {
            'name': self._extract_name_fallback(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'skills': self.extract_skills_fallback(text),
            'experience_years': self.extract_experience(text),
            'raw_text': text[:500],
            'fallback': True
        }
    
    def _extract_name_fallback(self, text):
        """
        Fallback method to extract name from text
        Uses simple heuristic: first line with capitalized words
        """
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) < 50:
                words = line.split()
                if all(word[0].isupper() for word in words if len(word) > 0):
                    # Likely a name
                    return line
        return None
