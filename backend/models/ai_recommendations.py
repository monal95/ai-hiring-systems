"""
AI Models for candidate scoring, salary recommendations, and interview panel suggestions
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
import random

class CandidateScorer:
    """AI model for scoring and categorizing candidates"""
    
    def __init__(self):
        self.weights = {
            'skill_match': 0.40,
            'experience_match': 0.25,
            'education': 0.15,
            'culture_fit': 0.10,
            'availability': 0.10
        }
    
    def calculate_score(self, candidate_data: Dict, job_requirements: Dict) -> Dict:
        """Calculate candidate score (0-100)"""
        
        scores = {
            'skill_match': self._score_skills(candidate_data, job_requirements),
            'experience_match': self._score_experience(candidate_data, job_requirements),
            'education': self._score_education(candidate_data),
            'culture_fit': self._score_culture(candidate_data),
            'availability': self._score_availability(candidate_data)
        }
        
        # Calculate weighted total
        total_score = sum(
            scores[key] * self.weights[key]
            for key in scores
        )
        
        return {
            'overall_score': round(total_score, 2),
            'breakdown': scores,
            'category': self._categorize_candidate(total_score),
            'hire_probability': round(total_score * 0.95, 2),  # Slightly conservative
            'recommendation': self._get_recommendation(total_score),
            'skill_gaps': self._identify_skill_gaps(candidate_data, job_requirements)
        }
    
    def _score_skills(self, candidate: Dict, job_req: Dict) -> float:
        """Score candidate's skills against JD requirements"""
        candidate_skills = set(s.lower() for s in candidate.get('skills', []))
        required_skills = set(s.lower() for s in job_req.get('must_have', []))
        nice_to_have = set(s.lower() for s in job_req.get('good_to_have', []))
        
        # Calculate matches
        must_have_matches = len(candidate_skills & required_skills)
        nice_to_have_matches = len(candidate_skills & nice_to_have)
        total_required = len(required_skills)
        
        if total_required == 0:
            return 50.0
        
        # Score: 60% for must-have, 40% for nice-to-have
        must_have_score = (must_have_matches / total_required) * 100 * 0.6
        nice_to_have_score = (nice_to_have_matches / len(nice_to_have)) * 100 * 0.4 if nice_to_have else 0
        
        return min(100, must_have_score + nice_to_have_score)
    
    def _score_experience(self, candidate: Dict, job_req: Dict) -> float:
        """Score candidate's experience"""
        try:
            candidate_exp = int(candidate.get('experience_years', 0))
            required_exp = int(job_req.get('experience_required', '0-2').split('-')[0])
            
            if candidate_exp >= required_exp:
                # More experience is good (up to +10 years)
                over_qualification = min(candidate_exp - required_exp, 10)
                return min(100, 70 + (over_qualification * 3))
            else:
                # Less experience - grade down
                gap = required_exp - candidate_exp
                return max(20, 70 - (gap * 10))
        except:
            return 50.0
    
    def _score_education(self, candidate: Dict) -> float:
        """Score candidate's education"""
        education = candidate.get('education', '').lower()
        degree = candidate.get('degree', '').lower()
        
        scores = {
            'phd': 95,
            'masters': 85,
            'bachelor': 75,
            'diploma': 50,
            'certification': 60
        }
        
        for key, score in scores.items():
            if key in education or key in degree:
                return float(score)
        
        return 50.0  # Default if not specified
    
    def _score_culture(self, candidate: Dict) -> float:
        """Score cultural fit"""
        # Use values from application form
        culture_score = candidate.get('culture_fit_score', 50.0)
        return float(culture_score)
    
    def _score_availability(self, candidate: Dict) -> float:
        """Score availability"""
        notice_period = int(candidate.get('notice_period_days', 30))
        
        # Prefer candidates available within 30 days
        if notice_period <= 30:
            return 100.0
        elif notice_period <= 60:
            return 75.0
        else:
            return 50.0
    
    def _categorize_candidate(self, score: float) -> str:
        """Categorize candidate based on score"""
        if score >= 75:
            return 'High Priority'
        elif score >= 50:
            return 'Medium Priority'
        else:
            return 'Low Priority'
    
    def _get_recommendation(self, score: float) -> str:
        """Get hiring recommendation"""
        if score >= 80:
            return 'Strong Hire - Schedule immediately'
        elif score >= 75:
            return 'Hire - Proceed to next round'
        elif score >= 60:
            return 'Consider - Review carefully'
        elif score >= 50:
            return 'Maybe - Needs further evaluation'
        else:
            return 'Pass - Consider for other roles'
    
    def _identify_skill_gaps(self, candidate: Dict, job_req: Dict) -> List[str]:
        """Identify missing critical skills"""
        candidate_skills = set(s.lower() for s in candidate.get('skills', []))
        required_skills = set(s.lower() for s in job_req.get('must_have', []))
        
        gaps = list(required_skills - candidate_skills)
        return gaps[:3]  # Return top 3 gaps


