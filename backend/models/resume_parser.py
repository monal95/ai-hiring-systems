import spacy
import re
from PyPDF2 import PdfReader
import json

nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    def __init__(self):
        # Common skills database
        self.skills_db = [
            'python', 'java', 'javascript', 'react', 'sql', 'aws', 
            'docker', 'kubernetes', 'machine learning', 'tensorflow',
            'fastapi', 'django', 'nodejs', 'mongodb', 'postgresql'
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF resume"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except:
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
    
    def extract_skills(self, text):
        """Extract skills by matching against skills database"""
        text_lower = text.lower()
        found_skills = []
        for skill in self.skills_db:
            if skill in text_lower:
                found_skills.append(skill)
        return found_skills
    
    def extract_experience(self, text):
        """Extract years of experience (simple pattern matching)"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*:?\s*(\d+)\+?\s*(?:years?|yrs?)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return 0
    
    def parse_resume(self, pdf_path):
        """Main parsing function"""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        doc = nlp(text)
        
        # Extract person name (first PERSON entity found)
        name = None
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
        
        return {
            'name': name,
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'skills': self.extract_skills(text),
            'experience_years': self.extract_experience(text),
            'raw_text': text[:500]  # First 500 chars for preview
        }