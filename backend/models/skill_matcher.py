class SkillMatcher:
    def __init__(self):
        pass
    
    def calculate_match_score(self, candidate_skills, job_requirements):
        """Calculate percentage match between candidate and job"""
        if not job_requirements or not candidate_skills:
            return 0
        
        # Convert to lowercase for comparison
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in job_requirements.get('must_have', [])]
        
        # Calculate matches
        matches = len(set(candidate_skills_lower) & set(required_skills_lower))
        total_required = len(required_skills_lower)
        
        if total_required == 0:
            return 0
        
        match_percentage = (matches / total_required) * 100
        return round(match_percentage, 2)
    
    def get_missing_skills(self, candidate_skills, job_requirements):
        """Identify skills gap"""
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        required_skills_lower = [s.lower() for s in job_requirements.get('must_have', [])]
        
        missing = set(required_skills_lower) - set(candidate_skills_lower)
        return list(missing)
    
    def categorize_candidate(self, match_score):
        """Categorize based on match score"""
        if match_score >= 75:
            return {"priority": "High", "action": "Interview", "color": "green"}
        elif match_score >= 50:
            return {"priority": "Medium", "action": "Review", "color": "orange"}
        else:
            return {"priority": "Low", "action": "Reject", "color": "red"}