class SalaryRecommender:
    """AI model for salary recommendations based on market data"""
    
    def __init__(self):
        self.market_data = {
            'python developer': (10, 16),
            'senior python developer': (16, 24),
            'backend engineer': (12, 20),
            'frontend developer': (10, 18),
            'full stack developer': (12, 22),
            'data scientist': (14, 22),
            'devops engineer': (15, 25),
            'ml engineer': (16, 28),
            'product manager': (15, 25),
            'engineering manager': (20, 35),
            'sales engineer': (15, 25),
            'business analyst': (8, 14),
        }
    
    def get_salary_recommendation(self, job_title: str, location: str, experience: int) -> Dict:
        """Get salary recommendation"""
        
        # Find matching role
        title_lower = job_title.lower()
        base_range = self._find_role_range(title_lower)
        
        # Adjust for experience
        min_salary, max_salary = base_range
        min_salary = min_salary + (experience - 3) * 0.5  # Add 0.5 LPA per year above 3 years
        max_salary = max_salary + (experience - 3) * 0.8
        
        # Adjust for location
        location_multiplier = self._get_location_multiplier(location)
        min_salary = round(min_salary * location_multiplier, 1)
        max_salary = round(max_salary * location_multiplier, 1)
        
        # Suggested salary (75th percentile)
        suggested = round(min_salary + (max_salary - min_salary) * 0.75, 1)
        
        return {
            'market_range': f"₹{min_salary}-{max_salary} LPA",
            'suggested_salary': f"₹{suggested} LPA",
            'min': min_salary,
            'max': max_salary,
            'suggested': suggested,
            'percentile': '75th',
            'location_adjusted': True,
            'data_source': 'Market Research 2025',
            'confidence': 0.85
        }
    
    def _find_role_range(self, title: str) -> Tuple[float, float]:
        """Find salary range for role"""
        title = title.lower()
        
        for role, salary_range in self.market_data.items():
            if role in title:
                return salary_range
        
        # Default range
        return (10, 20)
    
    def _get_location_multiplier(self, location: str) -> float:
        """Get location salary multiplier"""
        location_multipliers = {
            'bangalore': 1.0,
            'delhi': 1.1,
            'mumbai': 1.15,
            'hyderabad': 0.95,
            'pune': 0.98,
            'gurugram': 1.08,
            'noida': 1.05,
            'remote': 1.0,
            'us': 2.5,
            'uk': 2.0,
            'singapore': 1.8,
            'europe': 1.7
        }
        
        location_lower = location.lower()
        for loc, mult in location_multipliers.items():
            if loc in location_lower:
                return mult
        
        return 1.0


class InterviewPanelRecommender:
    """AI model for suggesting interview panel based on expertise and availability"""
    
    def __init__(self):
        # Mock database of company interviewers
        self.interviewers = [
            {
                'id': 'INT001',
                'name': 'Rajesh Kumar',
                'expertise': ['Python', 'Backend', 'System Design'],
                'availability': ['Monday', 'Tuesday', 'Wednesday'],
                'experience_years': 8
            },
            {
                'id': 'INT002',
                'name': 'Priya Sharma',
                'expertise': ['Frontend', 'React', 'UI/UX'],
                'availability': ['Tuesday', 'Thursday', 'Friday'],
                'experience_years': 6
            },
            {
                'id': 'INT003',
                'name': 'Amit Patel',
                'expertise': ['Data Science', 'Machine Learning', 'Python'],
                'availability': ['Monday', 'Wednesday', 'Friday'],
                'experience_years': 9
            },
            {
                'id': 'INT004',
                'name': 'Sneha Desai',
                'expertise': ['Soft Skills', 'Culture Fit', 'Communication'],
                'availability': ['Monday', 'Tuesday', 'Wednesday', 'Thursday'],
                'experience_years': 5
            },
            {
                'id': 'INT005',
                'name': 'Vikram Singh',
                'expertise': ['DevOps', 'Cloud', 'AWS', 'System Design'],
                'availability': ['Tuesday', 'Thursday', 'Friday'],
                'experience_years': 7
            }
        ]
    
    def recommend_panel(self, job_requirements: Dict) -> Dict:
        """Recommend interview panel based on job requirements"""
        
        required_expertise = job_requirements.get('must_have', [])
        
        # Score each interviewer
        scored_interviewers = []
        for interviewer in self.interviewers:
            score = self._score_interviewer(interviewer, required_expertise)
            if score > 0:
                scored_interviewers.append({
                    **interviewer,
                    'match_score': score
                })
        
        # Sort by score and select top 3
        scored_interviewers.sort(key=lambda x: x['match_score'], reverse=True)
        recommended_panel = scored_interviewers[:3]
        
        # Ensure we have soft skills person
        has_soft_skills = any('Soft Skills' in i.get('expertise', []) for i in recommended_panel)
        if not has_soft_skills and len(recommended_panel) < 3:
            soft_skills_person = next(
                (i for i in self.interviewers if 'Soft Skills' in i.get('expertise', [])),
                None
            )
            if soft_skills_person:
                recommended_panel.append(soft_skills_person)
        
        return {
            'recommended_panel': [
                {
                    'id': p['id'],
                    'name': p['name'],
                    'expertise': p['expertise'],
                    'match_score': round(p.get('match_score', 0), 2),
                    'role': self._assign_interview_role(p),
                    'availability': p['availability']
                }
                for p in recommended_panel[:3]
            ],
            'interview_structure': [
                {'round': 1, 'type': 'Technical', 'duration_minutes': 60, 'interviewer': 'Technical Lead'},
                {'round': 2, 'type': 'System Design', 'duration_minutes': 60, 'interviewer': 'Sr. Engineer'},
                {'round': 3, 'type': 'Cultural Fit', 'duration_minutes': 30, 'interviewer': 'HR Manager'}
            ],
            'total_rounds': 3,
            'total_time_hours': 2.5
        }
    
    def _score_interviewer(self, interviewer: Dict, required_expertise: List[str]) -> float:
        """Score interviewer match"""
        interviewer_expertise = set(e.lower() for e in interviewer.get('expertise', []))
        required = set(e.lower() for e in required_expertise)
        
        matching_skills = len(interviewer_expertise & required)
        total_required = len(required)
        
        if total_required == 0:
            return 50.0
        
        base_score = (matching_skills / total_required) * 100
        experience_bonus = min(interviewer.get('experience_years', 0) * 2, 20)
        
        return min(100, base_score + experience_bonus)
    
    def _assign_interview_role(self, interviewer: Dict) -> str:
        """Assign interview role based on expertise"""
        expertise = interviewer.get('expertise', [])
        
        if 'Soft Skills' in expertise:
            return 'Cultural Fit Round'
        elif 'System Design' in expertise:
            return 'System Design Round'
        else:
            return 'Technical Round'


class AssessmentRecommender:
    """AI model for recommending assessment type based on role"""
    
    def __init__(self):
        self.role_assessments = {
            'python developer': 'coding',
            'backend engineer': 'coding',
            'frontend developer': 'coding',
            'full stack developer': 'coding',
            'data scientist': 'ml_case_study',
            'data analyst': 'sql_excel',
            'product manager': 'case_study',
            'business analyst': 'case_study',
            'devops engineer': 'system_design',
            'ml engineer': 'ml_case_study'
        }
    
    def recommend_assessment(self, job_title: str) -> Dict:
        """Recommend assessment type"""
        title_lower = job_title.lower()
        
        assessment_type = 'coding'
        for role, assessment in self.role_assessments.items():
            if role in title_lower:
                assessment_type = assessment
                break
        
        assessments = {
            'coding': {
                'platform': 'HackerRank',
                'type': 'Coding Test',
                'duration_minutes': 120,
                'skills_tested': ['Problem Solving', 'Coding', 'Algorithms', 'Data Structures'],
                'description': 'Complete coding challenges in your preferred language'
            },
            'ml_case_study': {
                'platform': 'Kaggle',
                'type': 'ML Case Study',
                'duration_minutes': 180,
                'skills_tested': ['Machine Learning', 'Data Analysis', 'Python', 'Statistics'],
                'description': 'Solve a real-world ML problem'
            },
            'sql_excel': {
                'platform': 'DataCamp',
                'type': 'SQL & Excel Test',
                'duration_minutes': 90,
                'skills_tested': ['SQL', 'Excel', 'Data Analysis', 'Query Optimization'],
                'description': 'Analyze data using SQL and Excel'
            },
            'case_study': {
                'platform': 'Custom',
                'type': 'Case Study',
                'duration_minutes': 120,
                'skills_tested': ['Problem Solving', 'Analysis', 'Communication'],
                'description': 'Analyze a business case and present solution'
            },
            'system_design': {
                'platform': 'Custom',
                'type': 'System Design',
                'duration_minutes': 90,
                'skills_tested': ['System Architecture', 'Scalability', 'Design Patterns'],
                'description': 'Design a scalable system'
            }
        }
        
        return {
            'recommended_assessment': assessment_type,
            'details': assessments.get(assessment_type, assessments['coding']),
            'expiry_days': 7,
            'passing_score': 70
        }


# Initialize models
candidate_scorer = CandidateScorer()
salary_recommender = SalaryRecommender()
interview_panel_recommender = InterviewPanelRecommender()
assessment_recommender = AssessmentRecommender()
